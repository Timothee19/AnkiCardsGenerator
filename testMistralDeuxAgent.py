import os
import json
import re
import networkx as nx
import genanki
from typing import List, Dict, Tuple
from pydantic import BaseModel, Field
from mistralai.client import Mistral
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
   - "concept_name": The explicit name of the concept if stated in the text (e.g., "Monotone Convergence Theorem"), otherwise "None".
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

4. EXHAUSTIVE PARTITION (NO OMISSIONS):
   - Every single line from the provided chunk MUST belong to exactly one interval in your output.
   - For general text, introductions, or transitional paragraphs not attached to a mathematical theorem/definition, use a "Context_XX" concept_id with "element_type": "Statement".
   - Do not arbitrarily fragment intervals. Group contiguous lines belonging to the same element into a single [[start, end]] interval.

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
                        response_format={
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
                                                "pattern": "^(Theorem|Proposition|Property|Definition|Lemma|Corollary|Context)_[0-9]{2}$"
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
                    )
                    
            json_string = response.choices[0].message.content
            parsed_data = json.loads(json_string)
            print(parsed_data.get("blocs",[]))
            
            
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
                        
                        #idx_start = max(0, start_line - 1)
                        #idx_end = min(len(markdown_lines), end_line)

                        # --- SMART EXPAND ---
                        """
                        while idx_end < len(markdown_lines):
                            next_line_clean = line_number_regex.sub("", markdown_lines[idx_end]).strip()
                            if next_line_clean == "" or next_line_clean in ["\\]", "$$", "]", "\\)"]:
                                idx_end += 1
                            else:
                                break"""
                                
                        #covered_lines.update(range(start_line, idx_end))
                        
                        raw_slice = markdown_lines[start_line-1:end_line]
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
    def etape_4_generation_anki(self, G: nx.DiGraph, output_filename: str):
        """
        Parcourt le graphe complété et génère le deck de manière 100% algorithmique.
        """
        # TODO: Initialiser genanki.Deck et les modèles de cartes
        
        # Parcours des noeuds principaux (Théorèmes, Définitions...)
        for node in self.G.nodes():
            if "_" in node and node.split("_")[0] in ["Theorem", "Proposition", "Corollary", "Lemma", "Definition", "Context"]:
                front_html = self.G.nodes[node]['label']
                back_html = ""
                
                # Récupération des sous-noeuds (Énoncé, Démo, etc.)
                sub_nodes = [v for u, v in G.out_edges(node)]
                
                # TODO: Trier les sub_nodes dans un ordre logique (Enoncé d'abord, puis Démo, etc.)
                # TODO: Convertir G.nodes[sub_node]['text'] de Markdown à HTML
                # TODO: Concaténer dans back_html
                
                # my_note = genanki.Note(fields=[front_html, back_html])
                # my_deck.add_note(my_note)
                pass

        # TODO: my_package.write_to_file(output_filename)
        pass

# ==========================================
# 3. EXÉCUTION PRINCIPALE
# ==========================================
import markdown

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
    all_results = []
    graph = pipeline.etape_2_map_analyse_locale(chunks)
    #Affichage et enregistrement du graphe avec graphviz
    A = nx.nx_agraph.to_agraph(graph)
    A.draw('AI_Chap2Test.png', prog='dot') 
    print("3. Création de la liste de cartes pour Anki")
    concept_list = pipeline.extraire_blocs_pour_anki()
    print("Markdown to html")
    def markdown_to_anki_html(text: str) -> str:
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

        text = re.sub(r'\\+\[(.*?)(?:\\+\]|\Z)', protect_block, text, flags=re.DOTALL)
        text = re.sub(r'\$\$(.*?)(?:\$\$|\Z)', protect_block, text, flags=re.DOTALL)

        def protect_inline(match):
            nonlocal counter
            key = f"@@MATH_INLINE_{counter}@@"
            content = match.group(1).strip()
            placeholders[key] = f"\\({content}\\)"
            counter += 1
            return key

        text = re.sub(r'\\+\((.*?)\\+\)', protect_inline, text, flags=re.DOTALL)
        text = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', protect_inline, text)

        html_output = markdown.markdown(
            text,
            extensions=['markdown.extensions.tables', 'markdown.extensions.nl2br'],
            output_format='html5'
        )

        for key, math_str in placeholders.items():
            html_output = html_output.replace(f"<p>{key}</p>", math_str)
            html_output = html_output.replace(f"{key}<br>", math_str)
            html_output = html_output.replace(key, math_str)

        html_output = html_output.replace("<p>", "")
        html_output = html_output.replace("</p>", "<br><br>")
        
        while html_output.endswith("<br>"):
            html_output = html_output[:-4]

        return html_output.strip()

    import genanki
    import random
    
    CSS = r"""
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
    
    MODEL_BASIC_ID = 1875392046
    model_basic = genanki.Model(
        MODEL_BASIC_ID,
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
        css=CSS,
    )
    
    MODEL_GENERALITES_ID = 1875392091
    model_generalites = genanki.Model(
        MODEL_GENERALITES_ID,
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
        css=CSS,
    )
    
    MODEL_CLOZE_ID = 1875392177
    model_cloze = genanki.Model(
        MODEL_CLOZE_ID,
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
        css=CSS,
    )




    import hashlib

    def generer_id_deterministe(chaine_texte):
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


    my_deck = genanki.Deck(
    generer_id_deterministe('AI_Chap2'),
    'AI_Chap2')
    context_deck = genanki.Deck(generer_id_deterministe('AI_Chap2::Contexts'),'AI_Chap2::Contexts')
    theorem_deck = genanki.Deck(generer_id_deterministe('AI_Chap2::Theorems'), 'AI_Chap2::Theorems')
    property_deck = genanki.Deck(generer_id_deterministe('AI_Chap2::Properties'),'AI_Chap2::Properties')
    lemma_deck = genanki.Deck(generer_id_deterministe('AI_Chap2::Lemma'), 'AI_Chap2::Lemma')
    definition_deck = genanki.Deck(generer_id_deterministe('AI_Chap2::Definitions'), 'AI_Chap2::Definitions')
    corollary_deck = genanki.Deck(generer_id_deterministe('AI_Chap2::Corollary'), 'AI_Chap2::Corollary')

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
            html_text = markdown_to_anki_html(card["sub_nodes"][i]["text"])
            
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
        if example:
            back += "<strong>Example(s) :</strong><br>" + "<br><br>".join(example) + "<br><br>"
        if remark:
            back += "<strong>Remark(s) :</strong><br>" + "<br><br>".join(remark) + "<br><br>"
        if exercice:
            back += "<strong>Exercise(s) :</strong><br>" + "<br><br>".join(exercice) + "<br><br>"


        
        my_note = genanki.Note(
            model=model_basic,
            fields=[front, back, str(j)])
        j += 1
        deck_dict[card["main_id"].split("_")[0]].add_note(my_note)

    my_package = genanki.Package([my_deck] + list(deck_dict.values()))
    my_package.media_files = media_files 
    my_package.write_to_file('AI_Chap2Test.apkg')
    print("✅ Génération du paquet Anki terminée !")
        
    print("Terminé !")

if __name__ == "__main__":
    main()