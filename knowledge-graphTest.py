import networkx as nx
import pygraphviz as pgv
import pydot

labels_fr = ["Théorème", "Proposition", "Corollaire", "Lemme", "Définition", "Contexte"]
sub_labels_fr = ["Démonstration", "Exemple", "Remarque", "Exercice"]
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
#Création d'un dictionnaire qui contient {main_node:name} pour chaque noeud renvoyé
main_node = { node_info.get("main") : node_info.get("name") for node_info in mistral_output.get("node", []) }

def create_graph_from_mistral_output(main_node):
    G = nx.DiGraph()
    
    for key in main_node.keys():
        main = key
        print(main)
        node_name = f"{key} : {main_node[key]}" if main_node[key] is not None else key  # Use the name if available, otherwise use the main node

        G.add_node(main, label=node_name)
    
    return G

startEnd = mistral_output.get("node", [])[0].get("startEndListPositions", [])


#Prototype json sub_node output :
#for
"""
{
    "sub_node": [
        {
            "type": "Enoncé" | "Démonstration" | "Exemple" | "Remarque" | "Exercice" 
        }
    ]
}
"""

#Remarque : on pourra essayer de faire les deux requetes en un seul appel plutôt que de le séparer en deux si c'est possible.


#sub_node_info = {main_node:sub_node}
#Récupération des informations de Mistral pour la création du graphe (noeuds principaux):

def add_sub_nodes_to_graph(G, main_node, sub_nodes_info):
    for sub_node_info in sub_nodes_info:
        sub_node = sub_node_info["type"]
        node_id = f"{main_node}_{sub_node}"  # Unique ID for the sub-node
        
        G.add_node(node_id, label=sub_node)
        G.add_edge(main_node, node_id)  # Link the main node to its sub-node


# Prototype de prompt en une seule passe :
"""
{
    {
    "node": [
        {
            "main": "Théorème_XX" | "Proposition_XX" | "Definition_XX" | "Lemme_XX" | "Corrolaire_XX" | "Contexte_XX" ,
            "name" : "None" | "Insérer ici le nom du concept si il en possède un",
            "startEndListPositionsConcept": {"Enoncé" | "Démonstration" | "Exemple" | "Remarque" | "Exercice" : [[0, 28], [29,50], [75,115]], "Enoncé" | "Démonstration" | "Exemple" | "Remarque" | "Exercice" : [[0, 28], [29,50], [75,115]]}
        }
    ]
}
}
"""
#Création du graphe à partir de la sortie de Mistral en une seule passe :

def create_graph_from_mistral_output_single_pass(mistral_output):
    G = nx.DiGraph()
    
    for node_info in mistral_output.get("node", []):
        main_node = node_info.get("main")
        name = node_info.get("name")
        node_name = main_node +" : " + name if name else main_node # Use the name if available, otherwise use the main node

        G.add_node(main_node, label=node_name)
        
        start_end_positions = node_info.get("startEndListPositionsConcept", {})
        
        for sub_node_type, positions in start_end_positions.items():
            for position in positions:
                sub_node_id = f"{main_node}_{sub_node_type}_{position[0]}_{position[1]}"  # Unique ID for the sub-node
                G.add_node(sub_node_id, label=sub_node_type)
                G.add_edge(main_node, sub_node_id)  # Link the main node to its sub-node
    
    return G



# Création d'un main_node fictif pour tester la fonction create_graph_from_mistral_output

main_node_test = {
    "Théorème_01": "Théorème de Pythagore",
    "Proposition_01": None,
    "Definition_01": "Continuité uniforme",
}

testGraph = create_graph_from_mistral_output(main_node_test)

#Enregistrement du testGraph
#Affichage et enregistrement du graphe avec graphviz
A = nx.nx_agraph.to_agraph(testGraph)
A.draw('knowledge_graph.png', prog='dot')


#Test du mistral_output en une seule passe :

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

#Enregistrement du testGraph
#Affichage et enregistrement du graphe avec graphviz
A = nx.nx_agraph.to_agraph(testGraph_full)
A.draw('knowledge_graphFull.png', prog='dot')

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