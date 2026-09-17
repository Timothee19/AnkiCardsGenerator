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
from prompts import courseIdentifier, MathsCourse, ComputerScienceCourse, PhysicsCourse
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

        cost, chunks, first_chunk = semantic_split_with_ai(self.client, texte_numerote)

        self.cost += cost

        return chunks, first_chunk

    def courseIdentifier(self, chunks, first_chunk):
        agentTopic = courseIdentifier()
        response = self.client.chat.complete(
                                model="mistral-small-latest",
                                messages=[{
                                    "role": "system",
                                    "content": agentTopic.prompt
                                },
                                {
                                    "role": "user",
                                    "content": f"<course_content>\n{first_chunk}\n{chunks[0]}</course_content>"
                                }],
                                temperature=0.0,
                                response_format={
                                "type": "json_schema",
                                "json_schema": {
                                    "description": "Creation of the graph",
                                    "name": "graph_creation",
                                    "strict": True,
                                    "schema":agentTopic.json_schema
                                    }
                                }
                            )
                            
        json_string = response.choices[0].message.content
        details = getattr(response.usage, "prompt_tokens_details", None)
        cached_tokens = getattr(details, "cached_tokens", 0) or 0

        parsed_data = json_repair.loads(json_string)
        topic = parsed_data.get("courseTopic", [])
        if topic == "Maths":
            return MathsCourse
        elif topic == "Computer Science":
            return ComputerScienceCourse
        elif topic == "Physics":
            return PhysicsCourse
        else:
            while topic not in ["1", "2"]: # Ajoute "3" quand PhysicsCourse sera prêt
                topic = input("Veuillez entrer 1 (Maths) ou 2 (ComputerScience) : ")
                if topic == "1": return MathsCourse
                elif topic == "2": return ComputerScienceCourse

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

        for node_info in parsed_data.get("blocks", []):
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
            

    def etape_2_map_analyse_locale(self, chunks: List, topic = MathsCourse):
        """
        Envoie un SEUL chunk à Mistral pour extraire le graphe local.
        Effectue également le contrôle d'exhaustivité mathématique sur le retour.
        """
        main_nodes_for_code = []
        main_nodes_for_ai = []
        i = 0
        previous_node = None


        for chunk in chunks :

            if not chunk.strip():
                continue

            with open(log_file, "a", encoding="utf-8") as log_f:
                log_f.write(f"\n=== Analyse locale du chunk {i+1}/{len(chunks)} ===\n")
                log_f.write(f"Chunk content:\n{chunk}\n")
                log_f.write(f"=== FIN DU CHUNK ===\n")

            prompt = topic.parserIntoGraph(main_nodes_for_ai)
            graph_response_format = topic.json_schema_graph()
            response = self.client.chat.complete(
                        model="mistral-large-latest",
                        messages=[{
                            "role": "system",
                            "content": prompt
                        },
                        {
                            "role": "user",
                            "content": topic.userInputMainAgent(chunk)
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
            parsed_data = json_repair.loads(json_string)
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
                correction_prompt = topic.parserIntoGraphCorrector()
                response_correction = self.client.chat.complete(
                                    model="mistral-large-latest",
                                    messages=[{
                                        "role": "system",
                                        "content": correction_prompt
                                    },
                                    {
                                        "role": "user",
                                        "content": topic.userInputCorrectorAgent(chunk, parsed_data, missing_lines_num)
                                    }],
                                    temperature=0.0,
                                    response_format=graph_response_format
                                )
                # Evaluation du coup
                details = getattr(response_correction.usage, "prompt_tokens_details", None)
                cached_tokens = getattr(details, "cached_tokens", 0) or 0

                self.cost += (
                    (response_correction.usage.prompt_tokens - cached_tokens) / 1e6 * 0.44
                    + response_correction.usage.completion_tokens / 1e6 * 1.3
                    + cached_tokens / 1e6 * 0.044
                )                

                json_string = response_correction.choices[0].message.content
                parsed_data_correction = json_repair.loads(json_string)

                with open(log_file, "a", encoding="utf-8") as log_f:
                    log_f.write(f"\n=== Résultat de Mistral pour la correction du chunk {i+1}/{len(chunks)} ===\n")
                    log_f.write(f"{parsed_data_correction}\n")
                    log_f.write(f"=== FIN DU CHUNK ===\n")

                parsed_data["blocks"].extend(parsed_data_correction.get("blocks", []))
                exhaustive_parsing,  missing_lines_num, missing_lines = self.exhaustivity_check_into_chunk(chunk, parsed_data)
                
            # Sort data depending on the starting line of each block to maintain order
            parsed_data["blocks"].sort(key=lambda x: x["lines"][0])

            if parsed_data_correction is not None:
                with open(log_file, "a", encoding="utf-8") as log_f:
                    log_f.write(f"\n=== Résultat final après correction du chunk {i+1}/{len(chunks)} ===\n")
                    log_f.write(f"{parsed_data}\n")
                    log_f.write(f"=== FIN DU CHUNK ===\n")
            parsed_data_correction = None  # Reset for the next chunk

            for node_info in parsed_data.get("blocks", []):

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

    def extraire_blocks_pour_anki(self):
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
    
    def course_into_flashcards(self, front, back, image_annotation, topic = MathsCourse):
        """
        Appel à Mistral Small pour simplifier et transformer le contenu des cartes en flashcards.
        """

        # Capture uniquement ce qui est dans les parenthèses qui suivent ![...]
        # Le [^\s)]+ ignore un éventuel titre optionnel entre guillemets
        pattern = r"!\[.*?\]\((https?://[^\s)]+|[^\s)]+)"

        liens = re.findall(pattern, back)
        img_description = {}
        for lien in image_annotation.keys():
            if lien in liens :
                img_description[lien] = image_annotation[lien]
        print("\n\n===========\nImageDescriptionForThisCard:\n", img_description, end="\n=============\n\n")
        prompt = topic.ankiFormater()
        response = self.client.chat.complete(
                    model="mistral-small-latest",
                    messages=[{
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"""
                            <front>
                            {front}
                            </front>
                            <back>
                            {back}
                            </back>
                            <images_description>
                            {img_description}
                            </images_description>
"""
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
                                    "description": "The formatted answer"
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
    markdown_file, media_files, cost, image_annotation = traiter_pdf_vers_markdown()
    print("Coût de l'OCR : ", cost, end="\n")
    pipeline = AnkiPipeline(API_KEY, markdown_file, media_files)
    
    print("1. Découpage du document...")
    chunks, first_chunk = pipeline.markdown_into_chunk(markdown_file)
    print("Identification du sujet du cours...")
    topic = pipeline.courseIdentifier(chunks, first_chunk)
    print(f"2. Analyse locale de {len(chunks)} chunks via LLM...")
    graph = pipeline.etape_2_map_analyse_locale(chunks, topic)

    #Affichage et enregistrement du graphe avec graphviz
    A = nx.nx_agraph.to_agraph(graph)
    A.draw(f'{deck_name.replace("::", "_")}.png', prog='dot')

    print("3. Création de la liste de cartes pour Anki")
    concept_list = pipeline.extraire_blocks_pour_anki()

    print("Création du paquet Anki")
    my_deck = genanki.Deck(pipeline.generer_id_deterministe(deck_name), deck_name)

    # Récupération du dictionnaire des noms de decks
    deck_suffixes = topic.deck_suffixes()
    deck_dict = {}
    created_decks = {} # Cache pour éviter de recréer l'objet Deck "Properties" deux fois

    # 3. Boucle de création automatique
    for key, suffix in deck_suffixes.items():
        full_name = f"{deck_name}::{suffix}"
        
        # Si l'objet genanki.Deck pour ce suffixe n'existe pas encore, on le crée
        if suffix not in created_decks:
            deck_id = pipeline.generer_id_deterministe(full_name)
            created_decks[suffix] = genanki.Deck(deck_id, full_name)
            
        # On assigne l'objet Deck à la clé correspondante dans deck_dict
        deck_dict[key] = created_decks[suffix]

    j=0
    for card in concept_list:
        if card["main_id"].split("_")[0]=="Ignore" :
            print("Carte Ignore_00\n" + "\n".join([card["sub_nodes"][i]["text"] for i in range(len(card["sub_nodes"]))]) , end="\n")
        else:                
            
            front = card["label"]
            back = ""

            content_dict = {element: [] for element in topic.sub_element()}

            for i in range(len(card["sub_nodes"])):
                sub_type = card["sub_nodes"][i]["type"]
                text = card["sub_nodes"][i]["text"]
                
                if sub_type in content_dict.keys():
                    content_dict[sub_type].append(text)
                    
            # Construction propre et sécurisée du dos de la carte
            for element, texts in content_dict.items():
                if texts :
                    back += f"**{element}**\n" + "\n".join(texts) + "\n"

            
            if len(back) < 20:
                print("This card has a very short back content, skipping it to avoid empty cards.\n Front: {}\nBack: {}".format(front, back))
            else:
                front, back = pipeline.course_into_flashcards(front, back, image_annotation, topic)
                # Add examples, remarks and exercises in collapsible sections

                # 2. LA RUSTINE : On "aspire" les espaces aux bords et on force un double dollar propre
                back = re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', back, flags=re.DOTALL)
                front = re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', front, flags=re.DOTALL)
                # 3. CONVERSION MARKDOWN -> HTML (avec MathJax)
                front = pypandoc.convert_text(front, "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"])
                back = pypandoc.convert_text(back, "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"])
                
                #if example:
                #    back += f"<details><summary>Examples (click to expand)</summary>" + "\n".join([pypandoc.convert_text(re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', example[i], flags=re.DOTALL), "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"]) for i in range(len(example))]) + "</details><br>"

                #if remark:
                #    back += f"<details><summary>Remarks (click to expand)</summary>" + "\n".join([pypandoc.convert_text(re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', remark[i], flags=re.DOTALL), "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"]) for i in range(len(remark))]) + "</details><br>"
                #if exercice:
                #    back += f"<details><summary>Exercise {i + 1} (click to expand)</summary>" + "\n".join([pypandoc.convert_text(re.sub(r'\$\$+\s*(.*?)\s*\$\$+', r'$$\1$$', exercice[i], flags=re.DOTALL), "html", format="markdown+lists_without_preceding_blankline", extra_args=["--mathjax"]) for i in range(len(exercice))]) + "</details><br>"

                my_note = genanki.Note(
                    model=pipeline.model_basic,
                    fields=[front, back, str(j)],
                    due = j
                    )
                j += 1
                deck_dict[card["main_id"].split("_")[0]].add_note(my_note)

    my_package = genanki.Package([my_deck] + list(set(deck_dict.values())))
    my_package.media_files = media_files 
    my_package.write_to_file(f'{deck_name.replace("::","_")}.apkg')
    print("✅ Génération du paquet Anki terminée !")
    print(f"💰 Coût total estimé pour l'utilisation de Mistral : {pipeline.cost+cost:.4f} €")
    print("Terminé !")

if __name__ == "__main__":
    main()