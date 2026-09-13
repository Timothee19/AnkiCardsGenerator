import json
import os
import re
from typing import Dict, List, Tuple

from dotenv import load_dotenv
import json_repair
import genanki
import networkx as nx
from mistralai.client import Mistral
from pydantic import BaseModel, Field
import markdown
import hashlib
import pypandoc

from ocr import traiter_pdf_vers_markdown, semantic_split_with_ai
from scholarDesign import basic_model, twoway_model, cloze_model


# Fichier de logs pour débug chaque étape

log_file = "pipeline_log.txt"

# ==========================================
# 2. PIPELINE DE TRAITEMENT
# ==========================================


class AnkiPipeline:
    def __init__(self, mistral_api_key: str, markdown_file_path, media_files):
        self.client = Mistral(api_key=mistral_api_key)
        self.original_lines = [] # Stockera le texte numéroté pour l'extraction finale
        self.markdown_file_path = markdown_file_path
        self.G = nx.DiGraph()
        self.cost = 0
        self.concept_list = []
        
        self.MODEL_BASIC_ID = 1875392046
        self.model_basic = basic_model
        
        self.MODEL_GENERALITES_ID = 1875392091
        self.model_generalites = twoway_model
        
        self.MODEL_CLOZE_ID = 1875392177
        self.model_cloze = cloze_model

    def markdown_into_chunk(self, markdown_path: str , output_path: str = None):
        
        #Lit un fichier Markdown et génère un nouveau fichier où chaque ligne 
        #est précédée de son numéro de ligne (1-based).
        if not os.path.exists(markdown_path):
            raise FileNotFoundError(f"Le fichier '{markdown_path}' n'existe pas.")

        if output_path is None:
            base, ext = os.path.splitext(markdown_path)
            output_path = f"{base}_numerote{ext}"

        with open(markdown_path, 'r', encoding='utf-8') as f:
            lignes = f.readlines()

        lignes_numerotees = []
        
        for i, ligne in enumerate(lignes, 1):
            ligne_propre = ligne.rstrip('\n')
            lignes_numerotees.append(f"{i}: {ligne_propre}\n")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(lignes_numerotees)

        print(f"✅ Fichier numéroté avec succès : {output_path}")

        self.original_lines = lignes_numerotees

        texte_numerote = "\n".join(lignes_numerotees)

        cost, chunks = semantic_split_with_ai(self.client, texte_numerote)

        self.cost += cost

        return chunks
    
    def exhaustivity_check_into_chunk(self, chunk, parsed_data):
        """
        Lors de chaque appel à Mistral, on vérifie que toutes les lignes du chunk sont couvertes par les intervalles renvoyés.
        """
        included_lines = set()
        print(chunk.strip().splitlines()[0].split(":", 1)[0], end="-> First line\n")
        print(chunk.strip().splitlines()[-1].split(":", 1)[0], end=" -> Last line\n")
        first_line_chunk = int(chunk.strip().splitlines()[0].split(":", 1)[0])
        last_line_chunk = int(chunk.strip().splitlines()[-1].split(":", 1)[0])
        all_lines = set(range(first_line_chunk, last_line_chunk + 1))

        for node_info in parsed_data.get("blocs", []):
            pos = node_info.get("lines")
            included_lines.update(range(pos[0], pos[1] + 1))

        missing_lines_num = sorted(all_lines - included_lines)

        # Store only the missing lines that ccontain actual content (non-empty lines)
        missing_lines = [self.original_lines[line_num - 1].rstrip("\n") for line_num in missing_lines_num if self.original_lines[line_num - 1].split(":", 1)[1].strip()]

        # Logs of all the missing lines, even if they are empty, for debugging purposes
        with open("pipeline_log.txt", "a", encoding="utf-8") as log_f:
            log_f.write(f"\n=== Vérification d'exhaustivité pour le chunk ===\n")
            log_f.write(f"Chunk lines: {first_line_chunk} to {last_line_chunk}\n")
            log_f.write(f"Missing lines: {missing_lines_num}\n")
            for line_num in missing_lines_num:
                raw_content = self.original_lines[line_num - 1].rstrip("\n")
                log_f.write(f"[Ligne {line_num:4d}] : {raw_content}\n")
            log_f.write(f"=== MISSING LINES TELLES QU'ENVOYEES À MISTRAL ===\n")
            for line in missing_lines:
                log_f.write(f"{line}\n")

        if missing_lines:
            return False, missing_lines_num, missing_lines
        return True, [], []
            

    def etape_2_map_analyse_locale(self, chunks: List):
        """
        Envoie un SEUL chunk à Mistral pour extraire le graphe local.
        Effectue également le contrôle d'exhaustivité mathématique sur le retour.
        """
        main_nodes_for_code = []
        main_nodes_for_ai = []
        i = 0
        previous_node = None

        for chunk in chunks :

            with open(log_file, "a", encoding="utf-8") as log_f:
                log_f.write(f"\n=== Analyse locale du chunk {i+1}/{len(chunks)} ===\n")
                log_f.write(f"Chunk content:\n{chunk}\n")
                log_f.write(f"=== FIN DU CHUNK ===\n")

            prompt = rf"""ROLE
You are a structural parser and semantic segmentation agent for academic course notes.
Your task is to parse a markdown text provided with line numbers (format "LineNumber: Text") and structure the content into a flat, event-based conceptual graph.

OBJECTIVE
You will receive a chunk of the full course text. Segment EVERY single line of this chunk into pedagogical building blocks. Each block belongs to a primary concept (Theorem, Proposition, Property, Definition, Lemma, Corollary, Concept) and has a specific pedagogical function (Statement, Proof, Example, Remark, Exercise). Non-pedagogical noise must be filtered out.

STRICT RULES:

## 1. THE FLAT SCHEMA (UNIVERSAL BLOCK)
Every JSON object you generate MUST represent a text block using these 4 exact keys:
- "concept_id": The parent concept's ID. Must strictly match the regex "^(Theorem|Proposition|Property|Definition|Lemma|Corollary|Concept|Ignore)_[0-9]{{2}}$". Use "Concept_XX" for valid pedagogical concepts that don't fit the other specific labels. Use "Ignore_00" for filtered content.
- "concept_name": The explicit name of the concept if stated in the text (e.g., "Monotone Convergence Theorem"). If not applicable (for sub-elements or ignored text), output `null`.
- "element_type": The pedagogical function of this specific text block. MUST be exactly one of: ["Statement", "Proof", "Example", "Remark", "Exercise"].
- "lines": A list of line intervals [[start, end]] for this block. If an image tag appears ("![img-2.jpeg](img-2.jpeg)"), you must keep it in the interval.

## 2. HOW TO ASSIGN A LINE (DECISION TREE)
For every line in the chunk, evaluate its content using this exact order of priority:
- IF the line is an empty line, a table of contents, a structural chapter title without pedagogical content, or general introductory text:
    - Assign it to "concept_id": "Ignore_00" with "element_type": "Statement" and "concept_name": null.
- OTHERWISE, IF the line is a title introducing a list of multiple concepts (e.g., "# List of usual functions"):
    - Assign this title to "Ignore_00". Do NOT group the subsequent list items together. Apply the atomicity rule below to create a distinct node for each concept in the list.
- OTHERWISE, IF the line introduces a new formal concept (Theorem, Definition, Property, etc.) OR any other pedagogical concept that does not fit these standard mathematical labels:
    - Generate a NEW incremented "concept_id" (using the specific label or "Concept_XX" as a fallback) and use "element_type": "Statement". Extract or infer the title into "concept_name".
- OTHERWISE, IF the line is a Proof, Example, Remark, Statement or Exercise related to an existing concept in the graph:
    - Bind it strictly to the "concept_id" of its parent. Set "element_type" to the correct pedagogical function and "concept_name" to `null`. (A Remark, Proof, Exercise or Example NEVER creates a new concept).
- OTHERWISE (Safety Net):
    - EXTEND the `[start, end]` interval of the closest active parent node to absorb the line.

## 3. NON-CONTIGUOUS & DEFERRED ELEMENTS (THE GRAPH MEMORY)
Sub-elements are sometimes deferred (e.g., a Proof appearing 50 lines after its Theorem, or in a new chunk entirely).
MEMORY: Here are the main concepts already extracted in previous chunks:
{main_nodes_for_ai}
If a block in the current text is a Proof, Example, Statement, Exercise or Remark related to one of these past concepts, use its exact "concept_id" from the list above. Do NOT invent a new concept_id.

## 4. EXHAUSTIVE PARTITION (CRITICAL - NO GAPS)
Every single line from the provided chunk MUST belong to exactly one interval in your output.
VERIFY YOUR INTERVALS: If the chunk goes from line 230 to 250, your intervals must seamlessly cover 230 to 250 without any gaps (e.g., [230, 235], [236, 245], [246, 250]). DO NOT drop lines, including empty ones. Empty lines must be absorbed by the preceding concept or assigned to Ignore_00.

EXAMPLES

Input:
12: # Chapter 3: Limits
13: 
14: Here are the main properties to remember for the exam.
15: ## Limit of a sum
16: The limit of a sum is the sum of the limits.
17: *Remark: be careful with indeterminate forms.*
18: 
19: ## Calculation Method (Heuristic)
20: Always isolate the highest degree term.
21: 
22: ## Common limits to know
23: ### Limit of 1/x at infinity
24: The limit of 1/x as x approaches infinity is 0.
25: ### Limit of e^x at negative infinity
26: The limit of e^x as x approaches negative infinity is 0.

Expected Output:
{{
  "blocs": [
    {{
      "concept_id": "Ignore_00",
      "concept_name": null,
      "element_type": "Statement",
      "lines": [[12, 14]]
    }},
    {{
      "concept_id": "Property_01",
      "concept_name": "Limit of a sum",
      "element_type": "Statement",
      "lines": [[15, 16]]
    }},
    {{
      "concept_id": "Property_01",
      "concept_name": null,
      "element_type": "Remark",
      "lines": [[17, 18]]
    }},
    {{
      "concept_id": "Concept_01",
      "concept_name": "Calculation Method (Heuristic)",
      "element_type": "Statement",
      "lines": [[19, 20]]
    }},
    {{
      "concept_id": "Ignore_00",
      "concept_name": null,
      "element_type": "Statement",
      "lines": [[21, 22]]
    }},
    {{
      "concept_id": "Property_02",
      "concept_name": "Limit of 1/x at infinity",
      "element_type": "Statement",
      "lines": [[23, 24]]
    }},
    {{
      "concept_id": "Property_03",
      "concept_name": "Limit of e^x at negative infinity",
      "element_type": "Statement",
      "lines": [[25, 26]]
    }}
  ]
}}

OUTPUT FORMAT
Output MUST be strictly valid JSON matching the schema demonstrated in the example above.
        """
            graph_response_format = {
                                "type": "json_schema",
                                "json_schema": {
                                    "description": "Creation of the graph",
                                    "name": "graph_creation",
                                    "strict": True,
                                    "schema":{
                                        "type": "object",
                                        "required": [
                                            "blocs"
                                        ],
                                        "properties": {
                                            "blocs": {
                                            "type": "array",
                                            "minItems": 1,
                                            "items": {
                                                "type": "object",
                                                "required": [
                                                "concept_id",
                                                "concept_name",
                                                "element_type",
                                                "lines"
                                                ],
                                                "properties": {
                                                "concept_id": {
                                                    "type": "string",
                                                    "pattern": "^(Theorem|Proposition|Property|Definition|Lemma|Corollary|Concept|Ignore)_[0-9]+[a-z]?$"
                                                },
                                                "concept_name": {
                                                    "type": "string",
                                                    "default": "None"
                                                },
                                                "element_type": {
                                                    "type": "string",
                                                    "enum": [
                                                    "Statement",
                                                    "Proof",
                                                    "Example",
                                                    "Remark",
                                                    "Exercise"
                                                    ]
                                                },
                                                "lines": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "integer"
                                                    },
                                                    "minItems": 2,
                                                    "maxItems": 2
                                                    }
                                                },
                                            "additionalProperties": False
                                                }
                                            }
                                        }
                                    },
                                    "additionalProperties": False
                                }
                            }
            response = self.client.chat.complete(
                        model="mistral-large-latest",
                        messages=[{
                            "role": "system",
                            "content": prompt
                        },
                        {
                            "role": "user",
                            "content": chunk
                        }],
                        temperature=0.0,
                        response_format=graph_response_format
                    )
                    
            json_string = response.choices[0].message.content
            details = getattr(response.usage, "prompt_tokens_details", None)
            cached_tokens = getattr(details, "cached_tokens", 0) or 0

            self.cost += (
                (response.usage.prompt_tokens - cached_tokens) / 1e6 * 0.44
                    + response.usage.completion_tokens / 1e6 * 1.3
                    + cached_tokens / 1e6 * 0.044
            )         
            parsed_data = json.loads(json_string)
            parsed_data_correction = None

            with open(log_file, "a", encoding="utf-8") as log_f:
                log_f.write(f"\n=== Résultat de Mistral pour le chunk {i+1}/{len(chunks)} ===\n")
                log_f.write(f"{parsed_data}\n")
                log_f.write(f"=== FIN DU CHUNK ===\n")

            exhaustive_parsing,  missing_lines_num, missing_lines = self.exhaustivity_check_into_chunk(chunk, parsed_data)
            while exhaustive_parsing == False:
                print(f"⚠️ Retranscription incomplète pour ce chunk : {len(missing_lines)} ligne(s) non retranscrite(s) : {missing_lines_num}")
                print(f"❌ Lignes manquantes : {missing_lines}")

                # On demande à Mistral de corriger son output pour couvrir les lignes manquantes
                correction_prompt = r"""
                ROLE
You are a precise conceptual graph correction agent. Your colleague has parsed a markdown course text into a JSON graph but missed specific line intervals. 
Your ONLY task is to analyze these missing lines and generate the missing JSON blocks to repair the graph.

OBJECTIVE
Read the source text and the already extracted JSON graph. 
Then, for each interval in the MISSING LINES list, create one or multiple JSON blocks to integrate this orphaned text.

STRICT RULES FOR RESOLUTION:

## 1. THE FLAT SCHEMA
Every JSON object you generate MUST strictly match this schema:
- "concept_id": Must match "^(Theorem|Proposition|Property|Definition|Lemma|Corollary|Concept|Ignore)_[0-9]{2}$".
- "concept_name": The title of the concept, or `null` for sub-elements/ignored text.
- "element_type": One of ["Statement", "Proof", "Example", "Remark", "Exercise"].
- "lines": The line intervals [[start, end]].

## 2. HOW TO RESOLVE A MISSING LINE (DECISION TREE)
Analyze the missing text and apply this priority:
- IF the missing lines are empty lines, introductory text, transitions, or isolated titles without pedagogical properties:
    - Assign them to "concept_id": "Ignore_00" with "element_type": "Statement" and "concept_name": null.
- OTHERWISE, IF the missing lines represent a Proof, Example, Remark, or Exercise that logically belongs to a concept ALREADY PRESENT in the EXISTING JSON:
    - You MUST reuse the exact same "concept_id" from the existing JSON. Set "element_type" accordingly and "concept_name" to `null`.
- OTHERWISE, IF the missing lines contain a completely new Concept (Theorem, Definition, etc., or general Concept_XX) that was ignored:
    - Create a NEW incremented "concept_id" (e.g., if "Theorem_01" exists, create "Theorem_02").

## 3. CONSTRAINTS
- NO REPETITION: Do NOT output blocks that are already in the EXISTING JSON. ONLY output blocks covering the missing lines.
- EXHAUSTIVITY: The "lines" intervals in your output MUST perfectly and entirely cover all the numbers listed in MISSING LINES.

EXAMPLES

<source_text>
15: ## Limit of a sum
16: The limit of a sum is the sum of the limits.
17: *Remark: be careful with indeterminate forms.*
18: 
19: ## Calculation Method
</source_text>

<existing_json>
{
  "blocs": [
    {
      "concept_id": "Property_01",
      "concept_name": "Limit of a sum",
      "element_type": "Statement",
      "lines": [[15, 16]]
    }
  ]
}
</existing_json>

<missing_lines>
[17, 17], [18, 19]
</missing_lines>

Expected Output:
{
  "blocs": [
    {
      "concept_id": "Property_01",
      "concept_name": null,
      "element_type": "Remark",
      "lines": [[17, 17]]
    },
    {
      "concept_id": "Ignore_00",
      "concept_name": null,
      "element_type": "Statement",
      "lines": [[18, 19]]
    }
  ]
}
"""
                response_correction = self.client.chat.complete(
                                    model="mistral-large-latest",
                                    messages=[{
                                        "role": "system",
                                        "content": correction_prompt
                                    },
                                    {
                                        "role": "user",
                                        "content": rf"""
                                        INPUT DATA:

                                        <source_text>
                                        {chunk}
                                        </source_text>

                                        <existing_json>
                                        {parsed_data}
                                        </existing_json>

                                        <missing_lines>
                                        The following line intervals were missed and must be integrated:
                                        {missing_lines_num}
                                        </missing_lines>
                                        """
                                    }],
                                    temperature=0.0,
                                    response_format=graph_response_format
                                )
                # Evaluation du coup
                details = getattr(response.usage, "prompt_tokens_details", None)
                cached_tokens = getattr(details, "cached_tokens", 0) or 0

                self.cost += (
                    (response.usage.prompt_tokens - cached_tokens) / 1e6 * 0.44
                    + response.usage.completion_tokens / 1e6 * 1.3
                    + cached_tokens / 1e6 * 0.044
                )                

                json_string = response_correction.choices[0].message.content
                parsed_data_correction = json.loads(json_string)

                with open(log_file, "a", encoding="utf-8") as log_f:
                    log_f.write(f"\n=== Résultat de Mistral pour la correction du chunk {i+1}/{len(chunks)} ===\n")
                    log_f.write(f"{parsed_data_correction}\n")
                    log_f.write(f"=== FIN DU CHUNK ===\n")

                parsed_data["blocs"].extend(parsed_data_correction.get("blocs", []))
                exhaustive_parsing,  missing_lines_num, missing_lines = self.exhaustivity_check_into_chunk(chunk, parsed_data)
                
            # Sort data depending on the starting line of each block to maintain order
            parsed_data["blocs"].sort(key=lambda x: x["lines"][0])

            if parsed_data_correction is not None:
                with open(log_file, "a", encoding="utf-8") as log_f:
                    log_f.write(f"\n=== Résultat final après correction du chunk {i+1}/{len(chunks)} ===\n")
                    log_f.write(f"{parsed_data}\n")
                    log_f.write(f"=== FIN DU CHUNK ===\n")
            parsed_data_correction = None  # Reset for the next chunk

            for node_info in parsed_data.get("blocs", []):

                main_node_id = node_info.get("concept_id")
                name = node_info.get("concept_name")
                elementType = node_info.get("element_type")
                pos = node_info.get("lines")
                node_name = main_node_id + " : " + name if name and name != "None" else main_node_id
                sub_node_id = f"{main_node_id}_{elementType}_{pos[0]}_{pos[1]}"


                if main_node_id not in main_nodes_for_code :

                    main_nodes_for_code.append(main_node_id)
                    main_nodes_for_ai.append(node_name)
                    extracted_text = ""
                    extracted_text += "".join(self.original_lines[pos[0]-1:pos[1]]) + "\n"
                    self.G.add_node(main_node_id, label=node_name, text = extracted_text)
                    self.G.add_node(
                        sub_node_id,
                        label=elementType,
                        text = extracted_text,
                        pos=pos,
                        is_main=False
                    )
                    self.G.add_edge(main_node_id, sub_node_id, link="link")
                    if i >= 1:
                        self.G.add_edge(previous_node, main_node_id, label=i-1, link="next_topic")
                    
                    previous_node = main_node_id
                    
                    i += 1

                else:

                    extracted_text = ""
                    extracted_text += "".join(self.original_lines[pos[0]-1:pos[1]]) + "\n"
                    self.G.add_node(
                        sub_node_id,
                        label=elementType,
                        text = extracted_text,
                        pos=pos,
                        is_main=False
                    )
                    self.G.add_edge(main_node_id, sub_node_id, link="link")
        return self.G

    def extraire_blocs_pour_anki(self):
        """
        Prend tous les résultats locaux et construit le graphe NetworkX global.
        C'est ici qu'on remplace les numéros de lignes par le texte réel.
        """
        
        markdown_lines = self.original_lines

        total_lines_count = len(markdown_lines)
        all_lines = set(range(1, total_lines_count+1))
        covered_lines = set()
        
        line_number_regex = re.compile(r"^\s*\d+[\s\|\:\.\-\)]\s*")
        
        start_node = None
        for node in self.G.nodes():
            in_links = [data.get("link") for _, _, data in self.G.in_edges(node, data=True)]
            if "next_topic" not in in_links and any(data.get("link") == "next_topic" for _, _, data in self.G.out_edges(node, data=True)):
                start_node = node
                break

        if start_node is None and len(self.G) > 0:
            start_node = next(iter(self.G.nodes()))

        current_main = start_node

        while current_main is not None:
            main_data = {
                "main_id": current_main,
                "label": self.G.nodes[current_main].get("label", current_main),
                "sub_nodes": []
            }

            next_main = None

            for _, neighbor, edge_data in self.G.out_edges(current_main, data=True):
                if edge_data.get("link") == "link":
                    pos = self.G.nodes[neighbor].get("pos")
                    extracted_text_from_graph = self.G.nodes[neighbor].get("text")
                    with open(log_file, "a", encoding="utf-8") as log_f:
                        log_f.write(f"\n=== Extraction du texte pour le sous-noeud {neighbor} ===\n")
                        log_f.write(f"Label du sous-noeud : {self.G.nodes[neighbor].get('label')}\n")
                        log_f.write(f"Position dans le markdown : {pos}\n")
                        log_f.write(f"Texte extrait du graphe :\n{extracted_text_from_graph}\n")
                        log_f.write(f"=== FIN DE L'EXTRACTION ===\n")

                    if pos and len(pos) == 2:
                        start_line, end_line = pos[0], pos[1]
                        covered_lines.update(range(start_line, end_line))
                        
                        idx_start = max(0, start_line - 1)
                        idx_end = min(len(markdown_lines), end_line)

                        # --- SMART EXPAND ---
                        
                        while idx_end < len(markdown_lines):
                            next_line_clean = line_number_regex.sub("", markdown_lines[idx_end]).strip()
                            # On absorbe les lignes vides, les fermetures LaTeX et les sauts de lignes matriciels
                            if (next_line_clean == "" or 
                                next_line_clean in ["\\]", "$$", "]", "\\)", "}"] or 
                                next_line_clean.startswith("\\end{") or 
                                next_line_clean.endswith("\\\\")):
                                idx_end += 1
                            else:
                                break
                                
                        covered_lines.update(range(start_line, idx_end+1))
                        
                        raw_slice = markdown_lines[idx_start:idx_end]
                        cleaned_lines = [line_number_regex.sub("", line) for line in raw_slice]
                        extracted_text = "".join(cleaned_lines).strip()
                    
                    main_data["sub_nodes"].append({
                        "sub_id": neighbor,
                        "type": self.G.nodes[neighbor].get("label"),
                        "text": extracted_text
                    })

                    with open(log_file, "a", encoding="utf-8") as log_f:
                        log_f.write(f"\n=== Détails du sous-noeud {neighbor}, après smart expand ===\n")
                        log_f.write(f"Type : {self.G.nodes[neighbor].get('label')}\n")
                        log_f.write(f"Texte extrait après smart expand :\n{extracted_text}\n")
                        log_f.write(f"=== FIN DU SOUS-NOEUD ===\n")

                elif edge_data.get("link") == "next_topic":
                    next_main = neighbor

            self.concept_list.append(main_data)
            current_main = next_main

        # 4. Vérification de la complétude (Désindentée pour s'exécuter 1 seule fois !)
        missing_lines = sorted(all_lines - (covered_lines))
            
        print("\n" + "=" * 50)
        if not missing_lines:
            print("✅ Intégralité respectée : 100% du Markdown a été retranscrit !")
        else:
            taux = ((total_lines_count - len(missing_lines)) / total_lines_count) * 100
            print(f"⚠️ Retranscription incomplète : {taux:.1f}% des lignes couvertes.")
            print(f"❌ {len(missing_lines)} ligne(s) non retranscrite(s) :\n")
            
            report_file = "lignes_manquantes_rapport.txt"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(f"=== RAPPORT DES {len(missing_lines)} LIGNES MANQUANTES ===\n\n")
                for line_num in missing_lines:
                    raw_content = markdown_lines[line_num - 1].rstrip("\n")
                    f.write(f"[Ligne {line_num:4d}] : {raw_content}\n")
            
            print(f"📁 Le détail complet a été sauvegardé dans le fichier : {report_file}")
            
            print("\n🔍 Aperçu des 10 premières lignes manquantes :")
            for line_num in missing_lines[:10]:
                raw_content = markdown_lines[line_num - 1].rstrip("\n")
                print(f"   [Ligne {line_num:4d}] : {raw_content}")
                
        print("=" * 50 + "\n")

        return self.concept_list

    
    def generer_id_deterministe(self,chaine_texte):
            # 1. Préparation : conversion de la chaîne en séquence d'octets
            octets = chaine_texte.encode('utf-8')
            
            # 2. Hachage : création de l'objet hash avec l'algorithme SHA-256
            hash_obj = hashlib.sha256(octets)
            
            # 3. Récupération de l'empreinte sous forme de chaîne hexadécimale
            empreinte_hexa = hash_obj.hexdigest()
            
            # 4. Troncature : on garde les 8 premiers caractères 
            # (cela génère un nombre en base 16 qui tiendra largement sur 32 bits)
            empreinte_courte = empreinte_hexa[:8]
            
            # 5. Conversion finale : de la chaîne hexadécimale (base 16) vers un entier (base 10)
            id_final = int(empreinte_courte, 16)
            
            return id_final
    
    def course_into_flashcards(self, front, back):
        """
        Appel à Mistral Small pour simplifier et transformer le contenu des cartes en flashcards.
        """
        prompt = r"""You are an expert in mathematics pedagogy and Spaced Repetition Systems (Anki). Your task is to take dense mathematical flashcard content and reformat it to be highly memorizable, visually light, and structured without losing any information.

OBJECTIVE
Reformat the provided raw content into a clean JSON structure. The `back` field must be a SINGLE STRING formatted in 100% MARKDOWN (no HTML whatsoever) with MathJax/LaTeX equations, strictly following the rules below.

STRICT RULES:

0. FORMAT REQUIREMENT — MARKDOWN ONLY:
   - The ENTIRE output (front and back) must be valid Markdown. HTML tags are STRICTLY FORBIDDEN (no <ul>, <li>, <b>, <div>, <span>, <br>, etc.).
   - Bullet points MUST use Markdown syntax: newlines starting with "- " (dash + space), with sub-bullets indented by 2 spaces.
   - Bold text MUST use Markdown syntax: **text** (never <b>text</b>).
   - Sub-headings MUST use Markdown syntax: **Heading:** on its own line, or "#### Heading" if a true heading level is needed.
   - Numbered steps (e.g., in proof sketches) MUST use Markdown ordered lists: "1. ", "2. ", "3. " (never manual "1)" strings mixed with HTML).
   - Line breaks between blocks must be done with blank lines (Markdown paragraph breaks), never with <br>.
   - If any HTML tag appears anywhere in your output, the output is INVALID and must be corrected before returning.

1. THEOREM / DEFINITION / PROPERTY (The Core Statement):
   - Preserve ALL mathematical information, rigor, and hypotheses.
   - Visually space it out: Use Markdown bullet lists ("- ") to list hypotheses, conditions, or consequences instead of dense paragraphs.
   - Highlight key terms using Markdown bold (**text**).

2. PROOFS (Sketch of proof):
   - NEVER copy the full proof verbatim.
   - Replace the original proof with a section titled "**Sketch of proof:**" or "**Idea of the proof:**" (Markdown bold, not HTML bold).
   - Summarize the proof's architecture into 2 or 3 essential anchor points using a Markdown ordered list (e.g., "1. Initialize with X", "2. Use Y inequality", "3. Conclude by taking the limit"). Get straight to the point.

3. MATHEMATICAL FORMATTING:
   - Delimit ALL math:
     * Inline math MUST be enclosed in $...$ (e.g. $f_n \to f$, $\mathcal{A}$-measurable).
     * Display / block equations MUST be enclosed in $$...$$.
   - CRITICAL - Set notation :
     * LaTeX set braces \{ and \} are NOT delimiters! You MUST wrap whole set equations in dollars:
       BAD:  - \{\sup f_n < a\} = \bigcap \{f_n < a\}
       GOOD: - $\{\sup f_n < a\} = \bigcap \{f_n < a\}$
     * Never write naked LaTeX commands like \mathcal{A} attached to words; write $\mathcal{A}$-measurable.
   - CRITICAL - LIST AND NEWLINES IN JSON:
     - Do NOT use \begin{itemize} or \item, and do NOT use HTML tags for lists. Use Markdown dash-lists ("- ") exclusively.
     - You MUST insert a literal "\n\n" before before the VERY FIRST bullet point of a list to force a line break. And you MUST insert a single "\n" between consecutive bullet points :
       BAD: "List to write: - A point of the list - Another point of the list"
       GOOD: "Geometric Interpretation:\n\n- A point of the list\n- Another point of the list"

4. JSON CONSTRAINTS:
   - Every LaTeX backslash MUST be escaped for JSON validation (e.g., write \\frac and \\alpha, never \frac or \alpha).
   - Output MUST be a flat JSON object: {"front": "...", "back": "..."}.
   - The "back" field must be a single string containing valid Markdown + math only (no HTML).
   - Since the string is Markdown, escape internal double quotes as needed for valid JSON, but do NOT introduce HTML attributes or tags to work around quoting — restructure in Markdown instead.
   - Newlines inside the "back" string must be represented as literal "\n" characters so that, once unescaped, the text renders as proper Markdown (blank lines between paragraphs/lists as needed).

5. NO DELETION OF SECONDARY FACTS:
   - You are strictly forbidden from deleting secondary definitions, remarks, or historical names present in the raw text.
   - Never delete any image tag (e.g., ![img-2.jpeg](img-2.jpeg)) — Markdown image syntax is the one exception to the "no tags" rule and must appear exactly as in the original text.
   - If multiple concepts are present, use clear Markdown bold sub-headings (**Concept Name:**) to include ALL of them on the back of the card without dropping information.

6. STRICT ANTI-HALLUCINATION (EMPTY CARDS):
   - You are a formatter, NOT a content generator. You MUST NEVER invent, deduce, or retrieve external knowledge to fill a card.
   - If the Back input lacks actual pedagogical content (e.g., it is entirely empty, or consists strictly of a title/header with no body text), you MUST return empty strings.
     BAD: The Back input is only "### Properties" -> You use your own knowledge to list mathematical properties.
     GOOD: The Back input is only "### Properties" -> You output {"front": "", "back": ""}.
INPUT FORMAT:
[Front] The title of the card.
[Back] The raw text including the statement, proof, and examples.

OUTPUT FORMAT:
{
    "front": "The title or question (cleaned up if necessary, double-escaping LaTeX), in plain text or Markdown.",
     "back": "The newly formatted content combining the spaced-out statement, the sketch of proof, and the examples — written entirely in Markdown (no HTML), all inside ONE single string, double-escaping LaTeX and using \\n for line breaks."
}"""
        response = self.client.chat.complete(
                    model="mistral-small-latest",
                    messages=[{
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"Front: {front}\nBack: {back}"
                    }],
                    temperature=0.0,
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "description": "Creation of the flashcard",
                            "name": "graph_creation",
                            "strict": True,
                            "schema":{
                                "type": "object",
                                "title": "Minimal Spaced Repetition Flashcard Schema",
                                "required": [
                                    "front",
                                    "back"
                                ],
                                "properties": {
                                    "back": {
                                    "type": "string",
                                    "description": "The formatted answer, including core statement, proof sketch, and examples (if any)."
                                    },
                                    "front": {
                                    "type": "string",
                                    "minLength": 1,
                                    "description": "The title or question of the flashcard."
                                    }
                                },
                                "description": "A stripped-down schema for flashcards with only front and back fields.",
                                "additionalProperties": False
                                }
                            }
                        }
                    )

        details = getattr(response.usage, "prompt_tokens_details", None)
        cached_tokens = getattr(details, "cached_tokens", 0) or 0

        self.cost += (
            (response.usage.prompt_tokens - cached_tokens) / 1e6 * 0.12
            + response.usage.completion_tokens / 1e6 * 0.5
            + cached_tokens / 1e6 * 0.012
        )
        json_string = response.choices[0].message.content
        parsed_data = json_repair.loads(json_string)

        return parsed_data.get("front", ""), parsed_data.get("back", "")
# ==========================================
# 3. EXÉCUTION PRINCIPALE
# ==========================================


def main():

    load_dotenv()
    API_KEY = os.environ.get("MISTRAL_API_KEY")
    if not API_KEY:
        print("Erreur: Clé API manquante.")
        return
    deck_name = input("Entrez le nom du paquet Anki à générer (ex: AI_Algo_1) : ")
    markdown_file, media_files, cost = traiter_pdf_vers_markdown()
    print("Coût de l'OCR : ", cost, end="\n")
    pipeline = AnkiPipeline(API_KEY, markdown_file, media_files)
    
    print("1. Découpage du document...")
    chunks = pipeline.markdown_into_chunk(markdown_file)
    
    print(f"2. Analyse locale de {len(chunks)} chunks via LLM...")
    graph = pipeline.etape_2_map_analyse_locale(chunks)

    #Affichage et enregistrement du graphe avec graphviz
    A = nx.nx_agraph.to_agraph(graph)
    A.draw(f'{deck_name.replace("::", "_")}.png', prog='dot')

    print("3. Création de la liste de cartes pour Anki")
    concept_list = pipeline.extraire_blocs_pour_anki()

    print("Création du paquet Anki")
    my_deck = genanki.Deck(pipeline.generer_id_deterministe(deck_name), deck_name)
    concept_deck = genanki.Deck(pipeline.generer_id_deterministe(f'{deck_name}::Concepts'), f'{deck_name}::Concepts')
    theorem_deck = genanki.Deck(pipeline.generer_id_deterministe(f'{deck_name}::Theorems'), f'{deck_name}::Theorems')
    property_deck = genanki.Deck(pipeline.generer_id_deterministe(f'{deck_name}::Properties'), f'{deck_name}::Properties')
    lemma_deck = genanki.Deck(pipeline.generer_id_deterministe(f'{deck_name}::Lemma'), f'{deck_name}::Lemma')
    definition_deck = genanki.Deck(pipeline.generer_id_deterministe(f'{deck_name}::Definitions'), f'{deck_name}::Definitions')
    corollary_deck = genanki.Deck(pipeline.generer_id_deterministe(f'{deck_name}::Corollary'), f'{deck_name}::Corollary')

    deck_dict = {"Theorem":theorem_deck, "Proposition": property_deck,"Property": property_deck,"Definition" : definition_deck,
                 "Lemma": lemma_deck,"Corollary": corollary_deck, "Concept": concept_deck}

    j=0
    for card in concept_list:
        enonce = []
        proof = []
        remark = []
        example = []
        exercice = []
        
        front = card["label"]
        back = ""
        
        for i in range(len(card["sub_nodes"])):
            sub_type = card["sub_nodes"][i]["type"]
            html_text = card["sub_nodes"][i]["text"]
            
            if sub_type == "Statement":
                enonce.append(html_text)
            elif sub_type == "Proof":
                proof.append(html_text)
            elif sub_type == "Remark":
                remark.append(html_text)
            elif sub_type == "Example":
                example.append(html_text)
            elif sub_type == "Exercise":
                exercice.append(html_text)
                
        # Construction propre et sécurisée du dos de la carte
        if enonce:
            back += enonce[0] + "<br><br>"
        if proof:
            back += "<strong>Proof :</strong><br>" + proof[0] + "<br><br>"

        length_example = 0
        length_remark = 0
        length_exercice = 0
        if example:
            length_example = len(example[0])
        if remark:
            length_remark = len(remark[0])
        if exercice:
            length_exercice = len(exercice[0])
        if len(back) + length_example + length_remark + length_exercice < 50:
            print("This card has a very short back content, skipping it to avoid empty cards.\n Front: {}\nBack: {}".format(front, back))
        else:
            front, back = pipeline.course_into_flashcards(front, back)
            # Add examples, remarks and exercises in collapsible sections

            # 2. LA RUSTINE : On "aspire" les espaces aux bords et on force un double dollar propre
            back = re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', back, flags=re.DOTALL)
            front = re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', front, flags=re.DOTALL)
            # 3. CONVERSION MARKDOWN -> HTML (avec MathJax)
            front = pypandoc.convert_text(front, "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"])
            back = pypandoc.convert_text(back, "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"])

            if example:
                back += f"<details><summary>Examples (click to expand)</summary>" + "\n".join([pypandoc.convert_text(re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', example[i], flags=re.DOTALL), "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"]) for i in range(len(example))]) + "</details><br>"

            if remark:
                back += f"<details><summary>Remarks (click to expand)</summary>" + "\n".join([pypandoc.convert_text(re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', remark[i], flags=re.DOTALL), "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"]) for i in range(len(remark))]) + "</details><br>"
            if exercice:
                back += f"<details><summary>Exercise {i + 1} (click to expand)</summary>" + "\n".join([pypandoc.convert_text(re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', exercice[i], flags=re.DOTALL), "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"]) for i in range(len(exercice))]) + "</details><br>"

            # Skip the card if the content is empty
            if len(back) > 30:
                my_note = genanki.Note(
                    model=pipeline.model_basic,
                    fields=[front, back, str(j)])
                j += 1
                deck_dict[card["main_id"].split("_")[0]].add_note(my_note)
            else:
                print("carte skip: ", back, end="\n")

    my_package = genanki.Package([my_deck] + list(set(deck_dict.values())))
    my_package.media_files = media_files 
    my_package.write_to_file(f'{deck_name.replace("::","_")}.apkg')
    print("✅ Génération du paquet Anki terminée !")
    print(f"💰 Coût total estimé pour l'utilisation de Mistral : {pipeline.cost+cost:.4f} €")
    print("Terminé !")

if __name__ == "__main__":
    main()