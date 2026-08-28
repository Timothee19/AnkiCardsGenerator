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
from AnkiGeneratorRobustV1_3.py import split_markdown_into_chunks, semantic_split_with_ai

chunks = semantic_split_with_ai(client, markdown_file)

sys_prompt = r"""
ROLE
You are a structural parser and semantic segmentation agent for academic course notes.
Your task is to parse a markdown text provided with line numbers (format "LineNumber: Text") and structure the entire content into a comprehensive conceptual graph.

OBJECTIVE
Segment every single line of the document into pedagogical concepts (nodes). Each node represents a primary mathematical/scientific concept (Theorem, Proposition, Definition, Lemma, Corollary) or general introductory/transitional material (Context), aggregating all associated elements (statements, proofs, examples, remarks, exercises).

STRICT RULES:
1. WHAT IS A NODE:
   - A node is ONLY created when introducing a formal concept: "Definition", "Théorème", "Proposition", "Lemme", "Corollaire", or "Contexte".
   - "main" MUST be strictly one of: ["Theorem", "Proposition","Property", "Definition", "Lemma", "Corollary", "Context"].
   - COMPLETELY FORBIDDEN: You must NEVER use "Exemple_XX", "Remarque_XX", "Démonstration_XX", or "Exercice_XX" as a main node.
   - "name": The explicit name of the concept if stated (e.g., "Concept Alpha", "Theorem Beta"), otherwise "None".

2. STRICT SUB-ELEMENT AGGREGATION (NO STANDALONE EXAMPLES/REMARKS):
   - Whenever you encounter an "Example", "Remark", "Proof", or "Exercise" in the text, you MUST NEVER create a new node for it.
   - You MUST attach its line interval to the PARENT concept that precedes it or that it illustrates by calling the appropriate sub-node function.
   * Example in text: Lines 100-110 are "Example A". This is an example of the concept "Concept B" (Definition). Call the function to attach lines 100-110 inside Concept B under the "Example" type.
   * Example in text: Lines 150-160 are "Example C". This is an example of "Theorem D". Call the function to attach lines 150-160 inside Theorem D under the "Example" type.

3. NON-CONTIGUOUS & DEFERRED SUB-ELEMENT AGGREGATION:
   - Sub-elements (Proofs, Examples, Remarks, Exercises) are sometimes located far away from their parent statement or interleaved with unrelated concepts.
   - BEFORE you move on to the next independent concept, you MUST actively scan the remainder of the document. Locate any deferred proofs, examples, or exercises belonging to the current concept and link their line numbers to it right now, even if they appear pages later.
   - Always bind each sub-element strictly to its true semantic parent, regardless of distance, page breaks, or intervening nodes.
   - Never default an interleaved sub-element to the nearest preceding concept; resolve the conceptual reference explicitly before assigning intervals.

4. EXHAUSTIVE PARTITION (NO OMISSIONS, NO OVERLAPS):
   - Every single line from line 1 to the end of the text must belong to at least one interval in the output.
   - For general text, table of contents, introduction sections, or summaries not attached to a single theorem/definition, use a "Contexte" node with a "Statement" sub-node.

5. ANTI-LAZINESS & NO MICRO-FRAGMENTATION (CRITICAL):
   - You MUST process the text line by line until the VERY LAST LINE of the document. Do NOT skip any sections, and do NOT summarize. Stopping early is strictly forbidden.
   - Do NOT fragment intervals unnecessarily. A block of text should be one continuous interval `[[start, end]]` unless explicitly interrupted by a new Theorem/Definition.

6. CORRECTION PHASE (HANDLING MISSING LINES):
   - If the `exhaustivity_check` tool reports that you missed some lines, DO NOT blindly create new "Contexte" or "Definition" nodes at the end of the document just to patch the holes. This breaks chronological order and logic.
   - You MUST evaluate if the missing lines belong to a concept you ALREADY created.
   - If they are examples, remarks, or exercises belonging to an existing concept, use the list of existing main nodes provided in the error message and call `add_sub_node` to attach the missing lines to the CORRECT EXISTING parent node.
   - ONLY create a new main node during the correction phase if the missing lines genuinely represent a completely forgotten primary concept.

OUTPUT INSTRUCTIONS (FUNCTION CALLING):
You must NOT output raw JSON text or markdown in your response. Instead, you MUST use the provided functions (tools) to construct the graph sequentially.

For EVERY primary concept you extract, you must execute the following sequence:
1. Call `add_main_node` to create the parent concept (using the strict "main" and "name" rules).
2. Call `add_sub_node` to attach ALL its aggregated sub-elements. When calling `add_sub_node`, you MUST use the exact types from the schema: ["Statement", "Proof", "Example", "Remark", "Exercise"]. Provide a logical "reason" explaining the extraction, and the precise "startEndListPositions".
Write 0 text, only call function.
You must call these functions multiple times in a row to process the entire document from line 1 to the end.
"""

print("🧠 Agent 1 en cours d'exécution (Squelette)...")
import json
from mistralai.client import Mistral

tools = [
    {
        "type": "function",
        "function": {
            "name": "add_main_node",
            "description": "add a main concept node in the graph from the exact labels list : [\"Theorem\",\"Proposition\",\"Property\",\"Corollary\",\"Lemma\",\"Definition\",\"Context\"], indexed with a 2-digit number",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                    "node"
                ],
                "properties": {
                    "node": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "main",
                                "first_line",
                                "name"
                            ],
                            "properties": {
                                "main": {
                                    "type": "string",
                                    "pattern": "^(Theorem|Proposition|Property|Corollary|Lemma|Definition|Context)_[0-9]{2}$"
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
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_sub_node",
            "description": "add a sub_node to a specified main_node of the graph.",
            "strict": True,
            "parameters": {
                "type": "object",
                "title": "Semantic extraction of concept sub-nodes",
                "required": [
                    "sub_nodes",
                    "parent_node"
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
                                        "Statement",
                                        "Proof",
                                        "Example",
                                        "Remark",
                                        "Exercise"
                                    ],
                                    "type": "string",
                                    "description": "Type of sub-node from the allowed values"
                                },
                                "reason": {
                                    "type": "string",
                                    "description": "Small justification explaining why these lines belong to the target concept"
                                },
                                "startEndListPositions": {
                                    "type": "array",
                                    "items": {
                                        "type": "array",
                                        "items": {
                                            "type": "integer"
                                        },
                                        "maxItems": 2,
                                        "minItems": 2
                                    },
                                    "description": "List of line intervals (start, end) for this sub-node type"
                                }
                            }
                        },
                        "minItems": 1,
                        "description": "List of sub-nodes extracted for the target concept"
                    },
                    "parent_node": {
                        "type": "string",
                        "pattern": "^(Theorem|Proposition|Property|Corolarry|Lemma|Definition|Context)_[0-9]{2}$",
                        "description": "Unique identifier of the parent node where the sub-node should be added"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_for_reference",
            "description": "send a reference to search for in the document, about blind mention of a figure an exercice or anything else",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                    "blind_reference"
                ],
                "properties": {
                    "blind_reference": {
                        "type": "string",
                        "description": "exact blind reference mentionned, to search it with regex tools"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_graph_main_nodes",
            "description": "return all the main nodes of the graph, to get a backbone visualisation if needed for exploration",
            "strict": True,
            "parameters": {}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_node_content",
            "description": "read all the content from a parent node, read all its sub_nodes, and text pieces",
            "strict": True,
            "parameters": {
                "type": "object",
                "required": [
                    "parent_node"
                ],
                "properties": {
                    "node_id": {
                        "type": "string",
                        "pattern": "^(Théorème|Proposition|Corollaire|Lemme|Définition|Contexte)_[0-9]{2}$",
                        "description": "Unique identifier of the parent node to read"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name" : "exhaustivity_check",
            "description": "when you're over with the current file processing, call this function, that will check if all the lines of the course have been processed into the graph",
            "strict": True,
            "parameters": {}
        }
    }
]

import json
import re
import networkx as nx
from mistralai.client import Mistral


def agent_builder_loop(markdown_lines_str, tools, sys_prompt, client):
    print("🤖 Démarrage de l'agent...")
    
    # 1. Initialisation du graphe et des variables
    G = nx.DiGraph()
    previous_main_node = None
    line_number_regex = re.compile(r"^\s*\d+[\s\|\:\.\-\)]\s*")

    # Variables globales pour le suivi de la complétude
    markdown_lines = markdown_lines_str.splitlines(keepends=True)
    total_lines_count = len(markdown_lines)
    all_lines = set(range(1, total_lines_count + 1))
    covered_lines = set()

    blank_lines = set()
    for i, line in enumerate(markdown_lines, 1):
        line_clean = line_number_regex.sub("", line).strip()
        if not line_clean:  # Si la ligne est totalement vide après nettoyage
            blank_lines.add(i)

    input = [{
                "role": "system",
                "content": sys_prompt
            },
            {
                "role": "user",
                "content": chunks[0]
            }
            ]
    # 2. La boucle infinie agentique
    while True:
        response = client.chat.complete(
            model="mistral-medium-latest",
            messages=input,
            tools=tools,
            temperature=0.0
        )
        
        assistant_message = response.choices[0].message
        print(assistant_message, end="\n===========================================================\n")
        input.append(assistant_message)
        
        if not assistant_message.tool_calls:
            print("✅ L'agent a terminé son travail de construction et de vérification !")
            break
            
        # 3. Traitement de CHAQUE appel de fonction demandé par l'agent
        for tool_call in assistant_message.tool_calls:
            nom_fonction = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            
            print(f"⚙️ L'agent utilise l'outil en live : {nom_fonction}")
            resultat_outil = ""
            
            # --- ROUTAGE DES OUTILS ---
            
            if nom_fonction == "add_main_node":
                nodes = arguments.get("node", [])
                for node_data in nodes:
                    main_id = node_data.get("main")
                    name = node_data.get("name")
                    first_line = node_data.get("first_line")

                    if name != "None":
                        label = f"{main_id} : {name}"
                    else:
                        label = f"{main_id}"
                    
                    G.add_node(main_id, label=label, is_main=True, first_line=first_line)
                    covered_lines.add(first_line) # On déclare cette ligne comme couverte
                    
                    if previous_main_node:
                        G.add_edge(previous_main_node, main_id, link="next_topic")
                    previous_main_node = main_id
                    
                resultat_outil = f"Succès : {len(nodes)} main node(s) ajouté(s)."
                print(f"   └── {resultat_outil}")

            elif nom_fonction == "add_sub_node":
                parent_node = arguments.get("parent_node")
                sub_nodes = arguments.get("sub_nodes", [])
                
                if not G.has_node(parent_node):
                    resultat_outil = f"Erreur : Le parent_node '{parent_node}' n'existe pas."
                else:
                    for sub in sub_nodes:
                        sub_type = sub.get("type")
                        reason = sub.get("reason")
                        positions = sub.get("startEndListPositions", [])
                        
                        for pos in positions:
                            sub_id = f"{parent_node}_{sub_type}_{pos[0]}_{pos[1]}"
                            G.add_node(sub_id, label=sub_type, reason=reason, pos=pos, is_main=False)
                            G.add_edge(parent_node, sub_id, link="link")
                            
                            # On ajoute la totalité de l'intervalle dans nos lignes couvertes
                            if len(pos) == 2:
                                covered_lines.update(range(pos[0], pos[1] + 1))
                                
                                
                    resultat_outil = f"Succès : {len(sub_nodes)} sous-noeud(s) rattaché(s) à {parent_node}."
                print(f"   └── {resultat_outil}")
                
            elif nom_fonction == "search_for_reference":
                blind_ref = arguments.get("blind_reference", "")
                print(f"   └── Recherche demandée par l'agent : {blind_ref}")
                
                matches = []
                try:
                    # Recherche insensible à la casse dans tout le document
                    pattern = re.compile(re.escape(blind_ref), re.IGNORECASE)
                    for i, line in enumerate(markdown_lines, 1):
                        if pattern.search(line):
                            matches.append(f"Ligne {i} : {line.strip()}")
                except Exception as e:
                    matches.append(f"Erreur regex : {str(e)}")

                if matches:
                    # On ne lui renvoie que les premières occurrences pour économiser son contexte
                    resultat_outil = f"Résultat(s) trouvé(s) pour '{blind_ref}' :\n" + "\n".join(matches[:10])
                    if len(matches) > 10:
                        resultat_outil += f"\n... et {len(matches)-10} autres occurrences."
                else:
                    resultat_outil = f"Aucun résultat trouvé pour la référence '{blind_ref}'."

            elif nom_fonction == "read_graph_main_nodes":
                main_nodes_info = [f"{n} (Ligne {d.get('first_line', '?')})" for n, d in G.nodes(data=True) if d.get("is_main")]
                resultat_outil = f"Voici les main_nodes actuels et leur ligne de départ : {main_nodes_info}"
                
            elif nom_fonction == "read_node_content":
                node_id = arguments.get("node_id") 
                if G.has_node(node_id):
                    sub_nodes = [v for u, v in G.out_edges(node_id) if G.nodes[v].get("is_main") is False]
                    resultat_outil = f"Contenu du noeud {node_id} : {G.nodes[node_id]}. Sous-noeuds attachés : {sub_nodes}"
                else:
                    resultat_outil = f"Erreur : Le noeud {node_id} n'est pas dans le graphe."

            elif nom_fonction == "exhaustivity_check":
                missing_lines = sorted(all_lines - covered_lines)
                
                print("\n" + "=" * 50)
                if not missing_lines:
                    resultat_outil = "Exhaustivity Check success : 100% du document est couvert."
                    print("✅ Intégralité respectée : 100% du Markdown a été retranscrit !")
                else:
                    taux = ((total_lines_count - len(missing_lines)) / total_lines_count) * 100
                    print(f"⚠️ Retranscription incomplète : {taux:.1f}% des lignes couvertes.")
                    print(f"❌ {len(missing_lines)} ligne(s) non retranscrite(s).\n")
                    
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

                    main_nodes_list = [n for n, d in G.nodes(data=True) if d.get('is_main')]
                    # Ce qu'on renvoie réellement à l'agent pour qu'il puisse réagir !
                    resultat_outil = (
                        f"Exhaustivity Check failed : Only {taux:.1f}% coverage. Missing {len(missing_lines)} lines out of {total_lines_count}. "
                        f"Here are the missing lines to fix: {missing_lines}"
                        f"Here are the main nodes already created in the graph if a concept should be inserted in one of these nodes "
                        f"(or sub_nodes of one parent_node, that you can reach with the 'read_node_content' function) : {main_nodes_list}"
                    )
                print("=" * 50 + "\n")

            else:
                resultat_outil = f"Erreur : Fonction '{nom_fonction}' non reconnue."

            # 4. On renvoie le résultat à Mistral en tant que "tool"
            inputs.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": nom_fonction,
                "content": json.dumps(resultat_outil)
            })
            
        print("🔄 Renvoi des résultats à Mistral pour la prochaine étape...")

    return G


G = agent_builder_loop(markdown_lines, tools, inputs, client)


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
.card mjx-container{
  max-width:100%;
  overflow-x:auto;
  overflow-y:hidden;
}
.card mjx-container[display="true"]{
  display:block;
  margin:14px 0;
  padding-bottom:2px; /* evite que la scrollbar colle au texte */
}
/* anciens rendus MathJax (v2) et rendu image legacy, par securite */
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
  generer_id_deterministe('Lebesgue'),
  'Lebesgue')

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