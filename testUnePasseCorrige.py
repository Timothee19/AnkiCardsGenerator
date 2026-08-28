import networkx as nx
import pygraphviz as pgv
import pydot
import os
import json
import re
import markdown
import genanki

from ocr import traiter_pdf_vers_markdown
from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

labels_fr = ["Théorème", "Proposition", "Corollaire", "Lemme", "Définition", "Contexte"]
sub_labels_fr = ["Enoncé", "Démonstration", "Exemple", "Remarque", "Exercice"]
labels_en = ["Theorem", "Proposition", "Corollary", "Lemma", "Definition", "Context"]
sub_labels_en = ["Proof", "Example", "Remark", "Exercise"]

#==========================
# Numérotation du markdown
#==========================

markdown_file, media_files = traiter_pdf_vers_markdown()

def numeroter_fichier_markdown(input_path: str, output_path: str = None) -> str:
    
    #Lit un fichier Markdown et génère un nouveau fichier où chaque ligne 
    #est précédée de son numéro de ligne (1-based).
    
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Le fichier '{input_path}' n'existe pas.")

    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_numerote{ext}"

    with open(input_path, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    lignes_numerotees = []
    
    for i, ligne in enumerate(lignes, 1):
        ligne_propre = ligne.rstrip('\n')
        lignes_numerotees.append(f"{i}: {ligne_propre}\n")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lignes_numerotees)

    print(f"✅ Fichier numéroté avec succès : {output_path}")
    return output_path

# Utilisation de la variable dynamique au lieu du chemin en dur
numbered_markdown_output = numeroter_fichier_markdown(markdown_file, "markdown_numerote.md")

if os.path.exists("markdown_numerote.md"):
    with open("markdown_numerote.md", "r", encoding="utf-8") as f:
        markdown_lines = f.read()

from mistralai.client import Mistral

api_key = os.environ.get("MISTRAL_API_KEY")
model = "mistral-large-latest"
client = Mistral(api_key=api_key)

#================================================
# AGENT 1 : MainNodeParserAgent (Le Squelette)
#================================================

inputs = [
    {"role":"system", "content":r"""
ROLE
You are a structural parser and semantic extraction agent for academic course notes.
Your task is to parse a markdown text provided with line numbers (format "LineNumber: Text") and extract the sequence of primary concepts into a structured list.
Note: You are the FIRST agent in a pipeline. Your job is ONLY to extract the main conceptual blocks (ALL OF THEM). A second agent will process the internal sub-elements later.

OBJECTIVE
Identify every primary pedagogical concept (Théorème, Proposition, Définition, Lemme, Corollaire) or general introductory/transitional material (Contexte) in the document.

STRICT RULES:
1. WHAT IS A NODE:
   - A node is ONLY created when introducing a formal concept.
   - "main": A string combining the exact concept type and a 2-digit incremented index for that specific type (e.g., "Théorème_01", "Définition_01", "Contexte_01").
   - The type part of "main" MUST be strictly chosen from this exact list: ["Théorème", "Proposition", "Corollaire", "Lemme", "Définition", "Contexte"].
   - "name": The explicit name of the concept if stated in the text (e.g., "Théorème de Pythagore", "Borel σ-algebra"). If no specific name is given, output exactly the string "None".
   - "first_line": The line number (integer) where this concept is introduced in the text.

2. STRICT CHRONOLOGICAL ORDERING (NO GROUPING BY TYPE):
   - You MUST scan the text linearly from line 1 to the end and record each main concept AT THE EXACT MOMENT it appears.
   - DO NOT group or sort concepts by type (e.g., DO NOT put all Definitions first, then all Theorems).
   - The "node" array MUST be strictly sorted by "first_line" in ascending order (e.g., line 1, then line 12, then line 45, then line 80...).
   - Types WILL and SHOULD be mixed sequentially in the output array according to their order of appearance in the text.

3. IGNORE SUB-ELEMENTS:
   - Whenever you encounter an Example, Remark, Proof, or Exercise in the text, you MUST IGNORE IT entirely. Do NOT create a node for these sub-elements. Your focus is strictly on the main parent concepts.

4. EXHAUSTIVE EXTRACTION (NO OMISSION):
   - Every single main theorem, definition, proposition, lemma, corollary, and context block present in the text must be extracted.
   - Every single line from line 1 to the end of the text must belong to at least one interval in the output.
   - For general text, table of contents, introduction sections, or summaries not attached to a single theorem/definition/proposition/corrolary/lemma, use a "Contexte" node.

OUTPUT FORMAT:
Output MUST be strictly valid JSON matching this schema:

{
    "node": [
        {
            "main": "Contexte_01",
            "name": "Introduction aux espaces mesurables",
            "first_line": 1
        },
        {
            "main": "Définition_01",
            "name": "Tribu de Borel",
            "first_line": 12
        }
    ]
}
    """},
    {"role":"user","content":markdown_lines}
]

print("🧠 Agent 1 en cours d'exécution (Squelette)...")
chat_response = client.chat.complete(
    model= model,  # Corrigé pour utiliser mistral-large-latest
    messages=inputs,
    temperature=0.0,
    top_p=1.0,
    response_format={
          "type": "json_schema",
          "json_schema":{
            "description": "Extraction des concepts du cours pour création d'un graphe",
            "name": "extraction_concepts",
            "schema_definition":{
                "type": "object",
                "required": ["node"],
                "properties": {
                    "node": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["main", "first_line"],
                            "properties": {
                                "main": {
                                    "type": "string",
                                    "pattern": "^(Théorème|Proposition|Corollaire|Lemme|Définition|Contexte)_[0-9]{2}$"
                                },
                                "name": {
                                    "type": "string",
                                    "default": "None"
                                },
                                "first_line": {
                                    "type": "integer",
                                    "minimum": 1
                                }
                            }
                        }
                    }
                }
            },
            "strict":True
        }
    }
)

json_string = chat_response.choices[0].message.content
parsed_data = json.loads(json_string)
print(parsed_data.get("node",[]))
def create_graph_from_mistral_output(parsed_json):
    G = nx.DiGraph()
    i = 0
    previous_node = None
    
    for node_info in parsed_json.get("node", []):
        i += 1
        main_node_id = node_info.get("main")
        name = node_info.get("name")
        node_name = main_node_id + " : " + name if name and name != "None" else main_node_id

        G.add_node(main_node_id, label=node_name)

        if i >= 2:
            G.add_edge(previous_node, main_node_id, label=i-1, link="next_topic")

        previous_node = main_node_id
        
    return G

G = create_graph_from_mistral_output(parsed_data)

#================================================
# AGENT 2 : Création des sous-nœuds (Le Détaillant)
#================================================
print("🧠 Agent 2 en cours d'exécution (Détaillant)...")

nodes_list = parsed_data.get("node", [])
total_lines = len(markdown_lines) # Nombre total de lignes de ton document

for i, node_info in enumerate(nodes_list):
    parent_id = node_info.get("main")
    name = node_info.get("name", "None")
    first_line = node_info.get("first_line", 1)

    # 1. On détermine la frontière du concept suivant (La magie de l'Agent 2)
    if i + 1 < len(nodes_list):
        next_concept_line = nodes_list[i+1].get("first_line", total_lines)
    else:
        next_concept_line = total_lines # Fin du doc pour le tout dernier concept
        
    # 2. On crée le label en incluant TOUT : ID, Nom (s'il y en a un), Ligne de départ, et Limite
    if name != "None":
        label = f"{parent_id} - Name: {name} - Starts at line: {first_line} (Next concept boundary is line: {next_concept_line})"
    else:
        label = f"{parent_id} - Starts at line: {first_line} (Next concept boundary is line: {next_concept_line})"

    # 3. On injecte ce label ultra-précis dans le prompt
    sub_nodes_inputs = [{"role": "system", "content": fr"""
    ROLE
    You are a targeted semantic extraction agent for academic course notes. You are the SECOND agent in a parsing pipeline.
    You will be provided with a specific TARGET CONCEPT (its ID, Name, Starting Line, and Next Concept Boundary) and a markdown text with numbered lines.

    OBJECTIVE
    Perform a fine-grained analysis of the document to extract ALL the text blocks (line intervals) that belong strictly to the provided TARGET CONCEPT. You must categorize these blocks into specific sub-nodes.

    STRICT RULES:
    1. HYBRID BOUNDARIES (CRITICAL):
       - LOCAL ELEMENTS: "Enoncé", "Exemple", and "Remarque" almost always immediately follow the concept. They MUST be extracted strictly between the 'Starting line' and the 'Next concept boundary' provided in the prompt. Do NOT look for examples or remarks beyond the next concept line.
       - GLOBAL ELEMENTS: "Démonstration" and "Exercice" are sometimes deferred. You are authorized to scan the ENTIRE document to find a proof or exercise explicitly belonging to the TARGET CONCEPT.

    2. TARGET ISOLATION (NO SCOPE BLEED):
       - You must ONLY extract elements that belong explicitly to the TARGET CONCEPT. 
       - If an example introduces a new Theorem or Definition, it belongs to that new concept, NOT the current one.
       - Never assign the exact same Example or Proof to two different parent nodes.

    3. SUB-NODE CATEGORIZATION & JUSTIFICATION:
       - Every extracted block must be assigned a "type" strictly chosen from this exact list: ["Enoncé", "Démonstration", "Exemple", "Remarque", "Exercice"].
       - "Enoncé" refers to the core statement/definition of the concept itself. You cannot invent new types.
       - For EVERY sub-node you extract, you MUST write a brief "reason" explaining exactly WHY these specific lines belong to the target concept.

    4. LINE INTERVALS (startEndListPositions):
       - For each sub-node type, you must provide a list of line intervals: `[[start_line, end_line], ...]`
       - If there are multiple disjoint blocks for the same type (e.g., a proof split in two parts), append all their intervals to the same list: `[[start1, end1], [start2, end2]]`.
       - If a specific type does not exist for the target concept, simply do not include that type in the output.

    INPUT FORMAT EXPECTED:
    TARGET CONCEPT: {label}

    OUTPUT FORMAT:
    Output MUST be strictly valid JSON matching this schema. Do not output anything else.

    {{
        "sub_nodes": [
            {{
                "type": "Enoncé",
                "reason": "This is the core statement of the concept starting at the provided line.",
                "startEndListPositions": [[10, 15]]
            }},
            {{
                "type": "Démonstration",
                "reason": "Lines 40-50 contain the first part of the proof, and lines 120-135 explicitly resume the proof of this specific concept later in the text.",
                "startEndListPositions": [[40, 50], [120, 135]]
            }},
            {{
                "type": "Exemple",
                "reason": "Line 16 introduces an example directly applying the concept before the next boundary.",
                "startEndListPositions": [[16, 20]]
            }}
        ]
    }}
"""}, {"role": "user", "content": markdown_lines}]

    # 4. Appel à l'API Mistral (client.chat.complete...)
    
    sub_node_mistral = client.chat.complete(
        model= "mistral-small-latest",
        messages=sub_nodes_inputs,
        temperature=0.0,
        top_p=1.0,
        response_format={
            "type": "json_schema",
            "json_schema":{
                "description": "Extraction des sous catégorie du cours",
                "name": "extraction_semantique",
                "schema_definition":{
  "type": "object",
  "title": "Semantic extraction of concept sub-nodes",
  "required": [
    "sub_nodes"
  ],
  "properties": {
    "sub_nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "type",
          "reason",
          "startEndListPositions"
        ],
        "properties": {
          "type": {
            "enum": [
              "Enoncé",
              "Démonstration",
              "Exemple",
              "Remarque",
              "Exercice"
            ],
            "type": "string",
            "description": "Type of sub-node from the allowed values"
          },
          "reason": {
            "type": "string",
            "description": "Detailed justification explaining why these lines belong to the target concept"
          },
          "startEndListPositions": {
            "type": "array",
            "items": {
              "type": "array",
              "minItems": 2,
              "maxItems": 2,
              "items": {
                "type": "integer"
              }
            },
            "description": "List of line intervals (start, end) for this sub-node type"
          }
        }
      },
      "minItems": 1,
      "description": "List of sub-nodes extracted for the target concept"
    }
  },
  "additionalProperties": False
},
                "strict":True
            }
        }
    )

    sub_raw_json = sub_node_mistral.choices[0].message.content
    sub_data = json.loads(sub_raw_json)

    for item in sub_data.get("sub_nodes", []):
        sub_type = item.get("type")
        positions = item.get("startEndListPositions", [])

        for pos in positions:
            sub_node_id = f"{parent_id}_{sub_type}_{pos[0]}_{pos[1]}"
            G.add_node(
                sub_node_id,
                label=sub_type,
                pos=pos,
                is_main=False
            )
            G.add_edge(parent_id, sub_node_id, link="link")

# Dessin du graphe final
A = nx.nx_agraph.to_agraph(G)
A.draw('GraphMainLebesgue.png', prog='dot')

#====================================================
# Création du paquet ANKI
#====================================================

def extraire_blocs_pour_anki(G: nx.DiGraph, markdown_source: str, start_node: str = None):
    if os.path.exists(markdown_source):
        with open(markdown_source, "r", encoding="utf-8") as f:
            markdown_lines = f.readlines()
    else:
        markdown_lines = markdown_source.splitlines(keepends=True)

    total_lines_count = len(markdown_lines)
    all_lines = set(range(1, total_lines_count+1))
    covered_lines = set()
    
    line_number_regex = re.compile(r"^\s*\d+[\s\|\:\.\-\)]\s*")

    if start_node is None:
        for node in G.nodes():
            in_links = [data.get("link") for _, _, data in G.in_edges(node, data=True)]
            if "next_topic" not in in_links and any(data.get("link") == "next_topic" for _, _, data in G.out_edges(node, data=True)):
                start_node = node
                break

    if start_node is None and len(G) > 0:
        start_node = next(iter(G.nodes()))

    concepts_list = []
    current_main = start_node

    while current_main is not None:
        main_data = {
            "main_id": current_main,
            "label": G.nodes[current_main].get("label", current_main),
            "sub_nodes": []
        }

        next_main = None

        for _, neighbor, edge_data in G.out_edges(current_main, data=True):
            if edge_data.get("link") == "link":
                pos = G.nodes[neighbor].get("pos")
                extracted_text = ""

                if pos and len(pos) == 2:
                    start_line, end_line = pos[0], pos[1]
                    covered_lines.update(range(start_line, end_line))
                    
                    idx_start = max(0, start_line - 1)
                    idx_end = min(len(markdown_lines), end_line)

                    # --- SMART EXPAND ---
                    while idx_end < len(markdown_lines):
                        next_line_clean = line_number_regex.sub("", markdown_lines[idx_end]).strip()
                        if next_line_clean == "" or next_line_clean in ["\\]", "$$", "]", "\\)"]:
                            idx_end += 1
                        else:
                            break
                            
                    covered_lines.update(range(start_line, idx_end))
                    
                    raw_slice = markdown_lines[idx_start:idx_end]
                    cleaned_lines = [line_number_regex.sub("", line) for line in raw_slice]
                    extracted_text = "".join(cleaned_lines).strip()

                main_data["sub_nodes"].append({
                    "sub_id": neighbor,
                    "type": G.nodes[neighbor].get("label"),
                    "text": extracted_text
                })

            elif edge_data.get("link") == "next_topic":
                next_main = neighbor

        concepts_list.append(main_data)
        current_main = next_main

    # 4. Vérification de la complétude (Désindentée pour s'exécuter 1 seule fois !)
    missing_lines = sorted(all_lines - covered_lines)
        
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

    return concepts_list

# Utilisation de la variable markdown_numerote.md
anki_source = extraire_blocs_pour_anki(G, "markdown_numerote.md")

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
 
.cloze{
  font-weight:600;
  color:var(--accent2-dark);
  background:linear-gradient(160deg, rgba(193,105,79,.07) 0%, rgba(193,105,79,.17) 100%);
  padding:1px 7px;
  border-radius:5px;
  box-shadow:0 1px 2px rgba(193,105,79,.18), 0 2px 5px rgba(193,105,79,.18), inset 0 1px 0 rgba(255,255,255,.9);
}
 
img{
  max-width:100%;
  height:auto;
  display:block;
  margin:16px auto;
  border-radius:26px 8px 26px 8px;
  box-shadow:0 2px 4px rgba(46,42,36,.16), 0 6px 14px rgba(46,42,36,.18);
}
 
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
.card .MathJax_Display, .card .MJXc-display{
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

my_deck = genanki.Deck(
  2059400111,
  'AI_Chap2Test')

j=0
for card in anki_source:
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
        
        if sub_type == "Enoncé":
            enonce.append(html_text)
        elif sub_type == "Démonstration":
            proof.append(html_text)
        elif sub_type == "Remarque":
            remark.append(html_text)
        elif sub_type == "Exemple":
            example.append(html_text)
        elif sub_type == "Exercice":
            exercice.append(html_text)
            
    # Construction propre et sécurisée du dos de la carte
    if enonce:
        back += enonce[0] + "<br><br>"
    if proof:
        back += "<strong>Démonstration :</strong><br>" + proof[0] + "<br><br>"
    if example:
        back += "<strong>Exemple(s) :</strong><br>" + "<br><br>".join(example) + "<br><br>"
    if remark:
        back += "<strong>Remarque(s) :</strong><br>" + "<br><br>".join(remark) + "<br><br>"
    if exercice:
        back += "<strong>Exercice(s) :</strong><br>" + "<br><br>".join(exercice) + "<br><br>"
        
    my_note = genanki.Note(
        model=model_basic,
        fields=[front, back, str(j)])
    j += 1
    my_deck.add_note(my_note)

my_package = genanki.Package(my_deck)
my_package.media_files = media_files 
my_package.write_to_file('AI_Chap2Test.apkg')
print("✅ Génération du paquet Anki terminée !")