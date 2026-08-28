import base64
import os
from mistralai.client import Mistral
from mistralai.client.models import ResponseFormat, JSONSchema
from dotenv import load_dotenv



def encode_file(file_path):
    with open(file_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode('utf-8')

import tkinter as tk
from tkinter import filedialog
import base64
import json
import os

# ==========================================
# 1. SÉLECTION DU FICHIER PDF
# ==========================================
def select_file():
    root = tk.Tk()
    root.title("Sélection du cours (PDF)")
    root.geometry("400x150")
    print("Veuillez sélectionner votre fichier PDF depuis la fenêtre...")
    
    g_file = filedialog.askopenfilename(
        title="Choisissez le PDF du cours",
        filetypes=[("Documents PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
    )
    root.destroy()
    return g_file

def traiter_pdf_vers_markdown():
    load_dotenv()  # reads variables from a .env file and sets them in os.environ

    api_key = os.environ["MISTRAL_API_KEY"]

    client = Mistral(api_key=api_key)

    file_path = select_file()
    base64_file = encode_file(file_path)

    ocr_response = client.ocr.process(
        document={
        "type": "document_url",
        "document_url": f"data:application/pdf;base64,{base64_file}"
        },
        model="mistral-ocr-latest",
        include_image_base64=True,
        bbox_annotation_format=ResponseFormat(
            type="json_schema",
            json_schema=JSONSchema(
                name="response_schema",
                schema_definition={
                    "properties": {
                        "caption": {
                            "description": "caption written below the image if it has one",
                            "type": "string"
                        },
                        "figure-index": {
                            "description": "if the figure has an index, for example \"figure 2.8\", you should write \"2.8\"",
                            "type": "string"
                        },
                        "image_type": {
                            "description": "\"Type of image: 'diagram', 'graph', 'equation', 'photo', 'schema', 'table', 'screenshot', 'illustration'\"",
                            "enum": [
                                "diagram",
                                "graph",
                                "equation",
                                "photo",
                                "schema",
                                "table",
                                "screenshot",
                                "illustration"
                            ],
                            "type": "string"
                        },
                        "key_concepts": {
                            "description": "Comma-separated list of key academic concepts/topics illustrated by this image.",
                            "type": "array"
                        }
                    },
                    "required": [],
                    "type": "object"
                },
                strict=True,
            ),
        ),
        extract_header=True,
        extract_footer=True,
        include_blocks=False
    )

    print("Extraction et sauvegarde des images en cours...")

    media_files=[]
    full_markdown=""
    # Parcours des pages de la réponse OCR
    for page in ocr_response.pages:
        # On vérifie si des images sont attachées à cette page
        if hasattr(page, 'images') and page.images:
            for img in page.images:
                b64_str = img.image_base64
                
                # Nettoyage de l'en-tête "data:..." si présent dans la chaîne retournée
                if b64_str.startswith("data:"):
                    b64_str = b64_str.split(",", 1)[1]
                
                # Utilisation de l'ID fourni par Mistral comme nom de fichier
                img_filename = img.id
                if not img_filename.endswith(('.jpg', '.jpeg', '.png')):
                    img_filename += ".jpg"
                    
                # Sauvegarde physique de l'image (écriture binaire)
                with open(img_filename, "wb") as f_img:
                    f_img.write(base64.b64decode(b64_str))
                
                # 2. AJOUT À LA LISTE DES MÉDIAS POUR ANKI
                # Utilise le chemin absolu (recommandé pour éviter les bugs avec genanki)
                media_files.append(os.path.abspath(img_filename))
                print(f"✅ Image sauvegardée localement : {img_filename}")

        # On ajoute le markdown de la page (le texte principal sans les en-têtes/pieds de page)
        if hasattr(page, 'markdown') and page.markdown:
            full_markdown += page.markdown + "\n"

    # 3. Définition du nom du fichier de sortie
    output_filename = "markdownCourse.md"

    # 4. Écriture et sauvegarde dans le fichier local
    with open(output_filename, "w", encoding="utf-8") as md_file:
        md_file.write(full_markdown)

    print(f"✅ Le document Markdown a été sauvegardé avec succès sous le nom : {output_filename}")


    return output_filename, media_files