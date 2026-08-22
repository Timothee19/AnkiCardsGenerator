import networkx as nx
import pygraphviz as pgv
import pydot
import os
import json
import re
import markdown


labels_fr = ["Théorème", "Proposition", "Corollaire", "Lemme", "Définition", "Contexte"]
sub_labels_fr = ["Enoncé", "Démonstration", "Exemple", "Remarque", "Exercice"]
labels_en = ["Theorem", "Proposition", "Corollary", "Lemma", "Definition", "Context"]
sub_labels_en = ["Proof", "Example", "Remark", "Exercise"]


#==========================
# Numérotation du markdown
#==========================

from dotenv import load_dotenv

load_dotenv()  # reads variables from a .env file and sets them in os.environ

def numeroter_fichier_markdown(input_path: str, output_path: str = None) -> str:
    """
    Lit un fichier Markdown et génère un nouveau fichier où chaque ligne 
    est précédée de son numéro de ligne (1-based).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Le fichier '{input_path}' n'existe pas.")

    # Si aucun fichier de sortie n'est précisé, on ajoute '_numerote' au nom
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_numerote{ext}"

    # Lecture du fichier original
    with open(input_path, 'r', encoding='utf-8') as f:
        lignes = f.readlines()

    lignes_numerotees = []
    
    # enumerate(..., 1) permet de faire commencer le compteur à 1
    for i, ligne in enumerate(lignes, 1):
        # On retire le saut de ligne de fin pour construire notre chaîne proprement
        ligne_propre = ligne.rstrip('\n')
        lignes_numerotees.append(f"{i}: {ligne_propre}\n")

    # Écriture dans le nouveau fichier
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(lignes_numerotees)

    print(f"✅ Fichier numéroté avec succès : {output_path}")
    return output_path


def numeroter_texte_en_memoire(texte_markdown: str) -> str:
    """
    Numérote directement une chaîne de caractères (utile pour le pipeline LLM).
    """
    lignes = texte_markdown.splitlines()
    lignes_numerotees = [f"{i}: {ligne}" for i, ligne in enumerate(lignes, 1)]
    return "\n".join(lignes_numerotees)

numbered_markdown_output = numeroter_fichier_markdown("C:/Users/a956068/Downloads/ocr-playground-download-20260817T215800Z/Lebesgue_integral_V2.pdf/markdown.md","markown_numerote.md")

if os.path.exists(numbered_markdown_output):
        with open(numbered_markdown_output, "r", encoding="utf-8") as f:
            markdown_lines = f.read()

from mistralai.client import Mistral

client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY"))

#==================
# MainNodeParserAgent
#================================

inputs = [
    {"role":"system", "content":r"""
ROLE
You are a structural parser and semantic segmentation agent for academic course notes.
Your task is to parse a markdown text provided with line numbers (format "LineNumber: Text") and structure the entire content into a comprehensive conceptual graph.

OBJECTIVE
Segment every single line of the document into pedagogical concepts (nodes). Each node represents a primary mathematical/scientific concept (Theorem, Proposition, Definition, Lemma, Corollary) or general introductory/transitional material (Context), aggregating all associated elements (statements, proofs, examples, remarks, exercises).

STRICT RULES:
1. WHAT IS A NODE:
   - A node is ONLY created when introducing a formal concept: "Definition", "Théorème", "Proposition", "Lemme", "Corollaire", or "Contexte".
   - "main" MUST be strictly one of: ["Théorème", "Proposition", "Definition", "Lemme", "Corollaire", "Contexte"].
   - "name": The explicit name of the concept if stated (e.g., "Concept Alpha", "Theorem Beta"), otherwise "None".

2. STRICT SUB-ELEMENT AGGREGATION (NO STANDALONE EXAMPLES/REMARKS):
   - Whenever you encounter an "Example", "Remark", "Proof", or "Exercise" in the text, you MUST NEVER create a new node for it.
   - You MUST attach its line interval to the "startEndListPositionsConcept" dictionary of the PARENT concept that precedes it or that it illustrates.
   * Example in text: Lines 100-110 are "Example A". This is an example of the concept "Concept B" (Definition). Put lines 100-110 inside Concept B under the "Exemple" key.
   * Example in text: Lines 150-160 are "Example C". This is an example of "Theorem D". Put lines 150-160 inside Theorem D under the "Exemple" key.

3. NON-CONTIGUOUS & DEFERRED SUB-ELEMENT AGGREGATION:
   - Sub-elements (Proofs, Examples, Remarks, Exercises) are sometimes located far away from their parent statement or interleaved with unrelated concepts. 
   - Always bind each sub-element strictly to its true semantic parent, regardless of distance, page breaks, or intervening nodes.
   - Disjoint Resolution Example:
       {
  "nodes": [
    {
      "main": "Théorème",
      "name": "Théorème A",
      "startEndListPositionsConcept": {
        "Enoncé": [[200, 203]],
        "Démonstration": [[216, 240]]
      }
    },
    {
      "main": "Definition",
      "name": "Concept B",
      "startEndListPositionsConcept": {
        "Exercice": [[204, 215]]
      }
    }
  ]
}
   - Never default an interleaved sub-element to the nearest preceding concept; resolve the conceptual reference explicitly before assigning intervals.

4. EXHAUSTIVE PARTITION (NO OMISSIONS, NO OVERLAPS):
   - Every single line from line 1 to the end of the text must belong to at least one interval in the output.
   - For general text, table of contents, introduction sections, or summaries not attached to a single theorem/definition, use a "Contexte" node with "Enoncé".

OUTPUT FORMAT:
Output MUST be strictly valid JSON matching this schema:

{
    "nodes": [
        {
            "main": "Definition",
            "name": "Concept Alpha",
            "startEndListPositionsConcept": {
                "Enoncé": [[10, 15]],
                "Exemple": [[16, 20], [25, 30]]
            }
        },
        {
            "main": "Théorème",
            "name": "Theorem Beta",
            "startEndListPositionsConcept": {
                "Enoncé": [[35, 40]],
                "Démonstration": [[45, 55]],
                "Exemple": [[60, 65]]
            }
        },
        {
            "main": "Contexte",
            "name": "General Introduction",
            "startEndListPositionsConcept": {
                "Enoncé": [[1, 9]]
            }
        }
    ]
}
    """},
    {"role":"user","content":markdown_lines}
]

#Création du graphe à partir de la sortie de Mistral en une seule passe :

def create_graph_from_mistral_output_single_pass(mistral_output):
    G = nx.DiGraph()
    i=0
    for node_info in mistral_output.get("nodes", []):
        i+=1
        main_node = node_info.get("main")
        name = node_info.get("name")
        node_name = main_node +" : " + name if name else main_node # Use the name if available, otherwise use the main node

        G.add_node(main_node, label=node_name)

        #Connexions entre les noeuds principaux

        if i >= 2:
            G.add_edge(previous_node,main_node, label=i-1, link= "next_topic")

        previous_node = main_node

        start_end_positions = node_info.get("startEndListPositionsConcept", {})
        
        for sub_node_type, positions in start_end_positions.items():
            for position in positions:
                sub_node_id = f"{main_node}_{sub_node_type}_{position[0]}_{position[1]}"  # Unique ID for the sub-node
                G.add_node(sub_node_id, label=sub_node_type, pos=position)
                G.add_edge(main_node, sub_node_id, link = "link")  # Link the main node to its sub-node
    
    return G

api_key = os.environ["MISTRAL_API_KEY"]
model = "mistral-large-latest"

client = Mistral(api_key=api_key)

chat_response = client.chat.complete(
    model = "mistral-medium-latest",
    messages = inputs,
    temperature=0.0,
    top_p=1.0,
    response_format = {
          "type": "json_schema",
          "json_schema":{
              "schema" :{
                "type": "object",
                "required": [
                  "nodes"
                ],
                "properties": {
                  "nodes": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "main": {
                          "type": "string",
                          "pattern": "^(Théorème|Proposition|Definition|Lemme|Corrolaire|Contexte)_[0-9]{2}$"
                        },
                        "name": {
                          "type": "string",
                          "default": "None"
                        },
                        "startEndListPositionsConcept": {
                          "type": "object",
                          "properties": {
                            "Enoncé": {
                              "type": "array",
                              "items": {
                                "type": "array",
                                "items": {
                                  "type": "integer"
                                },
                                "maxItems": 2,
                                "minItems": 2
                              }
                            },
                            "Exemple": {
                              "type": "array",
                              "items": {
                                "type": "array",
                                "items": {
                                  "type": "integer"
                                },
                                "maxItems": 2,
                                "minItems": 2
                              }
                            },
                            "Exercice": {
                              "type": "array",
                              "items": {
                                "type": "array",
                                "items": {
                                  "type": "integer"
                                },
                                "maxItems": 2,
                                "minItems": 2
                              }
                            },
                            "Remarque": {
                              "type": "array",
                              "items": {
                                "type": "array",
                                "items": {
                                  "type": "integer"
                                },
                                "maxItems": 2,
                                "minItems": 2
                              }
                            },
                            "Démonstration": {
                              "type": "array",
                              "items": {
                                "type": "array",
                                "items": {
                                  "type": "integer"
                                },
                                "maxItems": 2,
                                "minItems": 2
                              }
                            }
                          },
                          "minProperties": 1,
                          "additionalProperties": False
                        }
                      }
                    },
                    "required": [
                      "main",
                      "startEndListPositionsConcept"
                    ]
                  }
                }
              }
  ,
"strict":True,
"name": "extraction_text_to_graph"
}}
      
)
mistral_output = chat_response
#print(chat_response)
# 1. On accède à la chaîne de caractères JSON contenue dans la réponse
json_string = mistral_output.choices[0].message.content

# 2. On transforme cette chaîne de caractères en vrai dictionnaire Python
parsed_data = json.loads(json_string)

# 3. Création d'un dictionnaire qui contient {main_node:name} pour chaque noeud renvoyé
# On utilise maintenant parsed_data au lieu de mistral_output
main_node = { node_info.get("main") : node_info.get("name") for node_info in parsed_data.get("nodes", []) }

#Création du graphe à partir de la sortie de Mistral en une seule passe :

def create_graph_from_mistral_output_single_pass(mistral_output):
    G = nx.DiGraph()
    i=0
    for node_info in mistral_output.get("nodes", []):
        i+=1
        main_node = node_info.get("main")
        name = node_info.get("name")
        node_name = main_node +" : " + name if name else main_node # Use the name if available, otherwise use the main node

        G.add_node(main_node, label=node_name)

        #Connexions entre les noeuds principaux

        if i >= 2:
            G.add_edge(previous_node,main_node, label=i-1, link= "next_topic")

        previous_node = main_node

        start_end_positions = node_info.get("startEndListPositionsConcept", {})
        
        for sub_node_type, positions in start_end_positions.items():
            for position in positions:
                sub_node_id = f"{main_node}_{sub_node_type}_{position[0]}_{position[1]}"  # Unique ID for the sub-node
                G.add_node(sub_node_id, label=sub_node_type, pos=position)
                G.add_edge(main_node, sub_node_id, link = "link")  # Link the main node to its sub-node
    
    return G

G = create_graph_from_mistral_output_single_pass(parsed_data)
A = nx.nx_agraph.to_agraph(G)
A.draw('GraphMainLebesgue.png', prog='dot')



#====================================================
# Création du paquet ANKI
#==========================================




def extraire_blocs_pour_anki(G: nx.DiGraph, markdown_source: str, start_node: str = None):
    # 1. Charger les lignes brutes du Markdown
    if os.path.exists(markdown_source):
        with open(markdown_source, "r", encoding="utf-8") as f:
            markdown_lines = f.readlines()
    else:
        markdown_lines = markdown_source.splitlines(keepends=True)

    total_lines_count = len(markdown_lines)
    all_lines = set(range(1, total_lines_count+1))
    covered_lines = set()

    # Expression régulière pour matcher les préfixes de type "1291: ", "1291 | ", etc.
    line_number_regex = re.compile(r"^\s*\d+[\s\|\:\.\-\)]\s*")

    # 2. Trouver la racine (nœud principal sans prédécesseur 'next_topic')
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

    # 3. Parcours séquentiel de la dorsale
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

                    covered_lines.update(range(start_line, end_line + 1))

                    # Conversion en index 0-based
                    idx_start = max(0, start_line - 1)
                    idx_end = min(len(markdown_lines), end_line)
                    
                    # Découpage puis suppression du préfixe numérique sur chaque ligne
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

    # 4. Vérification de la complétude
    missing_lines = sorted(all_lines - covered_lines)
    
    print("\n" + "=" * 50)
    if not missing_lines:
        print("✅ Intégralité respectée : 100% du Markdown a été retranscrit !")
    else:
        taux = ((total_lines_count - len(missing_lines)) / total_lines_count) * 100
        print(f"⚠️ Retranscription incomplète : {taux:.1f}% des lignes couvertes.")
        print(f"❌ {len(missing_lines)} ligne(s) non retranscrite(s).")
        
        # 1. Sauvegarde détaillée dans un fichier texte
        report_file = "lignes_manquantes_rapport.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(f"=== RAPPORT DES {len(missing_lines)} LIGNES MANQUANTES ===\n\n")
            for line_num in missing_lines:
                raw_content = markdown_lines[line_num - 1].rstrip("\n")
                f.write(f"[Ligne {line_num:4d}] : {raw_content}\n")
                
        print(f"📁 Le détail complet a été sauvegardé dans le fichier : {report_file}")
        
        # 2. Aperçu restreint dans la console (seulement les 10 premières)
        print("\n🔍 Aperçu des 10 premières lignes manquantes :")
        for line_num in missing_lines[:10]:
            raw_content = markdown_lines[line_num - 1].rstrip("\n")
            print(f"   [Ligne {line_num:4d}] : {raw_content}")
            
    print("=" * 50 + "\n")

    return concepts_list

    return concepts_list

anki_source = extraire_blocs_pour_anki(G, "markown_numerote.md")
import json


# Affiche le dictionnaire formaté sur plusieurs lignes avec encodage UTF-8 respecté
#print(json.dumps(anki_source, indent=4, ensure_ascii=False))





def markdown_to_anki_html(text: str) -> str:
    r"""
    Convertit le texte extrait en HTML compatible avec Anki.
    - Protège les équations des destructeurs Markdown.
    - Répare automatiquement les blocs d'équations dont la fin (\]) a été tronquée.
    - Supprime les balises <p> pour s'adapter à ton modèle de carte Anki.
    """
    if not text:
        return ""

    placeholders = {}
    counter = 0

    # ==========================================
    # 1. PROTECTION ET RÉPARATION DES BLOCS
    # ==========================================
    def protect_block(match):
        nonlocal counter
        key = f"@@MATH_BLOCK_{counter}@@"
        content = match.group(1).strip()
        # On force la fermeture parfaite pour Anki avec \[ et \]
        placeholders[key] = f"\\[\n{content}\n\\]"
        counter += 1
        return f"\n\n{key}\n\n"

    # Capture \[ ... \] ou $$ ... $$ 
    # Le |\Z permet de capturer même si le texte s'arrête net (LLM qui a mal compté les lignes)
    text = re.sub(r'\\+\[(.*?)(?:\\+\]|\Z)', protect_block, text, flags=re.DOTALL)
    text = re.sub(r'\$\$(.*?)(?:\$\$|\Z)', protect_block, text, flags=re.DOTALL)

    # ==========================================
    # 2. PROTECTION DES MATHS EN LIGNE
    # ==========================================
    def protect_inline(match):
        nonlocal counter
        key = f"@@MATH_INLINE_{counter}@@"
        content = match.group(1).strip()
        # On force le format Anki \( ... \)
        placeholders[key] = f"\\({content}\\)"
        counter += 1
        return key

    text = re.sub(r'\\+\((.*?)\\+\)', protect_inline, text, flags=re.DOTALL)
    text = re.sub(r'(?<!\\)\$([^\$\n]+?)(?<!\\)\$', protect_inline, text)

    # ==========================================
    # 3. CONVERSION MARKDOWN -> HTML
    # ==========================================
    html_output = markdown.markdown(
        text,
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.nl2br' # Conserve les sauts de ligne simples
        ],
        output_format='html5'
    )

    # ==========================================
    # 4. RÉINJECTION DES ÉQUATIONS INTACTES
    # ==========================================
    for key, math_str in placeholders.items():
        # Nettoyage des balises parasites de Markdown autour de nos jetons
        html_output = html_output.replace(f"<p>{key}</p>", math_str)
        html_output = html_output.replace(f"{key}<br>", math_str)
        html_output = html_output.replace(key, math_str)

    # ==========================================
    # 5. NETTOYAGE SPÉCIAL ANKI (Retrait des <p>)
    # ==========================================
    html_output = html_output.replace("<p>", "")
    html_output = html_output.replace("</p>", "<br><br>")
    
    # On retire les <br> superflus tout à la fin pour un rendu propre
    while html_output.endswith("<br>"):
        html_output = html_output[:-4]

    return html_output.strip()

print(len(anki_source))

enonce = []
proof = []
remark = []
example = []
sub_labels_fr = ["Enoncé", "Démonstration", "Exemple", "Remarque", "Exercice"]

for card in anki_source:
    #print(card["label"])
    for i in range(len(card["sub_nodes"])):
        if card["sub_nodes"][i]["type"] == "Enoncé":
            enonce.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Démonstration":
            proof.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Remarque":
            remark.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Exemple":
            example.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
    #print(enonce[0] + "\n")
    #if len(proof)>=1:
        #print(proof[0] + "\n")
    #if len(remark) >= 1:
        #print("\n".join(remark))
    #if len(example)>=1:
        #print("\n".join(example))
    
#========================================
# Création d'un paquet Anki intermédiaire
#========================================
import genanki


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
 
/* tableaux */
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
    'Basique (Claude)V2',
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


my_deck = genanki.Deck(
  2059400111,
  'LebesgueTestSinglePass')

j=0
for card in anki_source:
    enonce = []
    proof = []
    remark = []
    example = []
    front = ""
    back = ""
    front += card["label"]
    for i in range(len(card["sub_nodes"])):
        if card["sub_nodes"][i]["type"] == "Enoncé":
            enonce.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Démonstration":
            proof.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Remarque":
            remark.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Exemple":
            example.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
    back+=enonce[0] + "<br><br>"
    if len(proof)>=1:
        back+=proof[0] + "<br><br>"
    if len(remark) >= 1:
        back+="<br><br>".join(remark)
    if len(example)>=1:
        back+="<br><br>".join(example)
    my_note = genanki.Note(
    model=model_basic,
    fields=[front, back,str(j)])
    j+=1
    my_deck.add_note(my_note)

genanki.Package(my_deck).write_to_file('TestLebesgueSinglePasse.apkg')







