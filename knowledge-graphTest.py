import networkx as nx
import pygraphviz as pgv
import pydot

labels_fr = ["Théorème", "Proposition", "Corollaire", "Lemme", "Définition", "Contexte"]
sub_labels_fr = ["Démonstration", "Exemple", "Remarque", "Exercice"]
labels_en = ["Theorem", "Proposition", "Corollary", "Lemma", "Definition", "Context"]
sub_labels_en = ["Proof", "Example", "Remark", "Exercise"]

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