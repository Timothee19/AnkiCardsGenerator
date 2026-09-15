import base64
import json
import os
import re
import json_repair

from dotenv import load_dotenv
from mistralai.client import Mistral
from mistralai.client.models import JSONSchema, ResponseFormat


def encode_file(file_path):
    with open(file_path, "rb") as pdf_file:
        return base64.b64encode(pdf_file.read()).decode("utf-8")


import base64
import json
import os
import tkinter as tk
from tkinter import filedialog


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
        filetypes=[("Documents PDF", "*.pdf"), ("Tous les fichiers", "*.*")],
    )
    root.destroy()
    return g_file


def traiter_pdf_vers_markdown():

    cache_file = "ocr_cache.json"
    # ==========================================
    # 1. VÉRIFICATION DU CACHE
    # ==========================================
    if os.path.exists(cache_file):
        print("📁 Cache trouvé ! Chargement du Markdown et des images (OCR ignoré)...")
        with open(cache_file, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

        # On retourne directement les données sauvegardées
        return cache_data["markdown_file"], cache_data["media_files"], cache_data["cost"], image_annotation["annotation"]

    # ==========================================
    # 2. SI AUCUN CACHE, LANCEMENT DE L'OCR
    # ==========================================

    load_dotenv()  # reads variables from a .env file and sets them in os.environ

    api_key = os.environ["MISTRAL_API_KEY"]

    client = Mistral(api_key=api_key)

    file_path = select_file()
    base64_file = encode_file(file_path)

    ocr_response = client.ocr.process(
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{base64_file}",
        },
        model="mistral-ocr-latest",
        include_image_base64=True,
        bbox_annotation_format=ResponseFormat(
            type="json_schema",
            json_schema=JSONSchema(
                name="response_schema",
                schema_definition={
  "properties": {
    "image_type": {
      "description": "\"Type of image: 'diagram', 'graph', 'equation', 'photo', 'schema', 'table', 'screenshot', 'illustration'\"",
      "enum": [
        "diagram",
        "graph",
        "equation",
        "code_snippet",
        "photo",
        "schema",
        "table",
        "screenshot",
        "illustration",
        "logo",
        "decoration"
      ],
      "type": "string"
    },
    "pedagogical_role": {
      "description": "The educational purpose of the image within the context of an academic presentation. Use 'Core_Concept' for main theories, 'Example' for applied theories, 'Animation_Step' for intermediate/incomplete frames of a sequential visual process, and 'Noise' for elements without educational value",
      "enum": [
        "Core_Concept",
        "Example",
        "Animation_Step",
        "Noise"
      ],
      "type": "string"
    },
    "short_description": {
      "description": "A concise and factual description of the visual content. Focus on the pedagogical, technical, or structural elements depicted (e.g., 'A search tree showing nodes A, B, and C with the DFS path highlighted'). Keep it under 15 words.",
      "type": "string"
    }
  },
  "required": [
      "image_type",
      "pedagogical_role",
      "short_description"
  ],
  "type": "object"
},
                strict=True,
            ),
        ),
        extract_header=True,
        extract_footer=True,
        include_blocks=False,
    )

    print("Extraction et sauvegarde des images en cours...")

    processed_pages = ocr_response.usage_info.pages_processed
    cost = processed_pages / 1000 * 3.5

    media_files = []
    image_annotation = {}
    full_markdown = ""
    # Parcours des pages de la réponse OCR
    for page in ocr_response.pages:
        # On vérifie si des images sont attachées à cette page
        if hasattr(page, "images") and page.images:
            for img in page.images:
                b64_str = img.image_base64

                # Nettoyage de l'en-tête "data:..." si présent dans la chaîne retournée
                if b64_str.startswith("data:"):
                    b64_str = b64_str.split(",", 1)[1]

                # Utilisation de l'ID fourni par Mistral comme nom de fichier
                img_filename = img.id
                if not img_filename.endswith((".jpg", ".jpeg", ".png")):
                    img_filename += ".jpeg"

                annotation_dict = json_repair.loads(img.image_annotation)
                role = annotation_dict.get("pedagogical_role", "")
                description = annotation_dict.get("short_description", "")
                image_type = annotation_dict.get("image_type", "")

                image_annotation[img_filename] = [role, description, image_type]
                

                

                # 2. AJOUT À LA LISTE DES MÉDIAS POUR ANKI
                # Utilise le chemin absolu (recommandé pour éviter les bugs avec genanki)
                if image_annotation[img_filename][0] =="Noise":
                    print(f"Image {img_filename} non sauvegardé, car bruit")
                else:
                    # Sauvegarde physique de l'image (écriture binaire)
                    with open(img_filename, "wb") as f_img:
                        f_img.write(base64.b64decode(b64_str))
                    media_files.append(os.path.abspath(img_filename))
                    print(f"✅ Image sauvegardée localement : {img_filename}")

        # On ajoute le markdown de la page (le texte principal sans les en-têtes/pieds de page)
        if hasattr(page, "markdown") and page.markdown:
            full_markdown += page.markdown + "\n"

    # 3. Définition du nom du fichier de sortie
    output_filename = "markdownCourse.md"

    # 4 Nettoyage des images inutiles
    for img_id, annotation in image_annotation.items():
        if annotation[0] == "Noise":
            # On extrait uniquement "img-75" en retirant l'extension quelle qu'elle soit
            base_id = os.path.splitext(img_id)[0] 
            
            # Cette regex supprime : ![n'importe quoi](base_id + n'importe quelle extension) + le saut de ligne éventuel
            full_markdown = re.sub(rf'!\[.*?\]\({re.escape(base_id)}[^\)]*\)\n?', '', full_markdown)

    # 4. Écriture et sauvegarde dans le fichier local
    with open(output_filename, "w", encoding="utf-8") as md_file:
        md_file.write(full_markdown)

    print(
        f"✅ Le document Markdown a été sauvegardé avec succès sous le nom : {output_filename}"
    )

    # ==========================================
    # 3. CRÉATION DU CACHE POUR LA PROCHAINE FOIS
    # ==========================================
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(
            {"markdown_file": output_filename, "media_files": media_files, "cost": cost, "annotation": image_annotation},
            f,
            indent=4,
            ensure_ascii=False,
        )

    print("💾 Résultats enregistrés dans le cache (ocr_cache.json).")

    return output_filename, media_files, cost, image_annotation

def split_markdown_into_chunks(markdown_text, max_chunk_size=3000):
    lines = markdown_text.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        is_header = (
            line.startswith("# ") or line.startswith("## ") or line.startswith("### ")
        )

        if is_header and current_length > 1000:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = len(line)
        else:
            current_chunk.append(line)
            current_length += len(line) + 1

        if current_length > max_chunk_size and not line.strip():
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks


def semantic_split_with_ai(
    client, markdown_text, model="mistral-large-latest", retries=2
):
    
    lines = markdown_text.split("\n")
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    numbered_text = "\n".join(numbered_lines)
    cost = 0
    system_prompt = r"""
ROLE
You are a structural parser Agent. Your only job is to semantically split an academic course text (provided with line numbers) into logical "chunks" or "blocks".
Each chunk must be a coherent pedagogical unit that can later be fed completely to an Anki card generator.

RULES:
1. MAXIMUM AGGREGATION: A Theorem (or Proposition/Property), its associated Proof, and its direct Examples/Remarks form ONE INDIVISIBLE UNIT. You MUST group them together into ONE SINGLE CHUNK.
   - Example scenario: Line 10 is `## THEOREM 1`, Line 40 is `# EXAMPLE 1`, Line 70 is `# PROOF`, Line 120 is `# EXAMPLE 2`. You MUST create a SINGLE chunk starting at line 10 and ending at line 140 inclusive.
   - NEVER separate the formal statement of a Theorem from its Proof or its Examples. They MUST physically reside in the exact same chunk.
   - You only start a new chunk when shifting to a completely independent topic, a completely new Theorem, or a list of disconnected definitions.
2. A single chunk can contain multiple Definitions or minor properties if they are closely related.
3. Output a JSON array with the exact start and end line numbers for each chunk.
4. You must skip the Table of contents at the beginning of the document. The first chunk starts at the first line after the Table of contents, and the last chunk ends at the last line number.

OUTPUT FORMAT MUST BE STRICTLY JSON:
{
    "chunks": [
        {"start": 1, "end": 45, "reason": "Intro and early definitions"},
        {"start": 46, "end": 150, "reason": "Theorem 1 + Example 1 + Proof of Theorem 1"}
    ]
}

Ensure no lines are left out after skipping the Table of contents. The first chunk starts at first line after the Table of contents, the last chunk ends at the last line number.
"""

    for attempt in range(retries):
        try:
            print(
                f"   (Agent Splitter en cours d'analyse - Tentative {attempt+1}/{retries}...)"
            )
            response = client.chat.complete(
                model=model,
                temperature=0.0,
                response_format={
                    "type": "json_schema",
                    "json_schema":{
                        "description":"Semantic split of the course",
                        "name":"courseSplit",
                        "strict":True,
                        "schema":{                    
                            "title": "Academic Course Text Chunker Schema",
                            "description": "Schema for parsing academic course texts into pedagogical chunks for Anki card generation.",
                            "type": "object",
                            "properties": {
                                "chunks": {
                                "description": "Array of chunks representing coherent pedagogical units.",
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                    "start": {
                                        "description": "Starting line number of the chunk (inclusive).",
                                        "type": "integer",
                                        "minimum": 1
                                    },
                                    "end": {
                                        "description": "Ending line number of the chunk (inclusive).",
                                        "type": "integer",
                                        "minimum": 1
                                    },
                                    "reason": {
                                        "description": "Brief explanation of the chunk's content and why it was grouped.",
                                        "type": "string",
                                        "minLength": 1
                                    }
                                    },
                                    "required": [
                                    "start",
                                    "end",
                                    "reason"
                                    ],
                                    "additionalProperties": False
                                },
                                "minItems": 1
                                }
                            },
                            "required": [
                                "chunks"
                            ],
                            "additionalProperties": False
                            
                        }
                    }
                },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": numbered_text,
                    },
                ],
            )

            details = getattr(response.usage, "prompt_tokens_details", None)
            cached_tokens = getattr(details, "cached_tokens", 0) or 0

            cost += (
                (response.usage.prompt_tokens - cached_tokens) / 1e6 * 0.44
                + response.usage.completion_tokens / 1e6 * 1.3
                + cached_tokens / 1e6 * 0.044
            ) 

            json_strings = response.choices[0].message.content
            parsed_data = json_repair.loads(json_strings)

            if "chunks" in parsed_data:
                chunks = []
                i=0
                for chunk_info in parsed_data["chunks"]:
                    if not chunks :
                        start = max(0, int(chunk_info["start"]) - 1)
                        first_chunk = ("\n".join(lines[0:start]))
                    else:
                        start = end  # Start from the end of the previous chunk
                    end = min(len(lines), int(chunk_info["end"]))

                    if end > start:
                        chunks.append("\n".join(lines[start:end]))

                if chunks:
                    return cost, chunks, first_chunk
        except Exception as e:
            import time

            print(f"   Erreur Agent Splitter: {e}. Nouvel essai...")
            time.sleep(2)

    # Fallback
    print("   Fallback: utilisation du découpage heuristique statique.")
    first_chunk=""
    return cost, split_markdown_into_chunks(markdown_text), first_chunk
