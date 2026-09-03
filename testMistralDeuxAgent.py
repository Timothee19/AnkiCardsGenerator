import json
import os
import re
from typing import Dict, List, Tuple

import json_repair
import genanki
import networkx as nx
from mistralai.client import Mistral
from pydantic import BaseModel, Field
import markdown
import hashlib

from AnkiGeneratorRobustV1_3 import semantic_split_with_ai
from ocr import traiter_pdf_vers_markdown

# ==========================================
# 1. SCHÉMAS PYDANTIC (Pour contraindre Mistral)
# ==========================================

class Element(BaseModel):
    type: str = Field(description="Strictement parmi: 'Enoncé', 'Démonstration', 'Exemple', 'Remarque', 'Exercice'")
    startEndListPositions: List[Tuple[int, int]] = Field(
        description="Liste d'intervalles de lignes [début, fin]. Ex: [[10, 15], [20, 25]]"
    )

class Concept(BaseModel):
    main: str = Field(description="Ex: 'Théorème_01', 'Définition_01', 'Contexte_01'")
    name: str = Field(description="Nom du concept (ex: 'Théorème de Pythagore') ou 'None'")
    elements: List[Element] = Field(description="Les sous-éléments rattachés à ce concept dans ce chunk")

class ChunkResult(BaseModel):
    concepts: List[Concept]

# ==========================================
# 2. PIPELINE DE TRAITEMENT
# ==========================================


class AnkiPipeline:
    def __init__(self, mistral_api_key: str, markdown_file_path, media_files):
        self.client = Mistral(api_key=mistral_api_key)
        self.original_lines = [] # Stockera le texte numéroté pour l'extraction finale
        self.markdown_file_path = markdown_file_path
        self.G = nx.DiGraph()
        self.concept_list = []
        self.CSS = r"""
        :root{
        --bg:#faf6ef;
        --card-bg:#fffbf3;
        --dot:rgba(79,125,92,.22);
        --ink:#2e2a24;
        --ink-soft:#7a7266;
        --accent:#4f7d5c;
        --accent-light:#71a481;
        --accent-dark:#3c6047;
        --accent-soft:rgba(79,125,92,.14);
        --accent2:#c1694f;
        --accent2-light:#d78a6c;
        --accent2-dark:#9f4f39;
        --accent2-soft:rgba(193,105,79,.14);
        --line:#e6ddcf;
        --code-bg:#efe7d8;
        --code-ink:#4a4235;
        --code-dark-bg:#2e2a24;
        --code-dark-bg2:#3c3527;
        --code-dark-ink:#f4ede0;
        }
        
        html, body{
        margin:0;
        background-color:var(--bg);
        background-image:radial-gradient(circle, var(--dot) 1.5px, transparent 1.5px);
        background-size:22px 22px;
        }
        
        .card{
        font-family:"Source Sans 3","Segoe UI",-apple-system,BlinkMacSystemFont,Arial,sans-serif;
        font-size:20px;
        line-height:1.65;
        color:var(--ink);
        text-align:justify;
        max-width:640px;
        margin:0 auto;
        padding:32px 36px;
        background:linear-gradient(165deg, #ffffff 0%, var(--card-bg) 100%);
        border-radius:0 0 22px 22px;
        box-shadow:0 1px 2px rgba(46,42,36,.16), 0 4px 10px rgba(46,42,36,.18), inset 0 1px 0 rgba(255,255,255,.9);
        }
        
        /* separateur Question / Reponse : barre droite + bulle en relief */
        .divider{
        display:flex;
        align-items:center;
        gap:14px;
        margin:26px 0 22px;
        }
        .divider::before, .divider::after{
        content:"";
        flex:1;
        height:1px;
        background:var(--line);
        }
        .divider span{
        font-size:12px;
        font-weight:700;
        letter-spacing:.06em;
        text-transform:uppercase;
        color:var(--accent-dark);
        background:linear-gradient(160deg, rgba(79,125,92,.07) 0%, rgba(79,125,92,.17) 100%);
        padding:4px 12px;
        border-radius:999px;
        box-shadow:0 1px 2px rgba(79,125,92,.22), 0 2px 6px rgba(79,125,92,.22), inset 0 1px 0 rgba(255,255,255,.9), inset 0 -1px 2px rgba(60,96,71,.10);
        white-space:nowrap;
        }
        
        /* cloze : relief marque, forme V1 conservee */
        .cloze{
        font-weight:600;
        color:var(--accent2-dark);
        background:linear-gradient(160deg, rgba(193,105,79,.07) 0%, rgba(193,105,79,.17) 100%);
        padding:1px 7px;
        border-radius:5px;
        box-shadow:0 1px 2px rgba(193,105,79,.18), 0 2px 5px rgba(193,105,79,.18), inset 0 1px 0 rgba(255,255,255,.9);
        }
        
        /* images */
        img{
        max-width:100%;
        height:auto;
        display:block;
        margin:16px auto;
        border-radius:26px 8px 26px 8px;
        box-shadow:0 2px 4px rgba(46,42,36,.16), 0 6px 14px rgba(46,42,36,.18);
        }
        
        /* code */
        code{
        font-family:"JetBrains Mono","Fira Code",Consolas,monospace;
        font-size:.85em;
        background:linear-gradient(160deg, #ffffff 0%, var(--code-bg) 100%);
        color:var(--code-ink);
        padding:2px 7px;
        border-radius:8px 3px 8px 3px;
        box-shadow:0 1px 2px rgba(46,42,36,.12), inset 0 1px 0 rgba(255,255,255,.8);
        }
        pre{
        font-family:"JetBrains Mono","Fira Code",Consolas,monospace;
        background:linear-gradient(160deg, var(--code-dark-bg2) 0%, var(--code-dark-bg) 100%);
        color:var(--code-dark-ink);
        padding:16px 18px;
        border-radius:20px 6px 20px 6px;
        overflow-x:auto;
        line-height:1.55;
        font-size:.85em;
        box-shadow:0 1px 3px rgba(0,0,0,.24), 0 4px 10px rgba(0,0,0,.24), inset 0 1px 0 rgba(255,255,255,.08);
        }
        pre code{ background:none; padding:0; color:inherit; box-shadow:none; }
        
        /* equations LaTeX trop larges (cases, matrices...) : defilement horizontal plutot que debordement */
        /* Anki Desktop moderne rend le LaTeX dans <anki-mathjax>, un web component a Shadow DOM :
        on ne peut pas cibler son contenu interne (mjx-container/svg) depuis le CSS de la carte,
        seul l'element hote lui-meme est accessible depuis l'exterieur. */
        .card anki-mathjax{
        max-width:100%;
        overflow-x:auto;
        overflow-y:hidden;
        }
        .card anki-mathjax[block="true"]{
        display:block;
        margin:14px 0;
        padding-bottom:2px; /* evite que la scrollbar colle au texte */
        }
        /* secours : rendus sans Shadow DOM (anciennes versions, autres plateformes) */
        .card mjx-container{
        max-width:100%;
        overflow-x:auto;
        overflow-y:hidden;
        }
        .card mjx-container[display="true"]{
        display:block;
        margin:14px 0;
        padding-bottom:2px;
        }
        .card .MathJax_Display, .card .MJXc-display, .card .MathJax_SVG_Display{
        overflow-x:auto;
        overflow-y:hidden;
        max-width:100%;
        }
        .card img.latex{
        max-width:100%;
        width:auto;
        height:auto;
        }
        table{
        border-collapse:separate;
        border-spacing:0;
        width:100%;
        margin:18px 0;
        font-size:.92em;
        border:1px solid var(--line);
        border-radius:16px;
        overflow:hidden;
        box-shadow:0 2px 4px rgba(46,42,36,.12), 0 6px 14px rgba(46,42,36,.14);
        }
        th, td{ padding:10px 13px; text-align:left; border-bottom:1px solid var(--line); }
        tr:last-child td{ border-bottom:none; }
        th{ background:linear-gradient(160deg, #ffffff 0%, var(--accent-soft) 100%); color:var(--accent-dark); font-weight:700; box-shadow:inset 0 -1px 0 rgba(46,42,36,.06); }
        
        /* mode nuit (desktop + AnkiDroid) */
        .night_mode body, body.night_mode, .nightMode body, body.nightMode{
        background-color:#211d18;
        background-image:radial-gradient(circle, rgba(143,195,158,.22) 1.5px, transparent 1.5px);
        background-size:22px 22px;
        }
        .night_mode .card, .card.night_mode, .nightMode .card, .card.nightMode{
        --ink:#f0e9db;
        --ink-soft:#bcb2a0;
        --accent:#8fc39e;
        --accent-light:#a8d4b3;
        --accent-dark:#c7e6cd;
        --accent-soft:rgba(143,195,158,.18);
        --accent2:#e08e6f;
        --accent2-light:#eaab90;
        --accent2-dark:#f2c6b3;
        --accent2-soft:rgba(224,142,111,.18);
        --line:#3b352c;
        --code-bg:#332e26;
        --code-ink:#e9dfcb;
        --code-dark-bg:#171410;
        --code-dark-bg2:#211d17;
        --code-dark-ink:#f0e9db;
        background:linear-gradient(165deg, #332e24 0%, #2a251d 100%);
        box-shadow:0 22px 46px rgba(0,0,0,.45), 0 2px 6px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.06);
        }
        .night_mode .divider span, .nightMode .divider span{ background:linear-gradient(160deg, #3a352c 0%, var(--accent-soft) 100%); box-shadow:0 4px 10px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.10), inset 0 -2px 3px rgba(0,0,0,.25); }
        .night_mode .cloze, .nightMode .cloze{ background:linear-gradient(160deg, #3a352c 0%, var(--accent2-soft) 100%); box-shadow:0 3px 7px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.10); }
        .night_mode code, .nightMode code{ background:linear-gradient(160deg, #3a352c 0%, var(--code-bg) 100%); box-shadow:0 2px 5px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.08); }
        .night_mode th, .nightMode th{ background:linear-gradient(160deg, #3a352c 0%, var(--accent-soft) 100%); box-shadow:inset 0 -1px 0 rgba(0,0,0,.2); }
        """
        
        self.MODEL_BASIC_ID = 1875392046
        self.model_basic = genanki.Model(
            self.MODEL_BASIC_ID,
            'Basique (Claude)',
            fields=[{'name': 'Front'}, {'name': 'Back'}, {'name': 'Sequence'}],
            sort_field_index=2,
            templates=[
                {
                    'name': 'Card 1',
                    'qfmt': '<div class="note">{{Front}}</div>',
                    'afmt': '<div class="note">{{Front}}</div>'
                            '<div class="divider"><span>Reponse</span></div>'
                            '<div class="note answer">{{Back}}</div>',
                },
            ],
            css=self.CSS,
        )
        
        self.MODEL_GENERALITES_ID = 1875392091
        self.model_generalites = genanki.Model(
            self.MODEL_GENERALITES_ID,
            'Generalites deux sens (Claude)',
            fields=[{'name': 'Front'}, {'name': 'Back'}, {'name': 'Sequence'}],
            sort_field_index=2,
            templates=[
                {
                    'name': 'Sens 1',
                    'qfmt': '<div class="note">{{Front}}</div>',
                    'afmt': '<div class="note">{{Front}}</div>'
                            '<div class="divider"><span>Reponse</span></div>'
                            '<div class="note answer">{{Back}}</div>',
                },
                {
                    'name': 'Sens 2',
                    'qfmt': '<div class="note">{{Back}}</div>',
                    'afmt': '<div class="note">{{Back}}</div>'
                            '<div class="divider"><span>Reponse</span></div>'
                            '<div class="note answer">{{Front}}</div>',
                },
            ],
            css=self.CSS,
        )
        
        self.MODEL_CLOZE_ID = 1875392177
        self.model_cloze = genanki.Model(
            self.MODEL_CLOZE_ID,
            'Cloze (Claude)',
            model_type=genanki.Model.CLOZE,
            fields=[{'name': 'Text'}, {'name': 'Extra'}, {'name': 'Sequence'}],
            sort_field_index=2,
            templates=[
                {
                    'name': 'Cloze',
                    'qfmt': '<div class="note">{{cloze:Text}}</div>',
                    'afmt': '<div class="note">{{cloze:Text}}</div>'
                            '{{#Extra}}<div class="divider"><span>Info</span></div>'
                            '<div class="note answer">{{Extra}}</div>{{/Extra}}',
                },
            ],
            css=self.CSS,
        )

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

        chunks = semantic_split_with_ai(self.client, texte_numerote)

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
        missing_lines = [self.original_lines[line_num - 1].rstrip("\n") for line_num in missing_lines_num]

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

            prompt = rf"""ROLE
You are a structural parser and semantic segmentation agent for academic course notes.
Your task is to parse a markdown text provided with line numbers (format "LineNumber: Text") and structure the content into a flat, event-based conceptual graph.

OBJECTIVE
You will receive a chunk of the full course text.
Segment EVERY single line of this chunk into pedagogical building blocks. Each block belongs to a primary concept (Theorem, Proposition, Definition, Lemma, Corollary, Context) and has a specific pedagogical function (Statement, Proof, Example, Remark, Exercise).

STRICT RULES:
1. THE FLAT SCHEMA (UNIVERSAL BLOCK):
   Every JSON object you generate MUST represent a text block using these 4 exact keys:
   - "concept_id": The parent concept's ID. Must strictly match the regex "^(Theorem|Proposition|Property|Definition|Lemma|Corollary|Context)_[0-9]{2}$".
   - "concept_name": The explicit name of the concept if stated in the text (e.g., "Monotone Convergence Theorem"), otherwise give it a title.
   - "element_type": The pedagogical function of this specific text block. MUST be exactly one of: ["Statement", "Proof", "Example", "Remark", "Exercise"].
   - "lines": A list of line intervals [[start, end]] for this block. If an image tag appear ("![img-2.jpeg](img-2.jpeg)") , you must keep it in the interval.

2. CONCEPT CREATION VS SUB-ELEMENTS:
   - To introduce a NEW formal concept, output a block with "element_type": "Statement" and generate a NEW incremented "concept_id".
   - To attach a sub-element (Proof, Example, Remark, Exercise) to a concept, output a block with the SAME "concept_id" as its parent, set "concept_name" to "None", and choose the correct "element_type".
   - NEVER create a standalone concept ID for an Example or Remark. They ALWAYS belong to a parent concept.

3. NON-CONTIGUOUS & DEFERRED ELEMENTS (THE GRAPH MEMORY):
   - Sub-elements are sometimes deferred (e.g., a Proof appearing 50 lines after its Theorem, or in a new chunk entirely).
   - Always bind each sub-element strictly to its true semantic parent.
   - MEMORY: Here are the main concepts already extracted in previous chunks:
     {main_nodes_for_ai}
   - If a block in the current text is a Proof, Example, or Remark related to one of these past concepts, use its exact "concept_id" from the list above. Do NOT invent a new concept_id.

4. EXHAUSTIVE PARTITION (CRITICAL - NO GAPS):
   - Every single line from the provided chunk MUST belong to exactly one interval in your output. Do not skip any line numbers.
   - For general text, introductions, or transitional paragraphs not attached to a mathematical theorem/definition, use a "Context_XX" concept_id with "element_type": "Statement".
   - NEVER create a "Context_XX" node for empty lines, titles, trailing equations, or secondary remarks. Instead, EXTEND the `[start, end]` interval of the related parent node to absorb them, or add a new sub-element under the SAME parent `concept_id`.
   - VERIFY YOUR INTERVALS: If the chunk goes from line 230 to 250, your intervals must seamlessly cover 230 to 250 without any gaps (e.g., [230, 235], [236, 245], [246, 250]). DO NOT drop lines.
   - REPEATED TITLES: If a concept spans across multiple identical headers (e.g., a slide title repeated on the next page), group ALL of it under the same `concept_id`. Do not stop at the first page.


OUTPUT FORMAT:
Output MUST be strictly valid JSON matching this schema:
{{
  "blocs": [
    {{
      "concept_id": "Theorem_01",
      "concept_name": "Bolzano-Weierstrass Theorem",
      "element_type": "Statement",
      "lines": [10, 15]
    }},
    {{
      "concept_id": "Definition_01",
      "concept_name": "Uniform continuity",
      "element_type": "Statement",
      "lines": [16, 20]
    }},
    {{
      "concept_id": "Theorem_01",
      "concept_name": "None",
      "element_type": "Proof",
      "lines": [21, 30]
    }}
  ]
}}
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
                                                    "pattern": "^(Theorem|Proposition|Property|Definition|Lemma|Corollary|Context)_[0-9]+[a-z]?$"
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
            parsed_data = json.loads(json_string)

            exhaustive_parsing,  missing_lines_num, missing_lines = self.exhaustivity_check_into_chunk(chunk, parsed_data)
            while exhaustive_parsing == False:
                print(f"⚠️ Retranscription incomplète pour ce chunk : {len(missing_lines)} ligne(s) non retranscrite(s) : {missing_lines_num}")
                print(f"❌ Lignes manquantes : {missing_lines}")

                # On demande à Mistral de corriger son output pour couvrir les lignes manquantes
                correction_prompt = rf"""
                ROLE
You are a precise conceptual graph correction agent. Your colleague has parsed a markdown course text into a JSON graph but missed specific line intervals. 
Your ONLY task is to analyze these missing lines and generate the missing JSON blocks to repair the graph.

OBJECTIVE
Read the source text and the already extracted JSON graph. 
Then, for each interval in the MISSING LINES list, create one or multiple JSON blocks to integrate this orphaned text.

STRICT RULES FOR RESOLUTION:
1. ATTACHMENT (Sub-elements): If the missing lines represent a Proof, Example, Remark, or Exercise that logically belongs to a concept already present in the EXISTING JSON, you MUST reuse the exact same "concept_id" from the existing JSON. Set "concept_name" to "None".
2. NEW CONCEPTS (Major omissions): If the missing lines contain a completely new Theorem, Proposition, Definition, Lemma, or Corollary that was ignored, create a NEW incremented "concept_id" (e.g., if "Theorem_01" exists, create "Theorem_02").
3. CONTEXT (Transitions): If the missing lines are introductory text, transitions, or isolated titles not tied to a specific mathematical property, create a new "Context_XX" concept_id with "element_type": "Statement".
4. NO REPETITION: Do NOT output blocks that are already in the EXISTING JSON. ONLY output blocks covering the missing lines.
5. EXHAUSTIVITY: The "lines" intervals in your output MUST perfectly cover all the numbers listed in MISSING LINES.

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
                response_correction = self.client.chat.complete(
                                    model="mistral-large-latest",
                                    messages=[{
                                        "role": "system",
                                        "content": correction_prompt
                                    }],
                                    temperature=0.0,
                                    response_format=graph_response_format
                                )
                json_string = response_correction.choices[0].message.content
                parsed_data_correction = json.loads(json_string)
                parsed_data["blocs"].extend(parsed_data_correction.get("blocs", []))
                exhaustive_parsing,  missing_lines_num, missing_lines = self.exhaustivity_check_into_chunk(chunk, parsed_data)
                
            # Sort data depending on the starting line of each block to maintain order
            parsed_data["blocs"].sort(key=lambda x: x["lines"][0])

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
    
    def markdown_to_anki_html(self, text: str) -> str:
        if not text:
            return ""

        placeholders = {}
        counter = 0

        def protect_block(match):
            nonlocal counter
            key = f"@@MATH_BLOCK_{counter}@@"
            content = match.group(1).strip()
            placeholders[key] = f"\\[\n{content}\n\\]"
            counter += 1
            return f"\n\n{key}\n\n"

        text = re.sub(r'\\+\[(.*?)\\+\]', protect_block, text, flags=re.DOTALL)
        text = re.sub(r'\$\$(.*?)\$\$', protect_block, text, flags=re.DOTALL)

        def protect_inline(match):
            nonlocal counter
            key = f"@@MATH_INLINE_{counter}@@"
            content = match.group(1).strip()
            placeholders[key] = f"\\({content}\\)"
            counter += 1
            return key

        def protect_code_fallback(match):
            nonlocal counter
            content = match.group(1).strip()
            if "@@MATH_BLOCK_" in content or "@@MATH_INLINE_" in content:
                return content
            else:
                key = f"@@MATH_INLINE_{counter}@@"
                placeholders[key] = f"\\({content}\\)"
                counter += 1
                return content

        text = re.sub(r'\\+\((.*?)\\+\)', protect_inline, text, flags=re.DOTALL)
        text = re.sub(r'(?<!\\)\$([^$\n]+?)(?<!\\)\$', protect_inline, text)
        # Capture les balises HTML <code>...</code> générées par le LLM
        text = re.sub(r'<code>(.*?)</code>', protect_code_fallback, text, flags=re.DOTALL)
        # Capture les backticks Markdown `...` générés par le LLM
        text = re.sub(r'`([^`\n]+?)`', protect_code_fallback, text)

        # 1. Ta liste de lettres rebelles (on utilise 'r' devant la chaîne pour que le \ soit bien lu)
        lettres_grecques = [
            r"\alpha", r"\beta", r"\gamma", r"\delta", r"\epsilon", r"\zeta", r"\eta", r"\theta",
            r"\iota", r"\kappa", r"\lambda", r"\mu", r"\nu", r"\xi", r"\pi", r"\rho",
            r"\sigma", r"\tau", r"\upsilon", r"\phi", r"\chi", r"\psi", r"\omega",
            r"\Alpha", r"\Beta", r"\Gamma", r"\Delta", r"\Epsilon", r"\Zeta", r"\Eta", r"\Theta",
            r"\Iota", r"\Kappa", r"\Lambda", r"\Mu", r"\Nu", r"\Xi", r"\Pi", r"\Rho",
            r"\Sigma", r"\Tau", r"\Upsilon", r"\Phi", r"\Chi", r"\Psi", r"\Omega"
        ]

        # 2. La boucle de rattrapage
        for lettre in lettres_grecques:

            # Si la lettre est encore visible dans le texte à ce stade,
            # c'est qu'elle est "nue" (sinon elle serait déjà cachée dans un @@MATH_...)
            if lettre in text:

                # On fabrique une nouvelle étiquette de boîte noire
                key = f"@@MATH_INLINE_{counter}@@"

                # On range la lettre dans le dictionnaire, mais cette fois bien encadrée par ses balises
                placeholders[key] = f"\\({lettre}\\)"

                # On remplace l'occurrence nue dans le texte par notre boîte noire
                text = text.replace(lettre, key)

                # On n'oublie pas d'augmenter le compteur pour la prochaine lettre !
                counter += 1

        html_output = markdown.markdown(
            text,
            extensions=['markdown.extensions.tables', 'markdown.extensions.nl2br'],
            output_format='html5'
        )

        for key in reversed(list(placeholders)):
            math_str = placeholders[key]
            html_output = html_output.replace(key, math_str)

        return html_output.strip()
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
        prompt = r"""ROLE
You are an expert in mathematics pedagogy and Spaced Repetition Systems (Anki). Your task is to take dense mathematical flashcard content and reformat it to be highly memorizable, visually light, and structured without losing any information.

OBJECTIVE
Reformat the provided raw content into a clean JSON structure. The `back` field must be a SINGLE STRING formatted with HTML and mathjax equations, strictly following the rules below.

STRICT RULES:
1. THEOREM / DEFINITION / PROPERTY (The Core Statement):
   - Preserve ALL mathematical information, rigor, and hypotheses.
   - Visually space it out: Use bullet points (<ul><li> </li></ul> or <li> </li>) to list hypotheses, conditions, or consequences instead of dense paragraphs.
   - Highlight key terms using bold (<b>text</b>).

2. PROOFS (Sketch of proof):
   - NEVER copy the full proof verbatim.
   - Replace the original proof with a section titled "<b>Sketch of proof:</b>" or "<b>Idea of the proof:</b>".
   - Summarize the proof's architecture into 2 or 3 essential anchor points (e.g., "1. Initialize with X", "2. Use Y inequality", "3. Conclude by taking the limit"). Get straight to the point.

3. JSON FORMATTING AND LATEX (CRITICAL):
   - The output MUST be a valid flat JSON object with exactly two keys: "front" and "back".
   - The "back" field MUST BE A SINGLE CONTINUOUS STRING containing all your HTML text. DO NOT create nested JSON objects (like "statement": {...} or "proof": {...}) inside the back field!
   - Because your output is JSON, you MUST double-escape all LaTeX backslashes. For example, write \\( ... \\) instead of \( ... \), and \\[ ... \\] instead of \[ ... \], and \\frac instead of \frac.
   - Use single quotes ('') inside HTML attributes, never unescaped double quotes.
   - Keep images and figures in their original format (e.g., ![img-2.jpeg](img-2.jpeg)).

4. STRICT FORMATTING (CRITICAL):
   - The use of \\text{} or \\begin{aligned} is STRICTLY FORBIDDEN.
   - \\begin{array} or \\begin{matrix} environments are tolerated ONLY inside mathematical blocks \\[ ... \\] for real mathematical matrices. They are STRICTLY FORBIDDEN to format or structure natural text.
   - You must ensure that natural text is in plain text/HTML (use <b> instead of **).
   - You must ensure that EVERY mathematical expression (even a simple variable) is enclosed by \\( ... \\) for inline, or \\[ ... \\] for block mode. Verify that all \\( tags are properly closed by \\). Fix errors like \\( X_a(t) \" to \\( X_a(t) \\).
   - Never use <code> or <pre> tags for mathematical expressions. Use ONLY \\( ... \\) or \\[ ... \\].
   - NEVER leave bare LaTeX symbols or variables (like \\Omega, \\sigma, \\mu, t, s) in plain text. You MUST enclose EVERY single mathematical symbol or letter in inline math delimiters \\... \\), even if it is a single character.
   
5. INVALID LaTeX Environments: (CRITICAL)
   - NEVER USE \begin{itemize} or \\item. Use HTML tags (<ul>, <li>).
   - NEVER USE mathematical delimiters like $, $$. Use ONLY \\( and \\[.
6. NO DELETION OF SECONDARY FACTS: 
   - You are strictly forbidden from deleting secondary definitions, remarks, or historical names present in the raw text. 
   - If multiple concepts are present, use clear bold sub-headings to include ALL of them on the back of the card without dropping information.
   
INPUT FORMAT:
[Front] The title of the card.
[Back] The raw text including the statement, proof, and examples.

OUTPUT FORMAT:
{
  "front": "The title or question (cleaned up if necessary, double-escaping LaTeX).",
  "back": "The newly formatted content combining the spaced-out statement, the sketch of proof, and the collapsible examples (all inside ONE single string, double-escaping LaTeX)."
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
                            "description": "Creation of the graph",
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
                            },
                            "additionalProperties": False
                        }
                    }
                )
        
        json_string = response.choices[0].message.content
        parsed_data = json_repair.loads(json_string)

        return parsed_data.get("front", ""), parsed_data.get("back", "")
# ==========================================
# 3. EXÉCUTION PRINCIPALE
# ==========================================


def main():
    API_KEY = os.environ.get("MISTRAL_API_KEY")
    if not API_KEY:
        print("Erreur: Clé API manquante.")
        return

    markdown_file, media_files = traiter_pdf_vers_markdown()

    pipeline = AnkiPipeline(API_KEY, markdown_file, media_files)
    
    print("1. Découpage du document...")
    chunks = pipeline.markdown_into_chunk(markdown_file)
    
    print(f"2. Analyse locale de {len(chunks)} chunks via LLM...")
    graph = pipeline.etape_2_map_analyse_locale(chunks)

    #Affichage et enregistrement du graphe avec graphviz
    A = nx.nx_agraph.to_agraph(graph)
    A.draw('AdvancedProbabilities.png', prog='dot')

    print("3. Création de la liste de cartes pour Anki")
    concept_list = pipeline.extraire_blocs_pour_anki()

    print("Création du paquet Anki")
    my_deck = genanki.Deck(pipeline.generer_id_deterministe('AdvancedProbabilities'),'AdvancedProbabilities')
    context_deck = genanki.Deck(pipeline.generer_id_deterministe('AdvancedProbabilities::Contexts'),'AdvancedProbabilities::Contexts')
    theorem_deck = genanki.Deck(pipeline.generer_id_deterministe('AdvancedProbabilities::Theorems'), 'AdvancedProbabilities::Theorems')
    property_deck = genanki.Deck(pipeline.generer_id_deterministe('AdvancedProbabilities::Properties'),'AdvancedProbabilities::Properties')
    lemma_deck = genanki.Deck(pipeline.generer_id_deterministe('AdvancedProbabilities::Lemma'), 'AdvancedProbabilities::Lemma')
    definition_deck = genanki.Deck(pipeline.generer_id_deterministe('AdvancedProbabilities::Definitions'), 'AdvancedProbabilities::Definitions')
    corollary_deck = genanki.Deck(pipeline.generer_id_deterministe('AdvancedProbabilities::Corollary'), 'AdvancedProbabilities::Corollary')

    deck_dict = {"Theorem":theorem_deck, "Proposition": property_deck,"Property": property_deck,"Definition" : definition_deck,
                 "Lemma": lemma_deck,"Corollary": corollary_deck, "Context": context_deck}

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
        if len(back) + length_example + length_remark + length_exercice < 30:
            print("This card has a very short back content, skipping it to avoid empty cards.\n Front: {}\nBack: {}".format(front, back))
        else:
            front = ""
            front, back = pipeline.course_into_flashcards(front, back)
            # Add examples, remarks and exercises in collapsible sections
            
            if example:
                back += "<details><summary>Examples (click to expand)</summary>" + example[0] + "</details><br>"
            if remark:
                back += "<details><summary>Remarks (click to expand)</summary>" + remark[0] + "</details><br>"
            if exercice:
                back += "<details><summary>Exercises (click to expand)</summary>" + exercice[0] + "</details><br>"

            back = pipeline.markdown_to_anki_html(back)  # Ensure back is in HTML format
            my_note = genanki.Note(
                model=pipeline.model_basic,
                fields=[front, back, str(j)])
            j += 1
            deck_dict[card["main_id"].split("_")[0]].add_note(my_note)

    my_package = genanki.Package([my_deck] + list(deck_dict.values()))
    my_package.media_files = media_files 
    my_package.write_to_file('AdvancedProbabilities.apkg')
    print("✅ Génération du paquet Anki terminée !")
        
    print("Terminé !")

if __name__ == "__main__":
    main()