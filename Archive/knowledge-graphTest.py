import os

import networkx as nx
import pydot
import pygraphviz as pgv

labels_fr = ["Théorème", "Proposition", "Corollaire", "Lemme", "Définition", "Contexte"]
sub_labels_fr = ["Enoncé", "Démonstration", "Exemple", "Remarque", "Exercice"]
labels_en = ["Theorem", "Proposition", "Corollary", "Lemma", "Definition", "Context"]
sub_labels_en = ["Proof", "Example", "Remark", "Exercise"]

"""
#Création d'un graphe vide
G = nx.DiGraph()

#Ajout des noeuds principaux au graphe
# Construction de la structure hiérarchique
for p in labels_fr:
    # Le parent est son propre identifiant et affiche son nom
    G.add_node(p, label=p)
    
    for s in sub_labels_fr:
        # Clé unique pour éviter la fusion des nœuds
        node_id = f"{p}_{s}"
        
        # Le sous-nœud a un ID unique mais affiche le texte générique
        G.add_node(node_id, label=s)
        
        # Création du lien du parent vers son instance d'enfant
        G.add_edge(p, node_id)

#Création d'un arrête non orientée entre les noeuds principaux
for i in range(len(labels_fr)-1):
    G.add_edge(labels_fr[i], labels_fr[i+1])

#Affichage et enregistrement du graphe avec graphviz
A = nx.nx_agraph.to_agraph(G)
A.draw('knowledge_graph.png', prog='dot')
"""
"""
#Prototype json node output : mistral_output
{
    "node": [
        {
            "main": "Théorème_XX" | "Proposition_XX" | "Definition_XX" | "Lemme_XX" | "Corrolaire_XX" | "Contexte_XX" ,
            "name" : "None" | "Insérer ici le nom du concept si il en possède un",
            "startEndListPositions": [[0, 28], [29,50], [75,115]]
        }
    ]
}
"""

# ==========================
# Numérotation du markdown
# ==========================

import os


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
    with open(input_path, "r", encoding="utf-8") as f:
        lignes = f.readlines()

    lignes_numerotees = []

    # enumerate(..., 1) permet de faire commencer le compteur à 1
    for i, ligne in enumerate(lignes, 1):
        # On retire le saut de ligne de fin pour construire notre chaîne proprement
        ligne_propre = ligne.rstrip("\n")
        lignes_numerotees.append(f"{i}: {ligne_propre}\n")

    # Écriture dans le nouveau fichier
    with open(output_path, "w", encoding="utf-8") as f:
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


numbered_markdown = numeroter_fichier_markdown(
    "C:/Users/a956068/Downloads/ocr-playground-download-20260817T215800Z/Lebesgue_integral_V2.pdf/markdown.md",
    "markown_numerote.md",
)

mistral_output = {
    "node": [
        {
            "main": "Théorème_01",
            "name": "Théorème de Pythagore",
            "startEndListPositions": [[0, 28], [29, 50], [75, 115]],
        },
        {
            "main": "Definition_01",
            "name": "None",
            "startEndListPositions": [[120, 150]],
        },
    ]
}
# Création d'un dictionnaire qui contient {main_node:name} pour chaque noeud renvoyé
main_node = {
    node_info.get("main"): node_info.get("name")
    for node_info in mistral_output.get("node", [])
}


def create_graph_from_mistral_output(main_node):
    G = nx.DiGraph()

    for key in main_node.keys():
        main = key
        print(main)
        node_name = (
            f"{key} : {main_node[key]}" if main_node[key] is not None else key
        )  # Use the name if available, otherwise use the main node

        G.add_node(main, label=node_name)

    return G


startEnd = mistral_output.get("node", [])[0].get("startEndListPositions", [])


# Prototype json sub_node output :
# for
"""
{
    "sub_node": [
        {
            "type": "Enoncé" | "Démonstration" | "Exemple" | "Remarque" | "Exercice" 
        }
    ]
}
"""

# Remarque : on pourra essayer de faire les deux requetes en un seul appel plutôt que de le séparer en deux si c'est possible.


# sub_node_info = {main_node:sub_node}
# Récupération des informations de Mistral pour la création du graphe (noeuds principaux):


def add_sub_nodes_to_graph(G, main_node, sub_nodes_info):
    for sub_node_info in sub_nodes_info:
        sub_node = sub_node_info["type"]
        node_id = f"{main_node}_{sub_node}"  # Unique ID for the sub-node

        G.add_node(node_id, label=sub_node)
        G.add_edge(main_node, node_id)  # Link the main node to its sub-node


# Prototype de prompt en une seule passe :
"""

    {
    "node": [
        {
            "main": "Théorème_XX" | "Proposition_XX" | "Definition_XX" | "Lemme_XX" | "Corrolaire_XX" | "Contexte_XX" ,
            "name" : "None" | "Insérer ici le nom du concept si il en possède un",
            "startEndListPositionsConcept": {"Enoncé" | "Démonstration" | "Exemple" | "Remarque" | "Exercice" : [[0, 28], [29,50], [75,115]], "Enoncé" | "Démonstration" | "Exemple" | "Remarque" | "Exercice" : [[0, 28], [29,50], [75,115]]}
        }
    ]
}

"""
# Création du graphe à partir de la sortie de Mistral en une seule passe :


def create_graph_from_mistral_output_single_pass(mistral_output):
    G = nx.DiGraph()
    i = 0
    for node_info in mistral_output.get("node", []):
        i += 1
        main_node = node_info.get("main")
        name = node_info.get("name")
        node_name = (
            main_node + " : " + name if name else main_node
        )  # Use the name if available, otherwise use the main node

        G.add_node(main_node, label=node_name)

        # Connexions entre les noeuds principaux

        if i >= 2:
            G.add_edge(previous_node, main_node, label=i - 1, link="next_topic")

        previous_node = main_node

        start_end_positions = node_info.get("startEndListPositionsConcept", {})

        for sub_node_type, positions in start_end_positions.items():
            for position in positions:
                sub_node_id = f"{main_node}_{sub_node_type}_{position[0]}_{position[1]}"  # Unique ID for the sub-node
                G.add_node(sub_node_id, label=sub_node_type, pos=position)
                G.add_edge(
                    main_node, sub_node_id, link="link"
                )  # Link the main node to its sub-node

    return G


# Création d'un main_node fictif pour tester la fonction create_graph_from_mistral_output

main_node_test = {
    "Théorème_01": "Théorème de Pythagore",
    "Proposition_01": None,
    "Definition_01": "Continuité uniforme",
}

testGraph = create_graph_from_mistral_output(main_node_test)

# Enregistrement du testGraph
# Affichage et enregistrement du graphe avec graphviz
A = nx.nx_agraph.to_agraph(testGraph)
A.draw("knowledge_graph.png", prog="dot")


# Test du mistral_output en une seule passe :

mistral_output_full = {
    "node": [
        {
            "main": "Théorème_01",
            "name": "Théorème de Bolzano-Weierstrass",
            "startEndListPositionsConcept": {
                "Enoncé": [[0, 45]],
                "Démonstration": [[46, 120], [125, 210]],
                "Exemple": [[215, 260]],
            },
        },
        {
            "main": "Definition_01",
            "name": None,
            "startEndListPositionsConcept": {
                "Enoncé": [[265, 310]],
                "Remarque": [[315, 350]],
            },
        },
        {
            "main": "Corrolaire_01",
            "name": None,
            "startEndListPositionsConcept": {
                "Enoncé": [[355, 390]],
                "Démonstration": [[391, 450]],
                "Exercice": [[455, 520]],
            },
        },
    ]
}

testGraph_full = create_graph_from_mistral_output_single_pass(mistral_output_full)

# Enregistrement du testGraph
# Affichage et enregistrement du graphe avec graphviz
A = nx.nx_agraph.to_agraph(testGraph_full)
A.draw("knowledge_graphFull.png", prog="dot")

"""
Pour le parcours du texte :
On envoie tout le texte d'un coup à mistral, et il me renvoie dans un json, le noeud principal et une liste de liste 
contenant l'ensemble des sections associées à ce noeud.
Ensuite, pour chaque noeud et liste de liste, je demande à mistral small de les mettre dans des sous noeuds (toujours avec 
l'indexation des lignes, en lui renvoyant la section mentionnée par mistral large, et les lignes toujours numérotées).
Ainsi, en récupérant les infos de mistral small, et les lignes correspondantes dans le texte source, je peux créer les noeuds et 
ses sous noeuds associés.
Pour la répartition dans les decks et sub_decks, il suffira de récupérer le label du noeud en cours de traitement
pour pouvoir identifier dans quel sub_deck l'insérer :
Sub_deck 1 : Théorème, Proposition, Corollaire, Lemme
Sub_deck 2 : Définition, Contexte

Pour le stockage des graphes : 
Dans la section bibliothèque de l'application, plutôt que de renvoyer vers le dossier contenant tout les éléments, on 
pourrais essayer de renvoyer vers une visualisation graphe, que l'utilisateur pourrait parcourir, et qui contiendrait tout les
éléments du texte source, ainsi que les images, visualisables dans le graphe, et les liens entre les noeuds principaux, et 
les sous noeuds avec leur noeud parent.
"""


# Test en conditions réelles

mistral_real_output = {
    "node": [
        {
            "main": "Contexte_01",
            "name": "Lebesgue Integration Course Overview",
            "startEndListPositionsConcept": {
                "Enoncé": [[1, 11], [41, 42], [86, 88], [111, 114], [133, 134]]
            },
        },
        {
            "main": "Contexte_02",
            "name": "Chapter 2: Lebesgue Integral Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[115, 122]]},
        },
        {
            "main": "Contexte_03",
            "name": "Motivations and limitations of the Riemann integral",
            "startEndListPositionsConcept": {"Enoncé": [[123, 192]]},
        },
        {
            "main": "Definition_01",
            "name": "σ-Algebras",
            "startEndListPositionsConcept": {
                "Enoncé": [[198, 206]],
                "Exemple": [[212, 218]],
            },
        },
        {
            "main": "Definition_02",
            "name": "Borel σ-algebra on ℝⁿ",
            "startEndListPositionsConcept": {"Enoncé": [[220, 220]]},
        },
        {
            "main": "Definition_03",
            "name": "Borel σ-algebra on an open set Ω ⊂ ℝⁿ",
            "startEndListPositionsConcept": {"Enoncé": [[222, 229]]},
        },
        {
            "main": "Definition_04",
            "name": "Measures",
            "startEndListPositionsConcept": {
                "Enoncé": [[232, 240]],
                "Exemple": [[242, 273], [275, 288], [290, 310]],
            },
        },
        {
            "main": "Definition_05",
            "name": "Measurable space",
            "startEndListPositionsConcept": {"Enoncé": [[312, 315]]},
        },
        {
            "main": "Definition_06",
            "name": "Measured Spaces",
            "startEndListPositionsConcept": {
                "Enoncé": [[323, 329]],
                "Remarque": [[331, 331]],
            },
        },
        {
            "main": "Contexte_04",
            "name": "Key ideas to remember about Measure and σ-Algebras",
            "startEndListPositionsConcept": {"Enoncé": [[333, 339]]},
        },
        {
            "main": "Contexte_05",
            "name": "Measurable Functions Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[341, 343]]},
        },
        {
            "main": "Definition_07",
            "name": "Measurable Functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[347, 353]],
                "Remarque": [[355, 355]],
                "Exemple": [[363, 380], [384, 390]],
            },
        },
        {
            "main": "Théorème_01",
            "name": "Stability under Composition",
            "startEndListPositionsConcept": {
                "Enoncé": [[396, 396]],
                "Démonstration": [[398, 404]],
            },
        },
        {
            "main": "Proposition_01",
            "name": "Stability under elementary operations",
            "startEndListPositionsConcept": {
                "Enoncé": [[406, 416]],
                "Démonstration": [[418, 462]],
            },
        },
        {
            "main": "Théorème_02",
            "name": "Stability of limit operations",
            "startEndListPositionsConcept": {
                "Enoncé": [[468, 474]],
                "Démonstration": [[476, 516]],
            },
        },
        {
            "main": "Definition_08",
            "name": "Negligible set",
            "startEndListPositionsConcept": {
                "Enoncé": [[524, 530]],
                "Exemple": [[532, 576]],
            },
        },
        {
            "main": "Definition_09",
            "name": "Property holding almost everywhere",
            "startEndListPositionsConcept": {
                "Enoncé": [[578, 584]],
                "Exemple": [[590, 594]],
            },
        },
        {
            "main": "Proposition_02",
            "name": "Measurability of functions continuous almost everywhere",
            "startEndListPositionsConcept": {
                "Enoncé": [[598, 598]],
                "Démonstration": [[600, 614]],
            },
        },
        {
            "main": "Contexte_06",
            "name": "Why is measurability important?",
            "startEndListPositionsConcept": {"Enoncé": [[616, 619]]},
        },
        {
            "main": "Contexte_07",
            "name": "Integral for the Dirac and counting measures",
            "startEndListPositionsConcept": {
                "Enoncé": [[620, 636]],
                "Exemple": [[638, 640]],
            },
        },
        {
            "main": "Contexte_08",
            "name": "Integral of simple functions Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[642, 644]]},
        },
        {
            "main": "Definition_10",
            "name": "Simple functions",
            "startEndListPositionsConcept": {"Enoncé": [[648, 662]]},
        },
        {
            "main": "Definition_11",
            "name": "Integral of a simple function",
            "startEndListPositionsConcept": {"Enoncé": [[670, 674], [676, 676]]},
        },
        {
            "main": "Contexte_09",
            "name": "Simple example of integral of simple function",
            "startEndListPositionsConcept": {"Enoncé": [[678, 696]]},
        },
        {
            "main": "Proposition_03",
            "name": "Linearity of the integral of simple functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[700, 703], [706, 712]],
                "Démonstration": [[714, 738]],
            },
        },
        {
            "main": "Proposition_04",
            "name": "Monotonicity of the integral of simple functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[740, 742], [744, 744]],
                "Démonstration": [[746, 752]],
            },
        },
        {
            "main": "Proposition_05",
            "name": "Integral over a negligible set for simple functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[754, 756]],
                "Démonstration": [[758, 774]],
            },
        },
        {
            "main": "Proposition_06",
            "name": "Integral zero implies function zero almost everywhere for simple functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[776, 780]],
                "Démonstration": [[786, 790]],
            },
        },
        {
            "main": "Contexte_10",
            "name": "Why start with simple functions?",
            "startEndListPositionsConcept": {"Enoncé": [[792, 796]]},
        },
        {
            "main": "Contexte_11",
            "name": "Definition of the Lebesgue integral for a non-negative measurable function Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[798, 799]]},
        },
        {
            "main": "Definition_12",
            "name": "Non-negative measurable functions",
            "startEndListPositionsConcept": {"Enoncé": [[802, 805]]},
        },
        {
            "main": "Contexte_12",
            "name": "Approximation by simple functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[808, 812], [814, 822], [824, 830]]
            },
        },
        {
            "main": "Proposition_07",
            "name": "Equivalence of simple function approximation formula",
            "startEndListPositionsConcept": {
                "Enoncé": [[834, 836]],
                "Démonstration": [[838, 876]],
            },
        },
        {
            "main": "Théorème_03",
            "name": "Density of simple functions in C(K)",
            "startEndListPositionsConcept": {"Enoncé": [[878, 882], [884, 884]]},
        },
        {
            "main": "Definition_13",
            "name": "Lebesgue integral of a non-negative function",
            "startEndListPositionsConcept": {"Enoncé": [[888, 896], [898, 898]]},
        },
        {
            "main": "Contexte_13",
            "name": "Example of Lebesgue integral of a non-negative function",
            "startEndListPositionsConcept": {"Enoncé": [[900, 908]]},
        },
        {
            "main": "Proposition_08",
            "name": "Linearity of the Lebesgue integral for non-negative functions",
            "startEndListPositionsConcept": {"Enoncé": [[916, 920]]},
        },
        {
            "main": "Proposition_09",
            "name": "Monotonicity of the Lebesgue integral for non-negative functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[922, 926]],
                "Démonstration": [[928, 928]],
            },
        },
        {
            "main": "Proposition_10",
            "name": "Integral over a null set for non-negative functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[930, 934]],
                "Démonstration": [[936, 954]],
            },
        },
        {
            "main": "Proposition_11",
            "name": "Integral zero implies function zero almost everywhere for non-negative functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[956, 962]],
                "Démonstration": [[964, 984]],
            },
        },
        {
            "main": "Contexte_14",
            "name": "Summary of Lebesgue integral for non-negative functions",
            "startEndListPositionsConcept": {"Enoncé": [[986, 990]]},
        },
        {
            "main": "Contexte_15",
            "name": "Integral of General Functions Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[992, 996]]},
        },
        {
            "main": "Definition_14",
            "name": "Positive Part and Negative Part",
            "startEndListPositionsConcept": {
                "Enoncé": [[1000, 1008]],
                "Remarque": [[1010, 1010]],
            },
        },
        {
            "main": "Definition_15",
            "name": "Lebesgue Integral of a Real Function",
            "startEndListPositionsConcept": {
                "Enoncé": [[1018, 1022]],
                "Remarque": [[1023, 1023]],
            },
        },
        {
            "main": "Théorème_04",
            "name": "Characterization of Integrable Functions",
            "startEndListPositionsConcept": {"Enoncé": [[1024, 1028]]},
        },
        {
            "main": "Contexte_16",
            "name": "Examples of Integrable and Non-Integrable Functions",
            "startEndListPositionsConcept": {"Enoncé": [[1030, 1045], [1047, 1047]]},
        },
        {
            "main": "Contexte_17",
            "name": "Fundamental Properties of the Lebesgue Integral Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[1049, 1051]]},
        },
        {
            "main": "Proposition_12",
            "name": "Linearity of the Lebesgue Integral",
            "startEndListPositionsConcept": {"Enoncé": [[1059, 1063]]},
        },
        {
            "main": "Proposition_13",
            "name": "Monotonicity of the Lebesgue Integral",
            "startEndListPositionsConcept": {"Enoncé": [[1067, 1071]]},
        },
        {
            "main": "Théorème_05",
            "name": "Monotone Convergence Theorem (Beppo-Levi)",
            "startEndListPositionsConcept": {
                "Enoncé": [[1073, 1082]],
                "Démonstration": [[1084, 1118]],
                "Exemple": [[1126, 1134]],
            },
        },
        {
            "main": "Proposition_14",
            "name": "Integral over a negligible set for integrable functions",
            "startEndListPositionsConcept": {
                "Enoncé": [[1138, 1140]],
                "Démonstration": [[1142, 1156]],
                "Remarque": [[1158, 1159]],
            },
        },
        {
            "main": "Lemme_01",
            "name": "Fatou's Lemma",
            "startEndListPositionsConcept": {
                "Enoncé": [[1162, 1164]],
                "Démonstration": [[1170, 1182], [1184, 1196]],
            },
        },
        {
            "main": "Théorème_06",
            "name": "Lebesgue's Dominated Convergence Theorem",
            "startEndListPositionsConcept": {
                "Enoncé": [[1200, 1207]],
                "Démonstration": [[1209, 1247]],
                "Remarque": [[1249, 1249], [1251, 1261]],
            },
        },
        {
            "main": "Contexte_18",
            "name": "Examples and Counter examples Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[1267, 1269]]},
        },
        {
            "main": "Contexte_19",
            "name": "Lp(Ω) Space Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[1332, 1334]]},
        },
        {
            "main": "Definition_16",
            "name": "Lp Spaces",
            "startEndListPositionsConcept": {"Enoncé": [[1338, 1350]]},
        },
        {
            "main": "Proposition_15",
            "name": "Seminorm property of Lp norms",
            "startEndListPositionsConcept": {
                "Enoncé": [[1351, 1351]],
                "Démonstration": [[1353, 1353]],
            },
        },
        {
            "main": "Contexte_20",
            "name": "Quotient by Equality Almost Everywhere",
            "startEndListPositionsConcept": {"Enoncé": [[1359, 1363]]},
        },
        {
            "main": "Théorème_07",
            "name": "Riesz–Fischer Theorem",
            "startEndListPositionsConcept": {
                "Enoncé": [[1365, 1365]],
                "Démonstration": [[1366, 1367]],
                "Remarque": [[1369, 1371]],
            },
        },
        {
            "main": "Contexte_21",
            "name": "Fundamental Inequalities Introduction",
            "startEndListPositionsConcept": {"Enoncé": [[1383, 1383]]},
        },
        {
            "main": "Proposition_16",
            "name": "Minkowski's Inequality",
            "startEndListPositionsConcept": {
                "Enoncé": [[1387, 1390]],
                "Démonstration": [[1393, 1393]],
            },
        },
        {
            "main": "Proposition_17",
            "name": "Hölder's Inequality",
            "startEndListPositionsConcept": {"Enoncé": [[1397, 1400]]},
        },
        {
            "main": "Lemme_02",
            "name": "Young's Inequality",
            "startEndListPositionsConcept": {
                "Enoncé": [[1405, 1411]],
                "Démonstration": [[1417, 1421]],
            },
        },
        {
            "main": "Proposition_18",
            "name": "Inclusion Property of Lp Spaces",
            "startEndListPositionsConcept": {
                "Enoncé": [[1437, 1438]],
                "Démonstration": [[1441, 1447]],
            },
        },
        {
            "main": "Théorème_08",
            "name": "Interpolation Theorem",
            "startEndListPositionsConcept": {"Enoncé": [[1451, 1453]]},
        },
    ]
}

realGraph = create_graph_from_mistral_output_single_pass(mistral_real_output)

# Enregistrement du graphe

A = nx.nx_agraph.to_agraph(realGraph)
A.draw("graphLebesgueExtract.png", prog="dot")

"""
json_schema : {
  "type": "object",
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
            "minProperties": 1,
            "additionalProperties": false,
            "properties": {
              "Enoncé": {
                "type": "array",
                "items": {
                  "type": "array",
                  "minItems": 2,
                  "maxItems": 2,
                  "items": {
                    "type": "integer"
                  }
                }
              },
              "Démonstration": {
                "type": "array",
                "items": {
                  "type": "array",
                  "minItems": 2,
                  "maxItems": 2,
                  "items": {
                    "type": "integer"
                  }
                }
              },
              "Exemple": {
                "type": "array",
                "items": {
                  "type": "array",
                  "minItems": 2,
                  "maxItems": 2,
                  "items": {
                    "type": "integer"
                  }
                }
              },
              "Remarque": {
                "type": "array",
                "items": {
                  "type": "array",
                  "minItems": 2,
                  "maxItems": 2,
                  "items": {
                    "type": "integer"
                  }
                }
              },
              "Exercice": {
                "type": "array",
                "items": {
                  "type": "array",
                  "minItems": 2,
                  "maxItems": 2,
                  "items": {
                    "type": "integer"
                  }
                }
              }
            }
          }
        }
      },
      "required": [
        "main",
        "startEndListPositionsConcept"
      ]
    }
  },
  "required": [
    "nodes"
  ]
}"""


# ========================================
# Suite du Pipeline : Création des cartes
# ========================================

"""
Niveau intermédiaire :
si name -> front = name, back = énoncé + démonstration (si démonstration) + remarques + exmples

Niveau zéro lecture : 
Niveau intermédiaire + création de questions supplémentaires par navigation du graphe (function calling ou json output), soit tout dans un stream, soit appelle un nouvel agent
    - Le mieux serait peut être d'avoir une seule conv avec du function calling (se documenter), ou json_output, et donc, à chaque json output, il y a une variable qui permet
    de savoir si l'agent a fini ou pas
Niveau minimal :
    - On envoie les noeuds un par un, et l'agent synthétise chaque noeud en une seule carte, pas d'exemples, pas d'exercices.
"""


# Parcours du graphe
def parcourir_graphe_cours(G: nx.DiGraph, start_node: str = None):
    # 1. Trouver le premier nœud principal si non spécifié
    # (le nœud principal qui n'a pas d'arête entrante 'next_topic')
    if start_node is None:
        for node in G.nodes():
            in_links = [data.get("link") for _, _, data in G.in_edges(node, data=True)]
            # Si aucune arête entrante n'est un 'next_topic', c'est la racine
            if "next_topic" not in in_links and any(
                data.get("link") == "next_topic"
                for _, _, data in G.out_edges(node, data=True)
            ):
                start_node = node
                break
        # Cas limite si le graphe n'a qu'un seul nœud principal
        if start_node is None and len(G) > 0:
            start_node = next(iter(G.nodes()))

    current_main = start_node

    # 2. Itération le long de la dorsale
    while current_main is not None:
        main_label = G.nodes[current_main].get("label", current_main)
        print(f"\n==========================================")
        print(f"📖 NŒUD PRINCIPAL : {main_label}")
        print(f"==========================================")

        next_main_node = None

        # 3. Exploration des voisins sortants
        for _, target, edge_data in G.out_edges(current_main, data=True):
            relation_type = edge_data.get("link")

            if relation_type == "link":
                # C'est un sous-nœud rattaché
                sub_label = G.nodes[target].get("label", "Sous-élément")
                print(f"  ├── [{sub_label}] ID: {target}")

            elif relation_type == "next_topic":
                # C'est le nœud principal suivant sur la chaîne
                next_main_node = target

        # 4. Passage au nœud principal suivant
        current_main = next_main_node


parcourir_graphe_cours(realGraph)

import re


def extraire_blocs_pour_anki(
    G: nx.DiGraph, markdown_source: str, start_node: str = None
):
    # 1. Charger les lignes brutes du Markdown
    if os.path.exists(markdown_source):
        with open(markdown_source, "r", encoding="utf-8") as f:
            markdown_lines = f.readlines()
    else:
        markdown_lines = markdown_source.splitlines(keepends=True)

    # Expression régulière pour matcher les préfixes de type "1291: ", "1291 | ", etc.
    line_number_regex = re.compile(r"^\s*\d+[\s\|\:\.\-\)]\s*")

    # 2. Trouver la racine (nœud principal sans prédécesseur 'next_topic')
    if start_node is None:
        for node in G.nodes():
            in_links = [data.get("link") for _, _, data in G.in_edges(node, data=True)]
            if "next_topic" not in in_links and any(
                data.get("link") == "next_topic"
                for _, _, data in G.out_edges(node, data=True)
            ):
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
            "sub_nodes": [],
        }

        next_main = None

        for _, neighbor, edge_data in G.out_edges(current_main, data=True):
            if edge_data.get("link") == "link":
                pos = G.nodes[neighbor].get("pos")
                extracted_text = ""

                if pos and len(pos) == 2:
                    start_line, end_line = pos[0], pos[1]
                    # Conversion en index 0-based
                    idx_start = max(0, start_line - 1)
                    idx_end = min(len(markdown_lines), end_line)

                    # Découpage puis suppression du préfixe numérique sur chaque ligne
                    raw_slice = markdown_lines[idx_start:idx_end]
                    cleaned_lines = [
                        line_number_regex.sub("", line) for line in raw_slice
                    ]
                    extracted_text = "".join(cleaned_lines).strip()

                main_data["sub_nodes"].append(
                    {
                        "sub_id": neighbor,
                        "type": G.nodes[neighbor].get("label"),
                        "text": extracted_text,
                    }
                )

            elif edge_data.get("link") == "next_topic":
                next_main = neighbor

        concepts_list.append(main_data)
        current_main = next_main

    return concepts_list


anki_source = extraire_blocs_pour_anki(realGraph, "markown_numerote.md")
import json

# Affiche le dictionnaire formaté sur plusieurs lignes avec encodage UTF-8 respecté
print(json.dumps(anki_source, indent=4, ensure_ascii=False))


import re

import markdown


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
    text = re.sub(r"\\+\[(.*?)(?:\\+\]|\Z)", protect_block, text, flags=re.DOTALL)
    text = re.sub(r"\$\$(.*?)(?:\$\$|\Z)", protect_block, text, flags=re.DOTALL)

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

    text = re.sub(r"\\+\((.*?)\\+\)", protect_inline, text, flags=re.DOTALL)
    text = re.sub(r"(?<!\\)\$([^\$\n]+?)(?<!\\)\$", protect_inline, text)

    # ==========================================
    # 3. CONVERSION MARKDOWN -> HTML
    # ==========================================
    html_output = markdown.markdown(
        text,
        extensions=[
            "markdown.extensions.tables",
            "markdown.extensions.nl2br",  # Conserve les sauts de ligne simples
        ],
        output_format="html5",
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
    print(card["label"])
    for i in range(len(card["sub_nodes"])):
        if card["sub_nodes"][i]["type"] == "Enoncé":
            enonce.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Démonstration":
            proof.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Remarque":
            remark.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
        elif card["sub_nodes"][i]["type"] == "Exemple":
            example.append(markdown_to_anki_html(card["sub_nodes"][i]["text"]))
    print(enonce[0] + "\n")
    if len(proof) >= 1:
        print(proof[0] + "\n")
    if len(remark) >= 1:
        print("\n".join(remark))
    if len(example) >= 1:
        print("\n".join(example))

# ========================================
# Création d'un paquet Anki intermédiaire
# ========================================
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
  border-radius:22px;
  box-shadow:0 22px 46px rgba(46,42,36,.20), 0 2px 6px rgba(46,42,36,.10), inset 0 1px 0 rgba(255,255,255,.9);
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
  background:linear-gradient(160deg, #ffffff 0%, var(--accent-soft) 100%);
  padding:4px 12px;
  border-radius:999px;
  box-shadow:0 4px 10px rgba(79,125,92,.28), inset 0 1px 0 rgba(255,255,255,.9), inset 0 -2px 3px rgba(60,96,71,.10);
  white-space:nowrap;
}

/* cloze : relief marque, forme V1 conservee */
.cloze{
  font-weight:600;
  color:var(--accent2-dark);
  background:linear-gradient(160deg, #ffffff 0%, var(--accent2-soft) 100%);
  padding:1px 7px;
  border-radius:5px;
  box-shadow:0 3px 7px rgba(193,105,79,.25), inset 0 1px 0 rgba(255,255,255,.9);
}

/* images */
img{
  max-width:100%;
  height:auto;
  display:block;
  margin:16px auto;
  border-radius:26px 8px 26px 8px;
  box-shadow:0 16px 32px rgba(46,42,36,.22);
}

/* code */
code{
  font-family:"JetBrains Mono","Fira Code",Consolas,monospace;
  font-size:.85em;
  background:linear-gradient(160deg, #ffffff 0%, var(--code-bg) 100%);
  color:var(--code-ink);
  padding:2px 7px;
  border-radius:8px 3px 8px 3px;
  box-shadow:0 2px 5px rgba(46,42,36,.12), inset 0 1px 0 rgba(255,255,255,.8);
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
  box-shadow:0 16px 34px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.08);
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
  box-shadow:0 10px 22px rgba(46,42,36,.14);
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
    "Basique (Claude)",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Sequence"}],
    sort_field_index=2,
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="note">{{Front}}</div>',
            "afmt": '<div class="note">{{Front}}</div>'
            '<div class="divider"><span>Reponse</span></div>'
            '<div class="note answer">{{Back}}</div>',
        },
    ],
    css=CSS,
)

my_deck = genanki.Deck(2059400110, "LebesgueTest")

j = 0
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
    back += enonce[0] + "<br><br>"
    if len(proof) >= 1:
        back += proof[0] + "<br><br>"
    if len(remark) >= 1:
        back += "<br><br>".join(remark)
    if len(example) >= 1:
        back += "<br><br>".join(example)
    my_note = genanki.Note(model=model_basic, fields=[front, back, str(j)])
    j += 1
    my_deck.add_note(my_note)

genanki.Package(my_deck).write_to_file("TestLebesgue.apkg")
