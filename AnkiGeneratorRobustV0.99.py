import tkinter as tk
from tkinter import filedialog
import time
import os
import json
import random
import re
import threading
import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed

FILE_LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()

_original_print = print
def safe_print(*args, **kwargs):
    with PRINT_LOCK:
        _original_print(*args, **kwargs)
print = safe_print

_original_open = open
@contextlib.contextmanager
def safe_open(file, mode='r', **kwargs):
    if file == "pipeline_logs.md" and "a" in mode:
        with FILE_LOCK:
            with _original_open(file, mode, **kwargs) as f:
                yield f
    else:
        with _original_open(file, mode, **kwargs) as f:
            yield f
open = safe_open

try:
    from pydantic import BaseModel, Field
except ImportError:
    print("Veuillez installer le package pydantic : pip install pydantic")
    exit(1)

try:
    import genanki
except ImportError:
    print("Veuillez installer le package genanki : pip install genanki")
    exit(1)

# Chargement automatique du fichier .env
if os.path.exists(".env"):
    with open(".env", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip().strip("\"'")

try:
    from mistralai import Mistral
    from mistralai.extra import response_format_from_pydantic_model
except ImportError:
    print("Veuillez installer le package mistralai : pip install mistralai")
    exit(1)

# ==========================================
# MODÈLE D'ANNOTATION D'IMAGES (OCR)
# ==========================================

class ImageAnnotation(BaseModel):
    image_type: str = Field(..., description="Type of image: 'diagram', 'graph', 'equation', 'photo', 'schema', 'table', 'screenshot', 'illustration'")
    short_description: str = Field(..., description="A concise description of what the image shows, in the same language as the document.")
    key_concepts: str = Field(..., description="Comma-separated list of key academic concepts/topics illustrated by this image.")

# ==========================================
# FIX JSON ESCAPE POUR LES RÉPONSES LLM
# ==========================================

def fix_llm_json_escaping(raw_content):
    r"""Corrige les sequences d'echappement JSON invalides dans les reponses LLM.
    Approche : scanner caractere par caractere pour doubler les backslashes.
    Inclut un "Latex JSON Shield" pour proteger \text, \frac, \nu, \rho, etc.
    """
    VALID_JSON_ESCAPES = set('"\\/bfnrtu')
    # Les commandes LaTeX qui commencent par une lettre d'echappement JSON valide
    LATEX_KEYWORDS = {
        't': ['ext', 'heta', 'au', 'an', 'imes'],
        'f': ['rac'],
        'n': ['u', 'abla', 'e'],
        'r': ['ho', 'ight'],
        'b': ['eta', 'egin', 'oldsymbol']
    }
    
    result = []
    i = 0
    in_string = False
    while i < len(raw_content):
        ch = raw_content[i]
        if ch == '"' and (i == 0 or raw_content[i-1] != '\\'):
            in_string = not in_string
            result.append(ch)
            i += 1
        elif ch == '\\' and in_string:
            if i + 1 < len(raw_content):
                next_ch = raw_content[i + 1]
                
                # Verifier si c'est une fausse sequence JSON (ex: \text)
                is_latex_command = False
                if next_ch in LATEX_KEYWORDS:
                    for keyword in LATEX_KEYWORDS[next_ch]:
                        if raw_content.startswith(keyword, i + 2):
                            # V0.98 FIX: Faux positifs
                            # Verifier que ce n'est pas le debut d'un mot plus long (ex: \textrapolate)
                            next_idx = i + 2 + len(keyword)
                            if next_idx >= len(raw_content) or not raw_content[next_idx].isalpha():
                                is_latex_command = True
                                break
                            
                if next_ch in VALID_JSON_ESCAPES and not is_latex_command:
                    # Sequence valide et pas une commande LaTeX
                    result.append(ch)
                    result.append(next_ch)
                    i += 2
                else:
                    # Sequence invalide ou commande LaTeX, on double le backslash
                    result.append('\\\\')
                    result.append(next_ch)
                    i += 2
            else:
                result.append(ch)
                i += 1
        else:
            result.append(ch)
            i += 1
    return ''.join(result)

# ==========================================
# CONFIGURATION DES MODELES ANKI (genanki)
# ==========================================

CSS = """
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: white;
}
.cloze {
  font-weight: bold;
  color: blue;
}
"""

MODEL_BASIC_ID = 1593820471
model_basic = genanki.Model(
  MODEL_BASIC_ID,
  'Basique (Mistral)',
  fields=[
    {'name': 'Front'},
    {'name': 'Back'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Front}}',
      'afmt': '{{Front}}<hr id="answer">{{Back}}',
    },
  ],
  css=CSS
)

MODEL_GENERALITES_ID = 1593820473
model_generalites = genanki.Model(
  MODEL_GENERALITES_ID,
  'Généralités deux sens (Mistral)',
  fields=[
    {'name': 'Front'},
    {'name': 'Back'},
  ],
  templates=[
    {
      'name': 'Sens 1',
      'qfmt': '{{Front}}',
      'afmt': '{{Front}}<hr id="answer">{{Back}}',
    },
    {
      'name': 'Sens 2',
      'qfmt': '{{Back}}',
      'afmt': '{{Back}}<hr id="answer">{{Front}}',
    },
  ],
  css=CSS
)

MODEL_CLOZE_ID = 1593820474
model_cloze = genanki.Model(
  MODEL_CLOZE_ID,
  'Texte à trous V2 (Mistral)',
  model_type=genanki.Model.CLOZE,
  fields=[
    {'name': 'Text'},
    {'name': 'Back Extra'},
  ],
  templates=[
    {
      'name': 'Cloze',
      'qfmt': '{{cloze:Text}}',
      'afmt': '{{cloze:Text}}<br><hr><br>{{Back Extra}}',
    },
  ],
  css=CSS
)

MODEL_CLOZE_SIBLINGS_ID = 1593820475
model_cloze_siblings = genanki.Model(
  MODEL_CLOZE_SIBLINGS_ID,
  'Texte à trous (Cartes Soeurs)',
  fields=[
    {'name': 'Front1'}, {'name': 'Front2'}, {'name': 'Front3'}, {'name': 'Front4'}, {'name': 'Front5'},
    {'name': 'Front6'}, {'name': 'Front7'}, {'name': 'Front8'}, {'name': 'Front9'}, {'name': 'Front10'},
    {'name': 'Back'}
  ],
  templates=[
    {
      'name': f'Card {i}',
      'qfmt': '{{Front' + str(i) + '}}',
      'afmt': '{{Front' + str(i) + '}}<hr id="answer">{{Back}}',
    } for i in range(1, 11)
  ],
  css=CSS
)

# ==========================================
# LOGIQUE PRINCIPALE
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

def split_markdown_into_chunks(markdown_text, max_chunk_size=3000):
    lines = markdown_text.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        is_header = line.startswith("# ") or line.startswith("## ") or line.startswith("### ")
        
        if is_header and current_length > 1000:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = len(line)
        else:
            current_chunk.append(line)
            current_length += len(line) + 1

        if current_length > max_chunk_size:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks

def semantic_split_with_ai(client, markdown_text, model="mistral-large-latest", retries=2):
    lines = markdown_text.split("\n")
    # Numérotation des lignes pour guider l'IA
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    numbered_text = "\n".join(numbered_lines)

    system_prompt = r"""
ROLE
You are a structural parser Agent. Your only job is to semantically split an academic course text (provided with line numbers) into logical "chunks" or "blocks".
Each chunk must be a coherent pedagogical unit that can later be fed completely to an Anki card generator.

RULES:
1. MAXIMUM AGGREGATION FOR MATHEMATICAL CONCEPTS: A Theorem (or Proposition/Property), its associated Proof, and its direct Examples/Remarks form ONE INDIVISIBLE UNIT. You MUST group them together into ONE SINGLE CHUNK.
   - Example scenario: Line 10 is `## THEOREM 1`, Line 40 is `# EXAMPLE 1`, Line 70 is `# PROOF`, Line 120 is `# EXAMPLE 2`. You MUST create a SINGLE chunk starting at line 10 and ending at line 140 inclusive.
   - NEVER separate the formal statement of a Theorem from its Proof or its Examples. They MUST physically reside in the exact same chunk.
   - You only start a new chunk when shifting to a completely independent topic, a completely new Theorem, or a list of disconnected definitions.
2. A single chunk can contain multiple Definitions or minor properties if they are closely related.
3. Output a JSON array with the exact start and end line numbers for each chunk.

OUTPUT FORMAT MUST BE STRICTLY JSON:
{
    "chunks": [
        {"start": 1, "end": 45, "reason": "Intro and early definitions"},
        {"start": 46, "end": 150, "reason": "Theorem 1 + Example 1 + Proof of Theorem 1"}
    ]
}

Ensure no lines are left out. The first chunk starts at 1, the last chunk ends at the last line number.
"""

    for attempt in range(retries):
        try:
            print(f"   (Agent Splitter en cours d'analyse - Tentative {attempt+1}/{retries}...)")
            response = client.chat.complete(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Voici le texte numéroté en entrée, divisez-le en suivant strictement les règles :\n\n{numbered_text}"}
                ]
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            
            if "chunks" in data:
                chunks = []
                for chunk_info in data["chunks"]:
                    start = max(0, int(chunk_info["start"]) - 1)
                    end = min(len(lines), int(chunk_info["end"]))
                    if end > start:
                        chunks.append("\n".join(lines[start:end]))
                
                if chunks:
                    return chunks
        except Exception as e:
            import time
            print(f"   Erreur Agent Splitter: {e}. Nouvel essai...")
            time.sleep(2)
            
    # Fallback
    print("   Fallback: utilisation du découpage heuristique statique.")
    return split_markdown_into_chunks(markdown_text)

def extract_cards_from_chunk(client, chunk_text, filename_tag="Course", model="mistral-large-latest", retries=3):
    tag_instruction = (
        f"TAGS RULES: Every card MUST have a 'tags' field. "
        f"The first tag MUST always be '{filename_tag}'. "
        f"Then add 1-2 topic tags using the format 'Topic_Subtopic' (underscores, NO spaces). "
        f"Example: '{filename_tag} Pressure_Gradient Hydrostatics'"
    )
    
    system_prompt = r"""
ROLE
You are a bulletproof, scholarly Anki Flashcard Generator. 
Your goal is to parse academic engineering course content into highly detailed Anki flashcards.

RULES (CRITICAL):
1. LANGUAGE (STRICT LIMITATION): The generated text MUST be in the EXACT SAME LANGUAGE as the source text. NEVER translate.
2. ZERO-PRONOUN & CONTEXT SCRUBBING (ABSOLUTELY CRITICAL): Flashcards are viewed out of order. You MUST aggressively SCRUB and REMOVE any phrases like "In Example 1", "As we saw in the previous section", "The following theorem", or "This equation". If the textbook says "In Example 1, Green's theorem is verified...", you MUST rephrase it to be standalone: "Verify Green's theorem for the functions...". Never assume the student has the surrounding textbook! ABSOLUTELY NO BLIND REFERENCES: If the text says 'By Theorem 2.1', you MUST replace it by stating exactly what the theorem says. Never use blind pointers like 'Proposition 5.1' or 'Equation 17'.
3. PRESERVATION: Include ALL theorems, definitions, proofs, remarks, and examples exactly as they appear in the course. Do not condense important details.
4. JSON BACKSLASH ESCAPING: Because you are generating JSON, you MUST double-escape EVERY single backslash (`\\frac`, `\\text`).
    - For ALL cards, write the text assuming it is inside a mathematical `aligned` block.
    - Every visual line MUST start with the alignment character `& ` to ensure left-alignment.
    - To break lines, use LaTeX line breaks `\\\\`.
    - Use `\text{...}` for ALL standard readable text. **PAY ATTENTION TO SPACES** inside `\text{...}`!
    - **LINE WRAPPING LIMIT:** Manually wrap lines exceeding 75 chars by closing the current `\text{}`, outputting `\\\\`, and starting anew.
    - NEVER place line breaks `\\\\` or alignment characters `& ` INSIDE a cloze deletion.
5. IMAGES: You MUST NOT drop any image! Embed any image reference (e.g. `![img-0.jpeg](img-0.jpeg)`) in the most relevant flashcard EXACTLY as `![image_name](image_name)`. Let the image stand on a broken line via `\\\\`.
6. CLOZE FORMAT: Use DOUBLE SQUARE BRACKETS `[[c1::...]]` to define clozes. NEVER use curly braces! Group structurally related words under the SAME cloze index.
IMPORTANT: When clozing natural language, the cloze MUST be placed INSIDE the \text{} block. 
CORRECT: \text{The process is called [[c1::convolution]]}
WRONG: \text{The process is called } [[c1::\text{convolution}]]
NEVER put \text{} inside the cloze.
Mathematical expressions can be clozed outside \text{}.
7. IMAGE-DESCRIPTION PROHIBITION (CRITICAL): NEVER create cards that ask "What does this image show?", "Describe this image", "What is depicted?", "What is being illustrated?" or any variant. The front MUST contain a specific conceptual question about the TOPIC, not about an image. Images are supplementary visual aids placed as support, not the subject of questions.
   BAD: "What is depicted in this image?" + image
   GOOD: "Explain the convolution process in a CNN" (image on back as reference)
8. IMAGE PLACEMENT: When including an image reference `![img-x.jpeg](img-x.jpeg)`, it MUST be placed OUTSIDE any \text{} block, on its own line separated by `\\`.
   CORRECT: `\text{explanation} \\\\ \\\\ ![img-x.jpeg](img-x.jpeg)`
   WRONG: `\text{explanation \\\\ ![img-x.jpeg](img-x.jpeg)}`
9. NO LATEX LISTS (CRITICAL): NEVER use `\begin{itemize}`, `\begin{enumerate}`, or `\item`. MathJax aligned environments DO NOT support them and rendering will break. Use standard text lists like `-` or `1.` inside `\text{...}` instead.
10. NO INLINE MATH WRAPPERS (CRITICAL): NEVER use inline math delimiters like `$`, `$$`, `\\[`, or `\\(`. The entire flashcard is ALREADY wrapped in a MathJax block (`\( \begin{aligned} ... \end{aligned} \)`). Just write the math variables directly (e.g. `T_H`, not `$T_H$`).
11. AGGREGATION: Consolidate related information. Avoid making 5 separate cards for a single topic; instead make 1 rich 'Basique' card asking a comprehensive question with all the details synthesized on the back.
12. ABSOLUTELY NO MULTIPLE CHOICE QUESTIONS (MCQ): NEVER generate cards that ask "Which of the following statements is true/false?", "Identify the incorrect statement", or any variation of a multiple choice question. You MUST convert all multiple-choice questions from the source text into direct, open-ended conceptual questions. DO NOT list choices (A, B, C, D) on the front or back.
13. NO TRUNCATED CONTENT (CRITICAL): If you announce a list (with ':'), you MUST provide it IN FULL. NEVER write 'The Carnot cycle is composed of four processes:' without listing ALL four processes. The back MUST always completely answer the question asked on the front. If the front asks 'What are the four processes?', the back MUST list all four. Similarly, NEVER put 'For example:' on the front without including the actual examples either on the front or clearly on the back.
14. MULTI-IMAGE FIGURES (CRITICAL): A single figure in the source text may contain MULTIPLE images (e.g. `![img-5.jpeg](img-5.jpeg)` and `![img-6.jpeg](img-6.jpeg)` appearing together). You MUST include ALL images from the figure in the same card, not just the first one. If a figure has 2 graphs, include both. If it has 3 diagrams, include all 3. Place them on consecutive lines separated by `\\\\`.
15. NO \\tag{} COMMAND: NEVER use `\\tag{...}` (e.g. `\\tag{4.2.8}`). MathJax in Anki does NOT support it. Instead, use `\\text{    4.2.8}` (with leading spaces for visual separation from the equation) to label or reference equations.

RULES SPECIFIC TO THEOREMS AND DEFINITIONS (MANDATORY EXPECTATIONS):

IF THE CONTENT IS A THEOREM, PROPOSITION, COROLLARY, OR PROPERTY:
- ZERO-FRAGMENTATION RULE: You MUST GENERATE EXACTLY ONE COMPREHENSIVE CARD for the entire Theorem/Proposition unit. DO NOT fragment the proof or remarks into separate flashcards or separate cloze cards.
- Subdeck: MUST be "À Refaire"
- Card Type: MUST be "Basique" (for a question or basic card) or "Texte à trous" (if clozes are needed)
- `front` (Recto): You have 3 valid options:
   1. A clear question (e.g., "\text{State the Green's theorem}")
   2. The exact name of the theorem
   3. The exact statement of the theorem but with cloze deletions `[[c1::...]]`.
- `back` (Verso) CRITICAL REQUIREMENT:
   1. If `front` used a clozed statement, put the ENTIRE UNC-LOZED statement here first. If `front` used a question or the name of the theorem, still put the statement of the theorem here first.
   2. THEN, you MUST INCLUDE THE ENTIRE COMPLETE DEMONSTRATION/PROOF from the text, exactly as provided. DO NOT summarize it. DO NOT skip equations. It is essential the student learns to reproduce the full proof.
   3. THEN, include any remarks, corollaries, or examples that immediately follow it in the text.
   This guarantees that all context is physically printed on the back of the ONE theorem card.

IF THE CONTENT IS AN EXAMPLE OR AN EXERCISE:
- Subdeck: MUST be "À Refaire"
- Card Type: MUST be "Basique" -> ask for the resolution of the given example/exercise (stated on the front)
- `front` CRITICAL SELF-CONTAINMENT RULE: You MUST make the card completely self-contained. ABSOLUTELY NEVER refer to an example name (e.g., REMOVE "In Example 1..."). The student looking at the card does not have the book. You MUST write out the ENTIRE problem statement, all contextual equations, given values, and the exact question to solve explicitly on the front.
- `back`: Provide the complete, step-by-step resolution of the example/exercise.

IF THE CONTENT IS A GENERAL CONCEPT, DEFINITION, VOCABULARY, OR FACTUAL KNOWLEDGE:
- CONCEPTUAL AGGREGATION RULE (CRITICAL): Do NOT create many small cards for properties of the same concept. Group closely related facts, descriptions, and rules into a SINGLE comprehensive flashcard.
- Prefer a "Basique" card with a broad, overarching question on the front (e.g., "Describe the properties and purpose of the Carnot cycle"), and the full aggregated explanation on the back. Do not abuse "Texte à trous".
- Subdeck: MUST be "Par Cœur"
- Card Type: "Basique" (preferred) or "Généralités" or "Texte à trous" (sparingly)
- `front`: Ask a comprehensive conceptual question or ask for the definition.
- `back`: Provide the exact, concise definition or full aggregated text.
- If using "Généralités" (two-sided), replace the defined concept name on the back with a pronoun (e.g., "It", "They").

JSON OUTPUT ONLY:
{
    "cards": [
        {
            "type": "Texte à trous" | "Basique" | "Généralités",
            "subdeck": "Par Cœur" | "À Refaire",
            "front": "Complete text/formulas written in LaTeX, using \\text{} for normal text.",
            "back": "Detailed proof/answer in LaTeX, using \\text{} for normal text. Split lines > 75 chars.",
            "tags": "Math Course_Unit (NO SPACES IN INDIVIDUAL TAGS)"
        }
    ]
}
"""

    for attempt in range(retries):
        try:
            response = client.chat.complete(
                model=model,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "GeneratedCards",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "cards": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": ["Texte à trous", "Basique", "Généralités"]
                                            },
                                            "subdeck": {
                                                "type": "string",
                                                "enum": ["Par Cœur", "À Refaire"]
                                            },
                                            "front": {"type": "string"},
                                            "back": {"type": "string"},
                                            "tags": {"type": "string"}
                                        },
                                        "required": ["type", "subdeck", "front", "back", "tags"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": ["cards"],
                            "additionalProperties": False
                        }
                    }
                },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Extract all valuable concepts systematically from this content segment.\nCRUCIAL RULES FOR THIS CHUNK:\n1. KEEP THE EXACT SAME LANGUAGE AS THE TEXT BELOW. ABSOLUTELY NO FRENCH ALLOWED UNLESS THE TEXT ITSELF IS IN FRENCH. IF THE TEXT IS IN ENGLISH, EVERY SINGLE WORD OF YOUR GENERATED JSON MUST BE IN ENGLISH.\n2. Prioritize 'Texte à trous' and 'Basique' cards. ONLY use 'Généralités' sparingly for extremely fundamental, high-level definitions where a double-sided card is strictly necessary.\n3. {tag_instruction}\n\n{chunk_text}"}
                ]
            )
            
            content = response.choices[0].message.content
            
            # CRITICAL: fix_llm_json_escaping IS needed even with strict json_schema.
            # Reason: \text -> \t+ext (tab), \frac -> \f+rac (form feed), \nu -> \n+u (newline)
            # These are VALID JSON escapes that destroy LaTeX commands silently.
            content = fix_llm_json_escaping(content)
            
            data = json.loads(content)
            
            if "cards" in data:
                return data["cards"]
            else:
                print(f"Format JSON invalide. Tentative {attempt+1}/{retries}...")
        except Exception as e:
            print(f"Erreur d'API ou de parsing Mistral. Tentative {attempt+1}/{retries}... ({e})")
            time.sleep(2)
            
    print("Erreur: Impossible de traiter le chunk après plusieurs tentatives. Sautant ce chunk...")
    return []

def ai_quality_control_cards(client, cards, chunk_text="", image_descriptions=None, model="mistral-small-latest", retries=2):
    if not cards: return []
    
    print(f"   (Mistral Small : Agent QA actif sur {len(cards)} cartes...)")
    cards_payload = [{"id": i, "front": c.get("front", ""), "back": c.get("back", ""), "type": c.get("type", "")} for i, c in enumerate(cards)]
    payload_json = json.dumps(cards_payload, ensure_ascii=False)
    
    system_prompt = r"""
ROLE: Flashcard Quality Assurance Agent & Expert Typographe LaTeX.
Vos flashcards contiennent parfois des références aveugles à un livre ("D'après la proposition 2.14") OU des erreurs de formatage LaTeX (accolades non balancées, texte hors de \text{}).

TACHE: Evaluez chaque carte dans le JSON fourni pour les aspects suivants :
A. Le contexte visuel (CRITIQUE) : Si une carte contient une référence aveugle à une figure (ex: "Fig 2.3", "Points a, b, c"), vous DEVEZ vérifier dans le [TEXTE D'ORIGINE DU BLOC] fourni plus bas si cette image (représentée par `![img-x.jpeg](...)`) existe.
   - Si elle existe, REECRIVEZ la carte en injectant obligatoirement le lien exact de l'image à la fin du texte, sur sa propre ligne.
   - Si l'image n'est VRAIMENT PAS dans le texte, alors seulement supprimez la référence aveugle ou rejetez la carte.
   - Si l'image figure déjà dans la carte, analyser l'image pour s'assurer de la correspondance entre le texte et l'image. Si l'image est manquante ou ne correspond pas au texte, appliquez les règles précédentes.
   ATTENTION MULTI-IMAGES (V0.98 - TRÈS IMPORTANT) : Une figure peut comporter PLUSIEURS images côte à côte ou empilées dans le texte source. Vous DEVEZ IMPÉRATIVEMENT toutes les inclure dans la carte, pas seulement la première. Vérifiez dans le [TEXTE D'ORIGINE DU BLOC] s'il y a des images consécutives (ex: img-5.jpeg suivi de img-6.jpeg) faisant partie de la même figure.
   VÉRIFICATION DE CORRESPONDANCE : Si la carte contient déjà une image, vérifiez dans l'[INDEX DES IMAGES ET LEURS DESCRIPTIONS] que l'image correspond bien au sujet traité par la carte. Utilisez les descriptions et concepts-clés pour valider la correspondance. Si une image ne correspond manifestement pas au sujet de la carte, remplacez-la par la bonne image de l'index ou retirez-la.

   IMAGE INJECTION FORMAT (ABSOLUMENT CRITIQUE - NE JAMAIS VIOLER) :
   Quand vous injectez une image, elle DOIT TOUJOURS être placée EN DEHORS de tout bloc \text{...}.
   L'image doit être isolée sur sa propre ligne, séparée par des sauts de ligne LaTeX :
   CORRECT : \\text{explication du concept}\\\\ \\\\ ![img-x.jpeg](img-x.jpeg)
   CORRECT : \\text{fin du texte}\\\\ \\\\ ![img-5.jpeg](img-5.jpeg) \\\\ ![img-6.jpeg](img-6.jpeg)
   INCORRECT : \\text{explication \\\\ ![img-x.jpeg](img-x.jpeg)}
   INCORRECT : \\text{\\\\\\ \\![img-x.jpeg](img-x.jpeg)}
   Si vous voyez une image à l'intérieur d'un \text{}, SORTEZ-LA immédiatement.

B. Références aveugles et autonomie (STRICT) : le texte (front/back) doit être 100% autonome.
   - Retirez toute phrase du type "Dans cet exemple", "the given example", "the provided example", "in the following", à moins que l'exemple ne soit écrit en entier dans la carte.
   - Remplacez ces références par le contenu réel. Par exemple :
     MAUVAIS : "In the given example, what happens to the input volume?"
     BON : "Given an input volume of size [224x224x64] and a max-pooling layer with filter size 2 and stride 2, what is the output size?"
   - Si la carte décrit un exercice ou un exemple (ex: "Find the net work output for the example..."), mais que l'énoncé COMPLET (valeurs, contexte) n'est pas sur la carte, VOUS DEVEZ LE RÉÉCRIRE en utilisant le texte d'origine. Si cela dépend d'une image introuvable, REJETEZ LA CARTE.

C. Les balises \text{} MANQUANTES : (CRITIQUE) MathJax compresse le texte normal s'il n'est pas dans un \text{}. Vous DEVEZ vérifier que TOUTES les phrases en langage naturel sont ENTIÈREMENT encadrées par des \text{...}.
   - Vous DEVEZ vérifier rigoureusement que CHAQUE commande `\text{` possède son accolade fermante correspondante `}`. Un oubli d'accolade fait planter tout le rendu !
   - ATTENTION CLOZES : Le tag de cloze entier DOIT être à l'intérieur du \text{...}. NE METTEZ JAMAIS de \text{} à l'intérieur d'un cloze.
   CORRECT : \\text{This is a [[c1::fluid]]}
   INCORRECT : \\text{This is a } [[c1::\\text{fluid}]]

D. Les accolades non fermées : Vérifiez consciencieusement que chaque { a son } correspondant, particulièrement pour les \text{...} de fin de ligne.

E. Environnements LaTeX INVALIDS : (CRITIQUE)
   - NE JAMAIS UTILISER `\begin{itemize}`, `\begin{enumerate}`, `\begin{itemsize}` ou `\item`. L'environnement `aligned` de MathJax ne les supporte pas. Remplacez-les par de simples listes en texte (`1.`, `-`) à l'intérieur de `\text{...}`.
   - NE JAMAIS UTILISER de délimiteurs mathématiques comme `$`, `$$`, `\[`, ou `\(`. Le tout est DÉJÀ encapsulé dans un environnement MathJax `aligned`. Utilisez simplement `\text{variable}` ou tapez les variables mathématiques directement (ex: `T_H`, pas `$T_H$`).

E. INJECTION D'IMAGE PROACTIVE INTERDITE : N'ajoutez JAMAIS d'image de votre propre chef à une carte "autonome". Vous ne devez insérer une image que si et seulement si le texte de la carte contient une référence aveugle explicite (ex: "As shown in Fig 3", "In the diagram below") qui nécessite l'image pour être comprise. Si la carte est compréhensible sans image, LAISSEZ-LA SANS IMAGE.

F. Les cartes sans utilité pédagogique : Si la carte mentionne seulement quelque chose qui sera étudié plus tard, ou qui n'est pas pertinent (ne sollicite pas une notion du cours), rejetez la carte.

G. CARTES IMAGE-SEULE (REJET SYSTÉMATIQUE) : Si le front d'une carte ne contient QU'UNE IMAGE (ou qu'une image avec des commandes LaTeX de mise en forme comme & ou \\, sans aucun texte de question en langage naturel), vous DEVEZ la REJETER avec "action": "reject". Le front DOIT obligatoirement contenir une question textuelle claire. Une image seule n'est jamais une question valide.

H. CARTES "DÉCRIVEZ L'IMAGE" (REJET OU RÉÉCRITURE OBLIGATOIRE) : Si le front demande de "décrire", "expliquer" ou "identifier" ce que montre une image ("What is depicted in this image?", "Describe the concept in this image", "What does this image represent?", "What is being illustrated?"), cette carte est PÉDAGOGIQUEMENT FAIBLE et doit être :
   - SOIT RÉÉCRITE en posant une question conceptuelle PRÉCISE sur le sujet illustré (pas sur l'image elle-même), avec l'image déplacée au BACK comme support visuel.
     Exemple : Au lieu de "What is depicted in this image? [img]" → "Explain the convolution process in a CNN, including how a filter interacts with the input volume."
   - SOIT REJETÉE si le concept est déjà couvert par d'autres cartes.

I. LIMITE D'INJECTION D'IMAGE : N'injectez pas la même image dans plus de 2 cartes du lot. Si l'image est déjà référencée dans d'autres cartes, privilégiez la carte la plus pertinente.

J. CARTES QCM (RÉÉCRITURE OBLIGATOIRE OU REJET) : Si une carte demande "Laquelle de ces affirmations est vraie/fausse ?", "Identify the incorrect statement", ou présente des options (A, B, C, D), vous DEVEZ ABSOLUMENT la réécrire pour formuler une question ouverte directe (ex: "Quelles sont les propriétés de...?") et lister les informations sur le back, sans jamais lister les choix multiples. Rejetez-la si elle n'est pas sauvable.

K. PRESERVATION DES MARQUEURS D'ALIGNEMENT (CRITIQUE) : Chaque ligne visuelle dans le front et le back DOIT commencer par le caractère d'alignement `& ` (esperluette + espace). Ne supprimez JAMAIS les `& ` en début de ligne lors d'une réécriture. Si une carte réécrite perd ses `& `, vous devez les remettre.

L. FRONT INCOMPLET (REJET OU RÉÉCRITURE) : Si le front se termine par ":" ou "For example:" sans que le contenu annoncé soit présent sur le front, vous DEVEZ soit compléter le front avec le contenu manquant, soit supprimer le ":" / "For example:" pour que le front soit une question autonome. Un front qui promet du contenu sans le fournir est INTERDIT.

M. BACK INCOMPLET (RÉÉCRITURE OBLIGATOIRE) : Si le back annonce une liste (ex: "composed of four processes:") mais ne fournit pas la liste complète, vous DEVEZ compléter le back avec les éléments manquants en utilisant le [TEXTE D'ORIGINE DU BLOC]. Un back qui ne répond pas complètement à la question du front est INACCEPTABLE.

Règles d'action :
1. Si la carte est une localisation ("Où est défini X?") ou est insolvable SANS image (et l'image est introuvable), renvoyez "action": "reject".
2. S'il faut insérer une image, corriger une référence, encadrer par \text{}, ou réparer une accolade, renvoyez "action": "rewrite", et donnez le texte parfaitement formaté.
3. Si la carte est parfaitement autonome (ou a déjà son image) et parfaitement formatée, renvoyez "action": "keep".

IMPORTANT : Conserver rigoureusement la syntaxe des clozes ([[c1::...]]). Doubler les backslashes Latex dans le JSON (\\\\text, \\\\\\\\).

OUTPUT JSON PRECIS:
{
    "results": [
        {
            "id": 0,
            "action": "keep" | "reject" | "rewrite",
            "front": "le texte corrigé si rewrite",
            "back": "le texte corrigé si rewrite",
            "reasoning": "rationnel de la décision"
        }
    ]
}
"""

    for attempt in range(retries):
        try:
            response = client.chat.complete(
                model=model,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "QualityControlResults",
                        "strict": True,
                        "schema": {
                            "type": "object",
                            "properties": {
                                "results": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "action": {"type": "string", "enum": ["keep", "reject", "rewrite"]},
                                            "front": {"type": "string"},
                                            "back": {"type": "string"},
                                            "reasoning": {"type": "string"}
                                        },
                                        "required": ["id", "action", "front", "back", "reasoning"],
                                        "additionalProperties": False
                                    }
                                }
                            },
                            "required": ["results"],
                            "additionalProperties": False
                        }
                    }
                },
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"[TEXTE D'ORIGINE DU BLOC POUR REFERENCE IMAGE ET CONTEXTE]\n{chunk_text}\n\n" + (f"[INDEX DES IMAGES ET LEURS DESCRIPTIONS]\n" + "\n".join([f"- {k}: {v}" for k, v in (image_descriptions or {}).items() if v]) + "\n\n" if image_descriptions else "") + f"=======================\nVoici les cartes à évaluer et corriger :\n{payload_json}"}
                ]
            )
            content = response.choices[0].message.content
            # CRITICAL: fix_llm_json_escaping IS needed even with strict json_schema.
            # \text -> \t+ext, \frac -> \f+rac, \nu -> \n+u are valid JSON escapes
            content = fix_llm_json_escaping(content)
            data = json.loads(content)
            
            if "results" in data:
                valid_cards = []
                rejected_count = 0
                rewritten_count = 0
                
                results_map = {res.get("id"): res for res in data.get("results", [])}
                
                for i, c in enumerate(cards):
                    res = results_map.get(i)
                    if not res:
                        valid_cards.append(c)
                        continue
                        
                    action = res.get("action", "keep")
                    if action == "reject":
                        rejected_count += 1
                        print(f"      [QA REJECT] Carte rejetée : {c.get('front', '')[:80]}...")
                        try:
                            with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                                f.write("## [MISTRAL SMALL QA] Carte Rejetée\n\n")
                                f.write(f"### Raison:\n{res.get('reasoning', 'Non spécifiée')}\n\n")
                                f.write("### Carte Originale:\n```json\n" + json.dumps({"front": c.get("front", ""), "back": c.get("back", "")}, ensure_ascii=False, indent=2) + "\n```\n\n---\n")
                        except Exception as e:
                            print(f"Log Error: {e}")
                    elif action == "rewrite":
                        rewritten_count += 1
                        old_front = c.get("front", "")
                        old_back = c.get("back", "")
                        c["front"] = res.get("front", c.get("front"))
                        c["back"] = res.get("back", c.get("back"))
                        valid_cards.append(c)
                        print(f"      [QA REWRITE] Carte corrigée : {c.get('front', '')[:80]}...")
                        
                        try:
                            with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                                f.write("## [MISTRAL SMALL QA] Carte Corrigée\n\n")
                                f.write("### Avant:\n```json\n" + json.dumps({"front": old_front, "back": old_back}, ensure_ascii=False, indent=2) + "\n```\n\n")
                                f.write("### Après:\n```json\n" + json.dumps({"front": c["front"], "back": c["back"]}, ensure_ascii=False, indent=2) + "\n```\n\n---\n")
                        except Exception as e:
                            print(f"Log Error: {e}")
                    else:
                        valid_cards.append(c)
                
                print(f"   => Contrôle Qualité terminé : {len(valid_cards)} cartes conservées dont {rewritten_count} corrigées. {rejected_count} rejetées.")
                return valid_cards
        except Exception as e:
            import time
            print(f"   Erreur QA Mistral Small (Tentative {attempt+1}/{retries}): {e}")
            time.sleep(2)
            
    print("   QA a échoué. Retour des cartes non filtrées.")
    return cards

def filter_image_only_cards(cards):
    """Filtre post-QA : rejette les cartes dont le front ne contient que des images sans texte."""
    filtered = []
    rejected_count = 0
    for c in cards:
        front = c.get("front", "")
        # Retirer les images, commandes LaTeX de structure, espaces
        robust_pattern_img = r'\\*!?\\*\[([^\]]*?)\\*\]\\*\(([^)]+?\.(?:jpeg|jpg|png|gif|webp|svg))\\*\)'
        text_only = re.sub(robust_pattern_img, '', front, flags=re.IGNORECASE)
        text_only = re.sub(r'\\text\{\s*\}', '', text_only)
        text_only = re.sub(r'[&\\{}\s]', '', text_only)
        text_only = text_only.strip()
        if len(text_only) < 5:  # Pas assez de texte pour constituer une question
            rejected_count += 1
            print(f"      [FILTRE IMAGE-SEULE] Carte rejetée : {front[:80]}...")
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [FILTRE IMAGE-SEULE] Carte Rejetée\n\n")
                    f.write(f"### Front:\n```\n{front}\n```\n\n")
                    f.write(f"### Raison:\nLe front ne contient que des images sans question textuelle (texte résiduel: '{text_only}', {len(text_only)} chars).\n\n---\n")
            except Exception as e:
                print(f"Log Error: {e}")
            continue
        filtered.append(c)
    if rejected_count > 0:
        print(f"   => Filtre image-seule : {rejected_count} carte(s) rejetée(s), {len(filtered)} conservée(s).")
    return filtered

def filter_mcq_cards(cards):
    """Post-QA filter: detect and reject cards that still contain MCQ patterns.
    MCQ cards violate the pedagogical rule requiring open-ended conceptual questions."""
    filtered = []
    rejected_count = 0
    
    # MCQ detection patterns
    mcq_front_patterns = [
        r'(?i)which\s+(?:of\s+the\s+following|statement)',
        r'(?i)select\s+the\s+(?:correct|incorrect)',
        r'(?i)identify\s+the\s+(?:correct|incorrect)',
        r'(?i)laquelle?\s+(?:de\s+ces|des\s+suivant)',
        r'(?i)choisissez?\s+la\s+(?:bonne|correcte)',
        r'(?i)(?:true|false|vrai|faux)\s*(?:\?|$)',
    ]
    
    for c in cards:
        front = c.get("front", "")
        back = c.get("back", "")
        is_mcq = False
        matched_pattern = ""
        
        # Check for MCQ question patterns in front
        for pattern in mcq_front_patterns:
            if re.search(pattern, front):
                is_mcq = True
                matched_pattern = pattern
                break
        
        # Check for multiple (a), (b), (c) style choices
        if not is_mcq:
            choice_count = len(re.findall(r'\([a-e]\)', front))
            if choice_count >= 3:
                is_mcq = True
                matched_pattern = "Multiple choice options (a)(b)(c)..."
        
        # Check for roman numeral MCQ lists (I. II. III. with question keywords)
        if not is_mcq:
            roman_count = len(re.findall(r'(?:^|\s)(?:I{1,3}|IV|V)\.\s', front))
            if roman_count >= 3 and re.search(r'(?i)(?:statement|correct|true|false|affirmation)', front):
                is_mcq = True
                matched_pattern = "Roman numeral MCQ (I. II. III.)"
        
        if is_mcq:
            rejected_count += 1
            print(f"      [FILTRE MCQ] Carte rejetée : {front[:80]}...")
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [FILTRE MCQ] Carte Rejetée\n\n")
                    f.write(f"### Pattern détecté:\n`{matched_pattern}`\n\n")
                    f.write(f"### Front:\n```\n{front}\n```\n\n")
                    f.write(f"### Back:\n```\n{back}\n```\n\n---\n")
            except Exception as e:
                print(f"Log Error: {e}")
            continue
        filtered.append(c)
    
    if rejected_count > 0:
        print(f"   => Filtre MCQ : {rejected_count} carte(s) MCQ rejetée(s), {len(filtered)} conservée(s).")
    return filtered

def filter_truncated_cards(cards):
    """Post-QA filter: detect cards with truncated fronts or incomplete backs.
    - Front ending with ':' or 'For example:' without content = truncated front
    - Back ending with ':' without listing the announced items = incomplete back"""
    filtered = []
    rejected_count = 0
    
    for c in cards:
        front = c.get("front", "")
        back = c.get("back", "")
        is_truncated = False
        reason = ""
        
        # Strip LaTeX formatting to analyze the actual text content
        front_clean = re.sub(r'\\text\{([^}]*)\}', r'\1', front)
        front_clean = re.sub(r'[\\&{}]', '', front_clean).strip()
        back_clean = re.sub(r'\\text\{([^}]*)\}', r'\1', back)
        back_clean = re.sub(r'[\\&{}]', '', back_clean).strip()
        
        # Check: front ends with ':' or 'For example:' (truncated front)
        if re.search(r'(?:For example|Par exemple)\s*:?\s*$', front_clean, re.IGNORECASE):
            is_truncated = True
            reason = "Front se termine par 'For example:' sans contenu"
        
        # Check: back ends with ':' suggesting an incomplete list
        if not is_truncated and back_clean.endswith(':'):
            # Only flag if the back is very short (likely just the intro sentence)
            if len(back_clean) < 200:
                is_truncated = True
                reason = f"Back se termine par ':' sans lister les \u00e9l\u00e9ments annonc\u00e9s ('{back_clean[-60:]}...')"
        
        # Check: back is suspiciously short relative to front
        if not is_truncated and len(back_clean) < 30 and len(front_clean) > 50:
            is_truncated = True
            reason = f"Back anormalement court ({len(back_clean)} chars) pour un front de {len(front_clean)} chars"
        
        if is_truncated:
            rejected_count += 1
            print(f"      [FILTRE TRONCATURE] Carte rejet\u00e9e : {front_clean[:80]}...")
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [FILTRE TRONCATURE] Carte Rejet\u00e9e\n\n")
                    f.write(f"### Raison:\n{reason}\n\n")
                    f.write(f"### Front:\n```\n{front}\n```\n\n")
                    f.write(f"### Back:\n```\n{back}\n```\n\n---\n")
            except Exception as e:
                print(f"Log Error: {e}")
            continue
        filtered.append(c)
    
    if rejected_count > 0:
        print(f"   => Filtre troncature : {rejected_count} carte(s) tronqu\u00e9e(s) rejet\u00e9e(s), {len(filtered)} conserv\u00e9e(s).")
    return filtered

def audit_image_coverage(cards, chunk_text, image_descriptions=None):
    """V0.98: Post-QA audit - checks that every image in the chunk appears in at least one card.
    If an image is missing, attempts to inject it into the most relevant card (using image annotations).
    Logs warnings for images that could not be placed."""
    if not cards or not chunk_text:
        return cards
    
    import re
    
    # Find all image references in the chunk text
    chunk_images = set(re.findall(r'!\[.*?\]\(([^)]+\.(?:jpeg|jpg|png|gif|webp|svg))\)', chunk_text, re.IGNORECASE))
    
    if not chunk_images:
        return cards
    
    # Find all image references already present in cards
    covered_images = set()
    for c in cards:
        front = c.get("front", "")
        back = c.get("back", "")
        card_imgs = set(re.findall(r'([\w.-]+\.(?:jpeg|jpg|png|gif|webp|svg))', front + " " + back, re.IGNORECASE))
        covered_images.update(card_imgs)
    
    missing_images = chunk_images - covered_images
    
    if not missing_images:
        return cards
    
    injected_count = 0
    warned_count = 0
    
    for missing_img in missing_images:
        img_desc = (image_descriptions or {}).get(missing_img, "")
        best_card_idx = -1
        best_score = 0
        
        # Extract keywords from image description
        desc_words = set()
        if img_desc:
            desc_words = set(w.lower() for w in re.findall(r'[a-zA-Z]{3,}', img_desc))
        
        for idx_c, c in enumerate(cards):
            card_text = (c.get("front", "") + " " + c.get("back", "")).lower()
            if desc_words:
                # Score = number of matching keywords
                score = sum(1 for w in desc_words if w in card_text)
                if score > best_score:
                    best_score = score
                    best_card_idx = idx_c
            else:
                # No description available -- skip injection, just warn
                break
        
        if best_card_idx >= 0 and best_score >= 2:
            # Inject the image at the end of the back of the most relevant card
            c = cards[best_card_idx]
            img_ref = f" \\\\\\\\ \\\\\\\\ ![{missing_img}]({missing_img})"
            c["back"] = c.get("back", "") + img_ref
            injected_count += 1
            print(f"      [AUDIT IMAGE] Image manquante '{missing_img}' injectee dans carte {best_card_idx} (score: {best_score})")
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write(f"## [AUDIT IMAGE V0.98] Image manquante injectee\n\n")
                    f.write(f"- **Image:** {missing_img}\n")
                    f.write(f"- **Description:** {img_desc}\n")
                    f.write(f"- **Carte cible (ID {best_card_idx}):** {c.get('front', '')[:80]}...\n")
                    f.write(f"- **Score de correspondance:** {best_score}\n\n---\n")
            except Exception as e:
                print(f"Log Error: {e}")
        else:
            warned_count += 1
            print(f"      [AUDIT IMAGE] Image '{missing_img}' non couverte (aucune carte pertinente trouvee)")
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write(f"## [AUDIT IMAGE V0.98] Image non couverte (avertissement)\n\n")
                    f.write(f"- **Image:** {missing_img}\n")
                    f.write(f"- **Description:** {img_desc if img_desc else '(aucune annotation)'}\n")
                    f.write(f"- **Raison:** Aucune carte avec un score de correspondance suffisant (meilleur: {best_score})\n\n---\n")
            except Exception as e:
                print(f"Log Error: {e}")
    
    if injected_count > 0 or warned_count > 0:
        print(f"   => Audit images : {injected_count} image(s) injectee(s), {warned_count} avertissement(s).")
    
    return cards

def supervisor_deduplicate_cards(client, cards, image_descriptions=None, model="mistral-large-latest", retries=3):
    if len(cards) <= 1:
        return cards
        
    print(f"\n   (Agent Superviseur - Étape 1 : Identification sémantique des doublons...)")
    # ÉTAPE 1 : Identification (Seulement le 'front' pour économiser des tokens)
    fronts_only = [{"id": i, "front": c.get("front", "")} for i, c in enumerate(cards)]
    
    prompt_id = r"""
ROLE: Supervisor Agent.
YOUR TASK: Identify duplicate flashcards that test the exact same concept or ask the exact same question.
OUTPUT STRICTLY JSON with an array of groups of duplicate IDs.
Example: If IDs 0, 2, and 4 ask for Green's Theorem, and 10 and 14 ask for Stokes' Theorem, output:
{
    "duplicate_groups": [[0, 2, 4], [10, 14]]
}
If there are no duplicates, output an empty array for duplicate_groups.
"""
    
    cards_front_json = json.dumps(fronts_only, ensure_ascii=False)
    
    duplicate_groups = []
    for attempt in range(retries):
        try:
            response = client.chat.complete(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompt_id},
                    {"role": "user", "content": f"Cartes (rectos) :\n\n{cards_front_json}"}
                ]
            )
            data = json.loads(response.choices[0].message.content)
            duplicate_groups = data.get("duplicate_groups", [])
            
            # V0.98 FIX: Validation stricte du JSON
            if not isinstance(duplicate_groups, list):
                raise ValueError("duplicate_groups n'est pas une liste")
            if duplicate_groups and not isinstance(duplicate_groups[0], list):
                raise ValueError("duplicate_groups doit etre une liste de listes")
                
            break
        except Exception as e:
            import time
            print(f"Erreur d'Identification (Tentative {attempt+1}): {e}")
            time.sleep(2)

    if not duplicate_groups:
        print("   => Aucun doublon détecté, passage direct à l'assemblage.")
        return cards

    # ÉTAPE 2 : Fusion ciblée
    all_deleted_ids = set()
    print(f"   => {len(duplicate_groups)} groupes de doublons détectés. Lancement de la fusion ciblée...")
    
    prompt_fuse = r"""
ROLE: Combiner Agent.
YOUR TASK: You are given a set of POTENTIALLY REDUNDANT Anki flashcards that were flagged as duplicates based ONLY on their fronts.
Now that you have access to their FULL content (front and back), your first job is to decide if they TRULY cover the exact same structural theorem or concept and thus deserve to be merged.
Sometimes, cards might have similar fronts but completely different backs (e.g., asking for different proofs, distinct aspects, or separate examples).

CRITICAL RULES FOR DECIDING:
1. If the cards cover distinct concepts, distinct proofs, or distinct details that should not be combined into a single card without losing pedagogical value, KEEP THEM SEPARATE.
2. If they are genuinely redundant or just overlapping variations of the same underlying concept/theorem/example, MERGE THEM.

CRITICAL RULES FOR COMBINING (IF MERGING):
1. THEOREM/PROOF PRESERVATION: If any of the input cards contains a mathematical PROOF (`Démonstration`), METHODOLOGY, or detailed calculation steps on its "back", you MUST include the FULL, UNCUT proof/methodology on the back of the merged card. NEVER delete or summarize a proof.
2. CONTEXTUAL RECONSTRUCTION: For theorems, the Front MUST contain the statement (or clozed statement), and the Back MUST contain the ENTIRE un-clozed statement followed immediately by the FULL PROOF and any associated remarks/examples.
3. EXAMPLES ZERO-CONTEXT RULE (CRITICAL): The merged card MUST be 100% self-contained. ABSOLUTELY NEVER write things like "In Example 1..." or "For the example above...". The student using the flashcard does NOT have the textbook. The Front MUST explicitly present all initial values, boundary conditions, functions, and the complete question. You MUST rewrite or SCRUB referring phrases.
4. JSON BACKSLASH ESCAPING: You MUST double-escape EVERY single backslash (`\\frac`, `\\text`).
5. Keep the exact same formatting, LaTeX syntax, and cloze boundaries `[[c1::...]]`. NEVER use curly braces `{{c1::...}}`.
6. ALL sentences in natural language (English/French) must be enclosed within a `\\text{...}` command! When clozing natural language, the cloze tag MUST be placed INSIDE the `\\text{}` block. NEVER put `\\text{}` inside the cloze!
CORRECT: `\\text{The process is [[c1::convolution]]}`
WRONG: `\\text{The process is } [[c1::\\text{convolution}]]`
7. NO LATEX LISTS (CRITICAL): NEVER use `\begin{itemize}`, `\begin{enumerate}`, or `\item`. MathJax aligned environments do not support them. Use standard text lists like `-` or `1.` inside `\text{...}` instead.
8. NO INLINE MATH WRAPPERS (CRITICAL): NEVER use inline math delimiters like `$`, `$$`, `\\[`, or `\\(`. The entire flashcard is ALREADY wrapped in a MathJax block (`\( \begin{aligned} ... \end{aligned} \)`). Just write the variables directly.
9. CONCEPTUAL AGGREGATION: If merging multiple cards about the same concept, synthesize all their distinct information into one highly comprehensive "Basique" card with a broad question on the front and the complete synthesized explanation on the back.
10. For the "type" and "subdeck" fields, retain the most appropriate ones from the provided duplicate cards.
11. IMAGE PLACEMENT: Images MUST be placed OUTSIDE any `\\text{}` block, on their own line.
   CORRECT: `\\text{explanation}\\\\ \\\\ ![img-x.jpeg](img-x.jpeg)`
   WRONG: `\\text{explanation \\\\ ![img-x.jpeg](img-x.jpeg)}`
12. ABSOLUTELY NO MULTIPLE CHOICE QUESTIONS: NEVER output multiple choice questions. If any input cards contain MCQ format or list choices (A, B, C, D), you MUST convert them into direct, open-ended conceptual questions without listed options.

For more detail, here are the exact same rules as the primary generator (that has to be followed):
    RULES (CRITICAL):
    1. LANGUAGE (STRICT LIMITATION): The generated text MUST be in the EXACT SAME LANGUAGE as the source text. NEVER translate.
    2. ZERO-PRONOUN & CONTEXT SCRUBBING (ABSOLUTELY CRITICAL): Flashcards are viewed out of order. You MUST aggressively SCRUB and REMOVE any phrases like "In Example 1", "As we saw in the previous section", "The following theorem", or "This equation". If the textbook says "In Example 1, Green's theorem is verified...", you MUST rephrase it to be standalone: "Verify Green's theorem for the functions...". Never assume the student has the surrounding textbook! ABSOLUTELY NO BLIND REFERENCES: If the text says 'By Theorem 2.1', you MUST replace it by stating exactly what the theorem says. Never use blind pointers like 'Proposition 5.1' or 'Equation 17'.
    3. PRESERVATION: Include ALL theorems, definitions, proofs, remarks, and examples exactly as they appear in the course. Do not condense important details.
    4. JSON BACKSLASH ESCAPING: Because you are generating JSON, you MUST double-escape EVERY single backslash (`\\frac`, `\\text`).
        - For ALL cards, write the text assuming it is inside a mathematical `aligned` block.
        - Every visual line MUST start with the alignment character `& ` to ensure left-alignment.
        - To break lines, use LaTeX line breaks `\\\\`.
        - Use `\text{...}` for ALL standard readable text. **PAY ATTENTION TO SPACES** inside `\text{...}`!
        - **LINE WRAPPING LIMIT:** Manually wrap lines exceeding 75 chars by closing the current `\text{}`, outputting `\\\\`, and starting anew.
        - NEVER place line breaks `\\\\` or alignment characters `& ` INSIDE a cloze deletion.
    5. IMAGES: You MUST NOT drop any image! Embed any image reference (e.g. `![img-0.jpeg](img-0.jpeg)`) in the most relevant flashcard EXACTLY as `![image_name](image_name)`. Let the image stand on a broken line via `\\\\`.
    6. CLOZE FORMAT: Use DOUBLE SQUARE BRACKETS `[[c1::...]]` to define clozes. NEVER use curly braces! When clozing natural language, the cloze MUST be placed INSIDE the \text{} block. Example: \text{The process is [[c1::convolution]]}. NEVER put \text{} inside the cloze.

    RULES SPECIFIC TO THEOREMS AND DEFINITIONS (MANDATORY EXPECTATIONS):
        IF THE CONTENT IS A THEOREM, PROPOSITION, COROLLARY, OR PROPERTY:
        - ZERO-FRAGMENTATION RULE: You MUST GENERATE EXACTLY ONE COMPREHENSIVE CARD for the entire Theorem/Proposition unit. DO NOT fragment the proof or remarks into separate flashcards or separate cloze cards.
        - Subdeck: MUST be "À Refaire"
        - Card Type: MUST be "Basique" or "Texte à trous"
        - `front` (Recto): You have 3 valid options:
            1. A clear question (e.g., "\text{State the Green's theorem}")
            2. The exact name of the theorem
            3. The exact statement of the theorem but with cloze deletions `[[c1::...]]`.
        - `back` (Verso) CRITICAL REQUIREMENT:
            1. If `front` used a clozed statement, put the ENTIRE UNC-LOZED statement here first.
            2. THEN, you MUST INCLUDE THE ENTIRE COMPLETE DEMONSTRATION/PROOF from the text, exactly as provided. DO NOT summarize it. DO NOT skip equations. It is essential the student learns to reproduce the full proof.
            3. THEN, include any remarks, corollaries, or examples that immediately follow it in the text.
            This guarantees that all context is physically printed on the back of the ONE theorem card.
        IF THE CONTENT IS AN EXAMPLE OR AN EXERCISE:
        - Subdeck: MUST be "À Refaire"
        - Card Type: MUST be "Basique" or "Texte à trous"
        - `front` CRITICAL SELF-CONTAINMENT RULE: You MUST make the card completely self-contained. ABSOLUTELY NEVER refer to an example name (e.g., REMOVE "In Example 1..."). The student looking at the card does not have the book. You MUST write out the ENTIRE problem statement, all contextual equations, given values, and the exact question to solve explicitly on the front.
        - `back`: Provide the complete, step-by-step resolution of the example/exercise.
        IF THE CONTENT IS A DEFINITION, VOCABULARY, OR FACTUAL KNOWLEDGE:
        - Subdeck: MUST be "Par Cœur"
        - Card Type: "Texte à trous" or "Généralités"
        - `front`: Ask for the definition or present the definition with clozes.
        - `back`: Provide the exact, concise definition.
        - If using "Généralités" (two-sided), replace the defined concept name on the back with a pronoun (e.g., "It", "They").

OUTPUT STRICTLY JSON in this format:
{
    "reasoning": "Explain your decision on whether these cards are truly duplicates and should be merged, or if some/all cover different concepts and should be kept separate.",
    "final_cards": [
        {
            "id": <INTEGER: MUST be the ID of the master card, or the original ID of the card if kept separate>,
            "type": "<Select from inputs>",
            "subdeck": "<Select from inputs>",
            "front": "\\text{... merged explicit question ...}",
            "back": "\\text{... master merged proof/answer ...}",
            "tags": "<Concatenation of all unique tags from input cards, space-separated>"
        }
    ]
}
NOTE FOR OUTPUT: If you decide to merge them, return exactly 1 merged card with the `id` of the earliest card in the group. If you decide they are different/distinct, return them as separate objects retaining their original `id` from the inputs.
"""

    original_len = len(cards)
    fusion_lock = threading.Lock()
    
    def process_fusion_group(group):
        if not group or len(group) <= 1:
            return
            
        group_cards = [{"id": i, "front": cards[i].get("front", ""), "back": cards[i].get("back", ""), "type": cards[i].get("type", ""), "subdeck": cards[i].get("subdeck", ""), "tags": cards[i].get("tags", "")} for i in group if i < len(cards)]
        master_id = group[0]
        
        # Enrichir le message avec les descriptions d'images si disponibles
        image_ctx = ""
        if image_descriptions:
            image_ctx = "\n\n[INDEX DES IMAGES ET LEURS DESCRIPTIONS]\n" + "\n".join([f"- {k}: {v}" for k, v in image_descriptions.items() if v])
        
        group_json = json.dumps(group_cards, ensure_ascii=False)
        
        # --- LOG TERMINAL : Affichage du groupe ---
        print(f"\n      ────────────────────────────────────────")
        print(f"      [FUSION] Groupe Master ID: {master_id} ({len(group)} cartes)")
        for idx, gid in enumerate(group):
            prefix = "└─" if idx == len(group) - 1 else "├─"
            front_preview = cards[gid].get("front", "")[:70].replace("\n", " ")
            print(f"        {prefix} Carte {gid}: \"{front_preview}...\"")
        
        for attempt in range(retries):
            try:
                response = client.chat.complete(
                    model=model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": prompt_fuse},
                        {"role": "user", "content": f"Cartes à fusionner :{image_ctx}\n\n{group_json}"}
                    ]
                )
                content = response.choices[0].message.content
                content = fix_llm_json_escaping(content)
                
                DEBUG_SUPERVISOR = os.environ.get("ANKI_DEBUG_SUPERVISOR", "0") == "1"
                if DEBUG_SUPERVISOR:
                    with open(f"last_supervisor_fusion_group_{master_id}.txt", "w", encoding="utf-8") as f:
                        f.write(content)

                data = json.loads(content)
                final_cards = data.get("final_cards", [])
                reasoning = data.get("reasoning", "Non spécifié")
                
                if final_cards:
                    with fusion_lock:
                        all_deleted_ids.update(group)
                        
                        kept_ids = []
                        for c in final_cards:
                            target_id = c.get("id")
                            if target_id is not None and target_id in group:
                                cards[target_id] = c
                                if target_id in all_deleted_ids:
                                    all_deleted_ids.remove(target_id)
                                kept_ids.append(target_id)
                            else:
                                # Fallback : placer la carte à la position du master_id (pas en fin de liste) 
                                # pour préserver l'ordre chronologique
                                if master_id not in all_deleted_ids:
                                    # master_id déjà sauvé, ajouter après
                                    cards[master_id] = c
                                else:
                                    cards[master_id] = c
                                    all_deleted_ids.remove(master_id)
                                    kept_ids.append(master_id)
                        
                        deleted_in_group = [gid for gid in group if gid in all_deleted_ids]
                        
                        # --- LOG TERMINAL : Résultat ---
                        decision = "FUSION" if len(final_cards) < len(group) else "CONSERVÉES SÉPARÉMENT"
                        print(f"      → Décision: {decision} ({len(group)} → {len(final_cards)} carte(s))")
                        for kid in kept_ids:
                            status = "FUSIONNÉE" if len(final_cards) < len(group) else "CONSERVÉE"
                            absorbed = [gid for gid in group if gid != kid and gid in all_deleted_ids]
                            absorb_str = f" (absorbe {absorbed})" if absorbed and status == "FUSIONNÉE" else ""
                            print(f"        ✓ Carte {kid}: {status}{absorb_str}")
                        for did in deleted_in_group:
                            print(f"        ✗ Carte {did}: SUPPRIMÉE (fusionnée)")
                        print(f"      Rationnel: {reasoning[:120]}...")
                        
                        # --- LOG FICHIER : Enrichi avec le rationnel ---
                        try:
                            with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                                f.write(f"## [FUSION SUPERVISEUR] Groupe Master ID: {master_id}\n\n")
                                f.write(f"**Décision:** {decision} ({len(group)} → {len(final_cards)} carte(s))\n\n")
                                f.write(f"**Rationnel du Combiner:**\n> {reasoning}\n\n")
                                f.write(f"### Cartes Originales:\n```json\n{group_json}\n```\n\n")
                                f.write(f"### Résultat Combiner:\n```json\n{json.dumps(final_cards, ensure_ascii=False, indent=2)}\n```\n\n")
                                f.write(f"**IDs conservés:** {kept_ids} | **IDs supprimés:** {deleted_in_group}\n\n---\n")
                        except Exception as e:
                            print(f"Log Error: {e}")
                        
                    break
                else:
                    print(f"      - Échec de parsing JSON Combiner pour le groupe {master_id} (Tentative {attempt+1})...")
            except Exception as e:
                import time
                print(f"      - Erreur Fusion groupe {master_id} (Tentative {attempt+1}): {e}")
                time.sleep(2)
        print(f"      ────────────────────────────────────────")
        
    with ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(process_fusion_group, duplicate_groups))
                
    # Reconstruction ordonnée : ne garder que les cartes non supprimées, dans l'ordre original
    deduplicated_cards = [c for i, c in enumerate(cards) if i not in all_deleted_ids and i < original_len]
    # Ajouter les éventuelles cartes ajoutées au-delà de la liste originale (fallback rares)
    for i in range(original_len, len(cards)):
        if i not in all_deleted_ids:
            deduplicated_cards.append(cards[i])
    
    try:
        with open("pipeline_logs.md", "a", encoding="utf-8") as f:
            f.write("## [RÉSULTAT DU PROCESSUS DE FUSION / DÉDUPLICATION]\n\n")
            f.write(f"**Nombre de cartes avant déduplication:** {original_len}\n\n")
            f.write(f"**Nombre de cartes après déduplication:** {len(deduplicated_cards)}\n\n")
            f.write(f"**Cartes supprimées (IDs):** {sorted(all_deleted_ids)}\n\n")
            f.write("### Cartes Finales Post-Fusion (Rectos uniquement):\n```json\n")
            f.write(json.dumps([{"id": j, "front": c.get("front", "")} for j, c in enumerate(deduplicated_cards)], ensure_ascii=False, indent=2))
            f.write("\n```\n\n---\n")
    except Exception as e:
        print(f"Log Error: {e}")

    return deduplicated_cards

class LatexSanitizer:
    @staticmethod
    def fix_double_backslash_text(text):
        """Fix \\\\text -> \\text, \\\\frac -> \\frac etc. caused by QA agent over-escaping.
        Also recovers orphaned LaTeX commands (ext{ -> \\text{) and replaces unsupported \\tag{} with \\text{}."""
        if not text: return text
        import re
        # Pattern: double-backslash followed by known LaTeX commands
        text = re.sub(r'\\\\(text|frac|sqrt|left|right|begin|end|quad|operatorname|mathrm|mathbf|mathit|vec|boldsymbol|max|min|lim|sin|cos|tan|log|ln|exp|det|dim|ker|Im|Re|eta|nu|rho|tau|alpha|beta|gamma|delta|epsilon|lambda|mu|sigma|omega|phi|psi|theta|pi|nabla|partial|infty|sum|prod|int|cup|cap|cdot|times|pm|mp|leq|geq|neq|approx|equiv|propto|forall|exists|in|subset|supset|to|mapsto|circ|otimes|oplus|oint|iint)\b', r'\\\1', text)
        
        # V0.98 FIX: Orphan backslash recovery
        # When JSON parser consumes \t, \f, \n, \r, \b as control chars,
        # \text{} -> TAB+"ext{}", \frac{} -> FF+"rac{}", etc.
        # Detect control-char + orphan suffix and restore the LaTeX command.
        _orphan_fixes = [
            ('\t', 'ext', 'text'),     # \text -> TAB + ext
            ('\t', 'imes', 'times'),   # \times -> TAB + imes
            ('\t', 'heta', 'theta'),   # \theta -> TAB + heta
            ('\t', 'au', 'tau'),       # \tau -> TAB + au
            ('\t', 'an', 'tan'),       # \tan -> TAB + an
            ('\f', 'rac', 'frac'),     # \frac -> FF + rac
            ('\n', 'u', 'nu'),         # \nu -> NL + u
            ('\n', 'abla', 'nabla'),   # \nabla -> NL + abla
            ('\n', 'e', 'ne'),         # \ne -> NL + e
            ('\r', 'ho', 'rho'),       # \rho -> CR + ho
            ('\r', 'ight', 'right'),   # \right -> CR + ight
            ('\b', 'eta', 'beta'),     # \beta -> BS + eta
            ('\b', 'egin', 'begin'),   # \begin -> BS + egin
            ('\b', 'oldsymbol', 'boldsymbol'),  # \boldsymbol -> BS + oldsymbol
        ]
        for ctrl_char, suffix, full_cmd in _orphan_fixes:
            text = text.replace(ctrl_char + suffix, '\\' + full_cmd)
        
        # Also handle rare cases where control char was stripped entirely
        # leaving just the suffix at word boundaries
        _orphan_suffixes = {
            'ext{': r'\\text{',
            'rac{': r'\\frac{',
            'qrt{': r'\\sqrt{',
        }
        for suffix, replacement in _orphan_suffixes.items():
            # Only at start of string or after non-alpha non-backslash
            text = re.sub(r'(^|[^a-zA-Z\\\\])' + re.escape(suffix), 
                          lambda m: m.group(1) + replacement.replace(r'\\\\', '\\'), text)
        
        # V0.98 FIX: Replace \tag{...} with \text{    ...}
        # MathJax in Anki's aligned environment does not support \tag{}.
        # We replace it with \text{    X.Y.Z} (with leading spaces for visual separation).
        text = re.sub(r'\\tag\{([^}]*)\}', lambda m: r'\text{    ' + m.group(1) + '}', text)
        
        # FAILSAFE: Supprimer les environnements non supportés (itemize, enumerate, itemsize) et les symboles $
        text = re.sub(r'\\begin\{(itemize|enumerate|itemsize)\}', '', text)
        text = re.sub(r'\\end\{(itemize|enumerate|itemsize)\}', '', text)
        text = re.sub(r'\\item\s*', '- ', text)
        text = text.replace('$', '')
        
        return text


    @staticmethod
    def extract_images_from_text_blocks(text):
        """Rescue image references buried inside \\text{} blocks by extracting them outside."""
        if not text: return text
        import re
        def _fix_text_block_with_image(match):
            full = match.group(0)
            # Find images inside this \text{} block (now they are HTML tags)
            images = re.findall(r'<img[^>]+>', full)
            if not images:
                return full
            # Remove images from inside the \text{} block
            cleaned = re.sub(r'<img[^>]+>', ' ', full)
            # Remove excessive backslashes/whitespace left behind
            cleaned = re.sub(r'\\{3,}', '', cleaned)
            cleaned = cleaned.strip()
            # Build image references outside \text{}
            img_strs = [f' \\\\ \\\\ {img}' for img in images]
            return cleaned + ''.join(img_strs)
        
        # Match \text{...} blocks that contain <img ...> tags
        pattern = r'\\text\{[^}]*(?:<img[^>]+>)[^}]*\}'
        text = re.sub(pattern, _fix_text_block_with_image, text)
        return text

    @staticmethod
    def fix_spaces(text):
        if not text: return text
        import re
        text = re.sub(r'\}\s+\\(mathbf|mathit|vec|text|mathrm|boldsymbol)\b', r'} \\\1', text)
        text = re.sub(r'\}\s+([a-zA-Z0-9])(?![a-zA-Z])', r'} \1', text)
        text = re.sub(r'\}\s+\{\{c', r'} {{c', text)
        return text

    @staticmethod
    def balance_braces(text):
        if not text: return text
        result = []
        depth = 0
        i = 0
        while i < len(text):
            if text[i:i+2] in ['\\{', '\\}']:
                result.append(text[i:i+2])
                i += 2
                continue
            if text[i] == '{':
                depth += 1
                result.append('{')
                i += 1
            elif text[i] == '}':
                if depth > 0:
                    depth -= 1
                    result.append('}')
                i += 1
            else:
                result.append(text[i])
                i += 1
        while depth > 0:
            result.append('}')
            depth -= 1
        return "".join(result)

    @staticmethod
    def wrap_latex(text, max_len=75):
        if not text: return text
        import re
        
        # Pass 1: Break long \text{...} blocks
        result_p1 = []
        i = 0
        while i < len(text):
            if text[i:].startswith(r'\text{'):
                prefix = r'\text{'
                j = i + len(prefix)
                depth = 1
                inner = []
                while j < len(text) and depth > 0:
                    if text[j] == '{':
                        depth += 1
                    elif text[j] == '}':
                        depth -= 1
                    if depth > 0:
                        inner.append(text[j])
                    j += 1
                inner_str = "".join(inner)
                
                # V0.99 FIX: Extraire les commandes mathématiques coincées dans les \text{}
                # (ex: \eta_{th}, \frac{W}{Q}, W_{net}) en les sortant avec } ... \text{
                greek_or_sym = r'\\(?:alpha|beta|gamma|delta|epsilon|varepsilon|zeta|eta|theta|vartheta|iota|kappa|lambda|mu|nu|xi|pi|rho|sigma|tau|upsilon|phi|varphi|chi|psi|omega|Gamma|Delta|Theta|Lambda|Xi|Pi|Sigma|Upsilon|Phi|Psi|Omega|sum|prod|int|approx|neq|leq|geq|times|cdot|infty|partial|nabla)'
                sub_super = r'(?:_\{[^\}]+\}|\^\{[^\}]+\}|_[a-zA-Z0-9]|\^[a-zA-Z0-9])'
                
                p_frac = r'\\frac\{[^\}]+\}\{[^\}]+\}'
                p_greek = f'{greek_or_sym}{sub_super}?'
                p_var = f'[a-zA-Z]{sub_super}'
                p_fmt = r'\\(?:textbf|textit|underline|mathbf|mathit)\{[^\}]+\}'
                
                math_pattern = f'({p_frac}|{p_greek}|{p_var}|{p_fmt})'
                inner_str = re.sub(math_pattern, r'} \1 \\text{', inner_str)
                # Nettoyer les \text{} vides qui auraient pu être créés par l'extraction
                inner_str = inner_str.replace(r'\text{}', '')
                
                # Check if we need to wrap the internal string
                if len(inner_str) > max_len:
                    words = []
                    curr_word = []
                    brace_depth = 0
                    bracket_depth = 0
                    for char in inner_str:
                        if char == '{': brace_depth += 1
                        elif char == '}': brace_depth = max(0, brace_depth - 1)
                        elif char == '[': bracket_depth += 1
                        elif char == ']': bracket_depth = max(0, bracket_depth - 1)
                        
                        if char == ' ' and brace_depth == 0 and bracket_depth == 0:
                            if curr_word:
                                words.append("".join(curr_word))
                                curr_word = []
                        else:
                            curr_word.append(char)
                    if curr_word:
                        words.append("".join(curr_word))

                    lines_out = []
                    cur_line = []
                    cur_len = 0
                    for w in words:
                        # Remove cloze tags to calculate visible length
                        vis = len(re.sub(r'(\{\{c\d+::|\[\[c\d+::|\[\[|\{\{|\]\]|\}\})', '', w))
                        if cur_len + vis + 1 > max_len and cur_line:
                            lines_out.append(" ".join(cur_line))
                            cur_line = [w]
                            cur_len = vis
                        else:
                            cur_line.append(w)
                            cur_len += vis + 1
                    if cur_line:
                        lines_out.append(" ".join(cur_line))
                    
                    wrapped_text = r"} \\\\ & \text{".join(lines_out)
                    result_p1.append(r"\text{" + wrapped_text + r"}")
                else:
                    result_p1.append(r"\text{" + inner_str + r"}")
                i = j
            else:
                result_p1.append(text[i])
                i += 1
                
        text = "".join(result_p1)
        
        # Pass 2: Math Equation wrapping
        # Reverted to max_len (75 chars) as requested in V0.99, while keeping smart breaking rules
        math_max_len = max_len
        
        words = []
        curr_word = []
        depth = 0
        bracket_depth = 0
        html_depth = 0
        i = 0
        while i < len(text):
            char = text[i]
            if char == '{': depth += 1
            elif char == '}': depth = max(0, depth - 1)
            elif char == '[': bracket_depth += 1
            elif char == ']': bracket_depth = max(0, bracket_depth - 1)
            elif char == '<': html_depth += 1
            elif char == '>': html_depth = max(0, html_depth - 1)
            
            if char.isspace() and depth == 0 and html_depth == 0 and bracket_depth == 0:
                if curr_word:
                    words.append("".join(curr_word))
                    curr_word = []
            else:
                curr_word.append(char)
            i += 1
        if curr_word:
            words.append("".join(curr_word))
            
        wrapped_lines = []
        current_chunk = []
        current_len = 0
        left_depth = 0
        env_depth = 0
        
        # V0.98: Operators/tokens that should never be the LAST word before a line break
        # (i.e., don't leave an integral sign alone at the end of a line)
        no_break_after = {r'\int', r'\iint', r'\iiint', r'\oint', r'\sum', r'\prod',
                          r'\lim', r'\sup', r'\inf', r'\max', r'\min',
                          '=', '+', '-', r'\cdot', r'\times', r'\pm', r'\mp',
                          r'\leq', r'\geq', r'\neq', r'\approx', r'\equiv',
                          r'\to', r'\mapsto', r'\Rightarrow', r'\Leftarrow',
                          r'\implies', r'\iff'}
        
        # V0.98: Tokens that should never be the FIRST word after a line break
        # (i.e., don't push 'dx', 'dt', 'ds' onto the next line alone)
        no_break_before_patterns = re.compile(
            r'^(?:d[xtspru]|d\\[a-zA-Z]+|\\,\\s*d[xtspru]|\\[,;!]\s*d[xtspru])$'
        )
        
        for idx_w, w in enumerate(words):
            if w == r'\\':
                if env_depth == 0 and left_depth == 0:
                    if current_chunk:
                        wrapped_lines.append(" ".join(current_chunk))
                    current_chunk = []
                    current_len = 0
                    continue
                else:
                    current_chunk.append(w)
                    current_len += 2
                    continue
                    
            env_depth += w.count(r'\begin{') - w.count(r'\end{')
            left_depth += w.count(r'\left') - w.count(r'\right')
            
            # V0.98: Track subscript/superscript depth to avoid breaking inside _{...} or ^{...}
            sub_sup_depth = 0
            for ci in range(len(w) - 1):
                if w[ci] in ('_', '^') and ci + 1 < len(w) and w[ci + 1] == '{':
                    sub_sup_depth += 1
                elif w[ci] == '{' and ci > 0 and w[ci - 1] in ('_', '^'):
                    pass  # already counted
                elif w[ci] == '}' and sub_sup_depth > 0:
                    sub_sup_depth -= 1
            
            vis_len = len(re.sub(r'\\[a-zA-Z]+', '', w))
            can_break = (left_depth == 0 and env_depth == 0 
                        and w.count(r'\right') == 0 and w.count(r'\end{') == 0
                        and sub_sup_depth == 0)
            
            # V0.98: Additional anti-break checks
            if can_break and current_chunk:
                last_word = current_chunk[-1] if current_chunk else ""
                # Don't break if previous word is an operator that should keep its operand
                if last_word in no_break_after:
                    can_break = False
                # Don't break if current word is a differential (dx, dt, ds...)
                if no_break_before_patterns.match(w):
                    can_break = False
            
            if current_chunk and (current_len + vis_len > math_max_len) and can_break:
                wrapped_lines.append(" ".join(current_chunk))
                current_chunk = [w]
                current_len = vis_len
            else:
                current_chunk.append(w)
                current_len += vis_len + 1
                
        if current_chunk:
            wrapped_lines.append(" ".join(current_chunk))
            
        res = []
        for line in wrapped_lines:
            line = line.strip()
            # FIX V0.99: Éviter les doubles & en début de ligne (ex: & &q_{in} = ...)
            line = re.sub(r'^(&\s*)+', '& ', line)
            if line and not line.startswith('&') and not line.startswith(r'\begin'):
                line = '& ' + line
            res.append(line)
        return " \\\\ \n".join(res)

    @staticmethod
    def _robust_cloze_replacer(t_str):
        import re
        result = []
        i = 0
        while i < len(t_str):
            match = re.match(r'\{\{c\d+::', t_str[i:])
            if match:
                prefix = match.group(0)
                j = i + len(prefix)
                depth = 0
                inner = []
                while j < len(t_str):
                    if t_str[j] == '{': depth += 1; inner.append('{')
                    elif t_str[j] == '}':
                        if depth == 0:
                            if j + 1 < len(t_str) and t_str[j+1] == '}':
                                j += 2
                                break
                            else: inner.append('}')
                        else: depth -= 1; inner.append('}')
                    else: inner.append(t_str[j])
                    j += 1
                inner_str = "".join(inner).replace("}}", "} }")
                result.append(prefix + inner_str + "}}")
                i = j
            else: result.append(t_str[i]); i += 1
        return "".join(result)

    @staticmethod
    def process_aligned_wrapper(text):
        if not text: return text
        import re
        # Fix double-backslash before LaTeX commands (QA over-escaping)
        text = LatexSanitizer.fix_double_backslash_text(text)
        # Rescue images buried inside \text{} blocks
        text = LatexSanitizer.extract_images_from_text_blocks(text)
        text = LatexSanitizer.wrap_latex(text)
        text = LatexSanitizer._robust_cloze_replacer(text)
        
        # Cleanup empty text artifacts from aggressive regexes
        text = text.replace(r'\text{}', '')
        # Clean up stray "]." or "].]" artifacts
        text = re.sub(r'\]\.\]', '', text)
        text = re.sub(r'\]\.$', '', text)
        
        res = "\\( \\begin{aligned} \n" + text + "\n \\end{aligned} \\)"
        res = res.replace("\n", " ")
        # Nettoyer les sauts de ligne parasites (doubles \\ consécutifs)
        res = re.sub(r'(\\\\\s*){2,}', r'\\\\ ', res)
        # Supprimer les lignes vides d'alignement (& suivi immédiatement de \\)
        res = re.sub(r'\\\\\s*&\s*\\\\', r'\\\\', res)
        res = re.sub(r'(<img[^>]+>)', r'\\end{aligned}\\)<br>\1<br>\\(\\begin{aligned} & ', res)
        # Nettoyage robuste des blocs aligned vides (plusieurs patterns possibles)
        res = res.replace("\\( \\begin{aligned}   \\end{aligned} \\)", "")
        res = res.replace("\\(\\begin{aligned} &  \\end{aligned} \\)", "")
        res = re.sub(r'\\\(\s*\\begin\{aligned\}\s*[&\s]*\\end\{aligned\}\s*\\\)', '', res)
        # Supprimer les <br> orphelins en début/fin
        res = re.sub(r'^(<br>\s*)+', '', res)
        res = re.sub(r'(<br>\s*)+$', '', res)
        return res

    @staticmethod
    def extract_clozes(t_str, target_cloze_num=None):
        import re
        result = []
        i = 0
        while i < len(t_str):
            match = re.match(r'\{\{c(\d+)::', t_str[i:])
            if match:
                c_num = match.group(1)
                prefix = match.group(0)
                j = i + len(prefix)
                depth = 0
                inner = []
                while j < len(t_str):
                    if t_str[j] == '{': depth += 1; inner.append('{')
                    elif t_str[j] == '}':
                        if depth == 0:
                            if j + 1 < len(t_str) and t_str[j+1] == '}':
                                j += 2
                                break
                            else: inner.append('}')
                        else: depth -= 1; inner.append('}')
                    else: inner.append(t_str[j])
                    j += 1
                inner_str = "".join(inner)
                if target_cloze_num is None:
                    # Reveal mode
                    result.append(inner_str)
                else:
                    if c_num == str(target_cloze_num):
                        # (...) will behave correctly because it is inside \text{}
                        result.append(r"(...)")
                    else:
                        # Reveal OTHER clozes
                        result.append(inner_str)
                i = j
            else: 
                result.append(t_str[i])
                i += 1
        return "".join(result)

def add_card_to_decks(deck_par_coeur, deck_a_refaire, card):
    card_type = card.get("type", "Basique").strip()
    subdeck_choice = card.get("subdeck", "Par Cœur").strip()
    mapped_tag = "Catégorie::" + subdeck_choice.replace(" ", "_").replace(",", "")
    
    import re
    raw_front = card.get("front", "").strip()
    raw_front = re.sub(r'\[\[c(\d+)::(.*?)]]', r'{{c\1::\2}}', raw_front, flags=re.DOTALL)
    raw_front_lower = raw_front.lower()
    
    is_a_refaire = "refaire" in subdeck_choice.lower()
    a_refaire_keywords = ["théorème", "theorem", "proposition", "corollaire", "propriété", "lemme", "exemple", "exercice", "demonstration", "démonstration"]
    if any(kw in raw_front_lower for kw in a_refaire_keywords):
        is_a_refaire = True
    elif "définition" in raw_front_lower or "definition" in raw_front_lower:
        is_a_refaire = False
        
    deck = deck_a_refaire if is_a_refaire else deck_par_coeur
    raw_back = card.get("back", "").strip()
    raw_back = re.sub(r'\[\[c(\d+)::(.*?)]]', r'{{c\1::\2}}', raw_back, flags=re.DOTALL)
    
    raw_front = re.sub(r'\\n(?![a-zA-Z])', ' ', raw_front)
    raw_back = re.sub(r'\\n(?![a-zA-Z])', ' ', raw_back)
    
    # Échappement HTML ciblé : seulement < et > pour la sécurité HTML
    # Ne PAS échapper & (utilisé par LaTeX pour l'alignement dans \begin{aligned})
    front_escaped = raw_front.replace("<", "&lt;").replace(">", "&gt;")
    back_escaped = raw_back.replace("<", "&lt;").replace(">", "&gt;")
    
    robust_img_pattern = r'\\*!?\\*\[([^\]]*?)\\*\]\\*\(([^)]+?\.(?:jpeg|jpg|png|gif|webp|svg))\\*\)'
    front_escaped = re.sub(robust_img_pattern, r'<img src="\2">', front_escaped, flags=re.IGNORECASE)
    back_escaped = re.sub(robust_img_pattern, r'<img src="\2">', back_escaped, flags=re.IGNORECASE)
    
    # Fix double-quotes artefacts dans les img src
    front_escaped = front_escaped.replace('""', '"')
    back_escaped = back_escaped.replace('""', '"')

    # RESTORE ORDER: Strip alignment BEFORE balancing braces to fix hallucinated \end{aligned} inside \text{...}
    front_escaped = re.sub(r'\\begin\{(aligned|align\*?)\}', '', front_escaped)
    front_escaped = re.sub(r'\\end\{(aligned|align\*?)\}', '', front_escaped)
    back_escaped = re.sub(r'\\begin\{(aligned|align\*?)\}', '', back_escaped)
    back_escaped = re.sub(r'\\end\{(aligned|align\*?)\}', '', back_escaped)
    front_escaped = re.sub(r'(?<!\\)\\\[', '', front_escaped)
    front_escaped = re.sub(r'(?<!\\)\\\]', '', front_escaped)
    back_escaped = re.sub(r'(?<!\\)\\\[', '', back_escaped)
    back_escaped = re.sub(r'(?<!\\)\\\]', '', back_escaped)
    front_escaped = front_escaped.replace(r'\(', '').replace(r'\)', '')
    back_escaped = back_escaped.replace(r'\(', '').replace(r'\)', '')

    pre_sanitizer_front = front_escaped
    pre_sanitizer_back = back_escaped
    
    is_cloze = "trous" in card_type.lower() and "{{c" in front_escaped
    is_generalite = "Généralités" in card_type or "G\u00e9n\u00e9ralit\u00e9s" in card_type
    if "{{c" in front_escaped or "{{c" in back_escaped:
        is_cloze = True

    front_escaped = LatexSanitizer.balance_braces(front_escaped)
    back_escaped = LatexSanitizer.balance_braces(back_escaped)
    front_escaped = LatexSanitizer.fix_spaces(front_escaped)
    back_escaped = LatexSanitizer.fix_spaces(back_escaped)

    tags_str = card.get("tags", "").strip().replace(",", " ")
    tags = [t for t in tags_str.split(" ") if t]
    if mapped_tag not in tags:
        tags.append(mapped_tag)

    if is_cloze:
        cloze_numbers = set(re.findall(r'\{\{c(\d+)::', front_escaped + back_escaped))
        if not cloze_numbers:
            front = LatexSanitizer.process_aligned_wrapper(front_escaped)
            back = LatexSanitizer.process_aligned_wrapper(back_escaped)
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [LATEX SANITIZER] Basique/Généralités (Trous Vides)\n\n")
                    f.write(f"### Avant:\n**Front:**\n```\n{pre_sanitizer_front}\n```\n\n**Back:**\n```\n{pre_sanitizer_back}\n```\n\n")
                    f.write(f"### Après:\n**Front:**\n```\n{front}\n```\n\n**Back:**\n```\n{back}\n```\n\n---\n")
            except: pass
            my_note = genanki.Note(model=model_basic, fields=[front, back], tags=tags)
            deck.add_note(my_note)
        else:
            sorted_clozes = sorted(cloze_numbers, key=int)
            fields = [""] * 10
            final_back = ""
            for idx, cloze_num in enumerate(sorted_clozes):
                if idx >= 10: break
                current_front = LatexSanitizer.extract_clozes(front_escaped, cloze_num)
                current_front_revealed = LatexSanitizer.extract_clozes(front_escaped, None)
                current_back_revealed = LatexSanitizer.extract_clozes(back_escaped, None)
                
                final_front = LatexSanitizer.process_aligned_wrapper(current_front)
                
                # V0.98 FIX: Cartes soeurs vides
                # Verifier si le recto est vide une fois debarrasse des balises MathJax
                clean_front = re.sub(r'\\\(\s*\\begin\{aligned\}', '', final_front)
                clean_front = re.sub(r'\\end\{aligned\}\s*\\\)', '', clean_front)
                clean_front = clean_front.replace('<br>', '').strip()
                
                if not clean_front:
                    print(f"      [AVERTISSEMENT] Carte soeur vide ignoree pour le cloze {cloze_num}")
                    continue
                
                final_front_revealed = LatexSanitizer.process_aligned_wrapper(current_front_revealed)
                
                if current_back_revealed.strip():
                    final_back_extra = LatexSanitizer.process_aligned_wrapper(current_back_revealed)
                    final_back = f"{final_front_revealed}<br><hr><br>{final_back_extra}"
                else:
                    final_back = final_front_revealed
                fields[idx] = final_front
                
            fields.append(final_back)
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [LATEX SANITIZER] Carte à Trous\n\n")
                    f.write(f"### Avant:\n**Front:**\n```\n{pre_sanitizer_front}\n```\n\n**Back:**\n```\n{pre_sanitizer_back}\n```\n\n### Après (Cartes Sœurs):\n")
                    for i in range(min(10, len(sorted_clozes))):
                        f.write(f"**Front {i+1}:**\n```\n{fields[i]}\n```\n\n")
                    f.write(f"**Back Final:**\n```\n{final_back}\n```\n\n---\n")
            except: pass
            my_note = genanki.Note(model=model_cloze_siblings, fields=fields, tags=tags)
            deck.add_note(my_note)
    else:
        front = LatexSanitizer.process_aligned_wrapper(front_escaped)
        back = LatexSanitizer.process_aligned_wrapper(back_escaped)
        try:
            with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                f.write("## [LATEX SANITIZER] Basique/Généralités\n\n")
                f.write(f"### Avant:\n**Front:**\n```\n{pre_sanitizer_front}\n```\n\n**Back:**\n```\n{pre_sanitizer_back}\n```\n\n")
                f.write(f"### Après:\n**Front:**\n```\n{front}\n```\n\n**Back:**\n```\n{back}\n```\n\n---\n")
        except: pass
        if is_generalite:
            my_note = genanki.Note(model=model_generalites, fields=[front, back], tags=tags)
        else:
            my_note = genanki.Note(model=model_basic, fields=[front, back], tags=tags)
        deck.add_note(my_note)

def process_course():
    print("\n" + "="*50)
    print("GÉNÉRATEUR DE CARTES ANKI INFAILLIBLE (Mistral AI + Genanki)")
    print("="*50 + "\n")
    
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("ERREUR CRITIQUE: La variable d'environnement MISTRAL_API_KEY est introuvable.")
        print("Vérifiez votre fichier .env")
        return

    g_file = select_file()
    if not g_file:
        print("Opération annulée : Aucun fichier selectionné.")
        return
        
    client = Mistral(api_key=api_key)
    filename = os.path.basename(g_file)
    filename_without_ext = os.path.splitext(filename)[0]

    import datetime
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder_name = f"{filename_without_ext}_{timestamp_str}"
    
    try:
        os.makedirs(run_folder_name, exist_ok=True)
        os.chdir(run_folder_name)
        print(f"--> Environnement isolé : tous les fichiers (logs, images, deck) seront dans `{run_folder_name}`\n")
    except Exception as e:
        print(f"Erreur de création de dossier isolé : {e}")
        return

    try:
        print(f"1) Téléchargement de {filename} pour OCR Mistral...")
        with open(g_file, "rb") as f:
            uploaded_pdf = client.files.upload(
                file={
                    "file_name": filename,
                    "content": f,
                },
                purpose="ocr"
            )

        print("2) Traitement OCR en cours avec annotation d'images... (patientez plusieurs secondes)")
        signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "document_url",
                "document_url": signed_url.url,
            },
            table_format="markdown",
            include_image_base64=True,
            bbox_annotation_format=response_format_from_pydantic_model(ImageAnnotation)
        )
        
        client.files.delete(file_id=uploaded_pdf.id)

        import base64
        full_markdown = ""
        media_files = []
        image_descriptions = {}  # Dict: img_filename -> description string
        for page in ocr_response.pages:
            page_md = page.markdown
            if hasattr(page, 'images') and page.images:
                for img in page.images:
                    b64_str = img.image_base64
                    if b64_str.startswith("data:"):
                        b64_str = b64_str.split(",", 1)[1]
                    
                    img_filename = img.id
                    if not img_filename.endswith(('.jpg', '.jpeg', '.png')):
                        img_filename += ".jpg"
                        
                    with open(img_filename, "wb") as f_img:
                        f_img.write(base64.b64decode(b64_str))
                    media_files.append(img_filename)
                    
                    # Extraire l'annotation d'image (description) si disponible
                    # L'API Mistral OCR retourne les annotations dans img.image_annotation sous forme de string JSON
                    annotation_str = ""
                    if hasattr(img, 'image_annotation') and img.image_annotation:
                        try:
                            ann_raw = img.image_annotation
                            if isinstance(ann_raw, str):
                                parsed = json.loads(ann_raw)
                                annotation_str = f"[{parsed.get('image_type', 'unknown')}] {parsed.get('short_description', '')} (Concepts: {parsed.get('key_concepts', '')})"
                            elif isinstance(ann_raw, dict):
                                annotation_str = f"[{ann_raw.get('image_type', 'unknown')}] {ann_raw.get('short_description', '')} (Concepts: {ann_raw.get('key_concepts', '')})"
                            elif hasattr(ann_raw, 'image_type'):
                                annotation_str = f"[{ann_raw.image_type}] {ann_raw.short_description} (Concepts: {ann_raw.key_concepts})"
                        except Exception as e:
                            print(f"   Avertissement : impossible de parser l'annotation pour {img_filename}: {e}")
                    image_descriptions[img_filename] = annotation_str
                    
                    # Remplacement de l'ID d'image par le nom du fichier effectif dans le markdown
                    page_md = page_md.replace(f"({img.id})", f"({img_filename})")
            full_markdown += page_md + "\n\n"
            
        with open("extracted_course_text.md", "w", encoding="utf-8") as f:
            f.write(full_markdown)
        
        # Enrichir les annotations d'images avec les légendes/captions du texte source
        md_lines = full_markdown.split("\n")
        for img_name in list(image_descriptions.keys()):
            img_ref_pattern = f"![{img_name}]({img_name})"
            # Also search without alt text
            img_ref_pattern_noalt = f"![]({img_name})"
            found_line_idx = -1
            for li, line in enumerate(md_lines):
                if img_ref_pattern in line or img_ref_pattern_noalt in line:
                    found_line_idx = li
                    break
            if found_line_idx >= 0:
                # Extraire les 1-3 lignes suivantes comme légende potentielle
                caption_parts = []
                for offset in range(1, 4):
                    next_idx = found_line_idx + offset
                    if next_idx >= len(md_lines):
                        break
                    next_line = md_lines[next_idx].strip()
                    # Arrêter si on rencontre une autre image, un header, ou une ligne vide longue
                    if next_line.startswith('![') or next_line.startswith('#') or not next_line:
                        break
                    if len(next_line) > 3:
                        caption_parts.append(next_line)
                if caption_parts:
                    caption_text = " — ".join(caption_parts)
                    existing = image_descriptions[img_name]
                    image_descriptions[img_name] = f"{existing} | Caption: {caption_text}" if existing else f"Caption: {caption_text}"
                    print(f"   [IMAGE] {img_name}: légende enrichie avec '{caption_text[:60]}...'")
        
        # Sauvegarder les annotations d'images pour traçabilité
        annotated_count = sum(1 for v in image_descriptions.values() if v)
        if image_descriptions:
            with open("image_annotations.json", "w", encoding="utf-8") as f:
                json.dump(image_descriptions, f, ensure_ascii=False, indent=2)
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [OCR] Annotations d'images extraites\n\n")
                    for img_name, desc in image_descriptions.items():
                        f.write(f"- **{img_name}**: {desc if desc else '(aucune annotation)'}\n")
                    f.write(f"\n**Total:** {len(image_descriptions)} images, {annotated_count} annotées.\n\n---\n")
            except: pass
            
        print(f"3) OCR terminé avec succès ! ({len(full_markdown)} caractères extraits, {annotated_count}/{len(image_descriptions)} images annotées)")
        
        print("4) Découpage intelligent du cours en blocs sémantiques (Agent Splitter)...")
        chunks = semantic_split_with_ai(client, full_markdown)
        print(f"   => Cours découpé en {len(chunks)} blocs parfaits.")

        all_cards = []
        
        print("\n5) Analyse AI et génération JSON des cartes en cours (Mistral Large) :")
        
        def process_single_chunk(idx, chunk):
            if not chunk.strip():
                return idx, []
            print(f"   -> Traitement du bloc {idx+1}/{len(chunks)} (taille: {len(chunk)} chars)...")
            cards = extract_cards_from_chunk(client, chunk, filename_tag=filename_without_ext)
            cards = ai_quality_control_cards(client, cards, chunk_text=chunk, image_descriptions=image_descriptions)
            cards = filter_image_only_cards(cards)
            cards = filter_mcq_cards(cards)
            cards = filter_truncated_cards(cards)
            cards = audit_image_coverage(cards, chunk, image_descriptions=image_descriptions)
            return idx, cards

        chunk_results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_idx = {executor.submit(process_single_chunk, i, chunk): i for i, chunk in enumerate(chunks)}
            for future in as_completed(future_to_idx):
                idx, cards = future.result()
                chunk_results.append((idx, cards))
                
        # Tri des résultats pour maintenir l'ordre chronologique des blocs
        chunk_results.sort(key=lambda x: x[0])
        for _, cards in chunk_results:
            all_cards.extend(cards)
            
        print(f"\n5.5) Déduplication sémantique : {len(all_cards)} cartes en revue...")
        all_cards = supervisor_deduplicate_cards(client, all_cards, image_descriptions=image_descriptions)
        
        print(f"\n5.6) Assemblage final : {len(all_cards)} cartes générées, compilation du paquet Anki...")
        
        # Génération déterministe / pseudo-aléatoire des Deck IDs
        deck_id_1 = random.randrange(1 << 30, 1 << 31)
        deck_id_2 = random.randrange(1 << 30, 1 << 31)
        deck_name = f"{filename_without_ext}"
        
        deck_par_coeur = genanki.Deck(deck_id_1, f"{deck_name}::Par Cœur (Définitions)")
        deck_a_refaire = genanki.Deck(deck_id_2, f"{deck_name}::À Refaire (Théorèmes et Concepts)")
        
        for card in all_cards:
            add_card_to_decks(deck_par_coeur, deck_a_refaire, card)
            
        output_filename = f"{filename_without_ext}_Infaillible.apkg"
        my_package = genanki.Package([deck_par_coeur, deck_a_refaire])
        my_package.media_files = media_files
        my_package.write_to_file(output_filename)
                
        print(f"\n[SUCCÈS TOTAL] Votre deck Anki est prêt : {output_filename}")
        print("Vous pouvez double-cliquer dessus pour l'importer directement et parfaitement dans Anki !")

    except Exception as e:
        print(f"\n/!\\ UTILITAIRE INTERROMPU PAR UNE ERREUR /!\\ \n{e}")

if __name__ == "__main__":
    process_course()
