from pydantic import functional_serializers
import tkinter as tk
# Version 1.191 - Intégration des correctifs JSON Shield étendu, Leaked HTML Tags, MathJax Delimiters et Markdown Bold
from tkinter import filedialog
import time
import warnings
import random
import sys

# Forcer la gestion robuste des encodages de sortie pour éviter tout plantage sur Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
if hasattr(sys.stderr, 'reconfigure'):
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Silencer les avertissements de genanki concernant les faux tags HTML (< et > pour les maths)
warnings.filterwarnings("ignore", category=UserWarning)
import os
import json
import json_repair
import re
import threading
import contextlib
from concurrent.futures import ThreadPoolExecutor, as_completed

FILE_LOCK = threading.Lock()
PRINT_LOCK = threading.Lock()

# ------------------------------------------
# HOOKS DE SIGNALS / CALLBACKS POUR L'UI
# ------------------------------------------
UI_CALLBACK = None
PROGRESS_CALLBACK = None

def report_progress(stage, status_text, progress_ratio=0.0):
    global PROGRESS_CALLBACK
    if PROGRESS_CALLBACK:
        try:
            PROGRESS_CALLBACK(stage, status_text, progress_ratio)
        except Exception:
            pass

_original_print = print
def safe_print(*args, **kwargs):
    global UI_CALLBACK
    with PRINT_LOCK:
        try:
            _original_print(*args, **kwargs)
        except UnicodeEncodeError:
            safe_args = [
                arg.encode(sys.stdout.encoding or 'ascii', errors='replace').decode(sys.stdout.encoding or 'ascii')
                if isinstance(arg, str) else repr(arg)
                for arg in args
            ]
            try:
                _original_print(*safe_args, **kwargs)
            except Exception:
                pass
        
        if UI_CALLBACK:
            import io
            s = io.StringIO()
            try:
                _original_print(*args, file=s, **kwargs)
                UI_CALLBACK(s.getvalue().strip())
            except Exception:
                pass
print = safe_print

# ------------------------------------------
# ISOLATION DES CHEMINS ET ENCADREMENT THREAD-SAFE
# ------------------------------------------
THREAD_LOCAL = threading.local()

def set_current_run_folder(path):
    THREAD_LOCAL.run_folder = path

def get_current_run_folder():
    return getattr(THREAD_LOCAL, 'run_folder', None)

def get_abs_path(filename):
    if filename == ".env":
        return filename
    run_folder = get_current_run_folder()
    if run_folder and not os.path.isabs(filename):
        return os.path.join(run_folder, filename)
    return filename

_original_open = open
@contextlib.contextmanager
def safe_open(file, mode='r', **kwargs):
    abs_file = get_abs_path(file)
    parent_dir = os.path.dirname(abs_file)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)
        
    if file == "pipeline_logs.md" and "a" in mode:
        with FILE_LOCK:
            with _original_open(abs_file, mode, **kwargs) as f:
                yield f
    else:
        with _original_open(abs_file, mode, **kwargs) as f:
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

# Chargement automatique du fichier .env de manière robuste pour l'application
import sys
def load_env_file():
    user_home = os.path.expanduser("~")
    candidates = [
        os.path.join(user_home, "Anki_Generated_Decks", ".env"),
        ".env",
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    ]
    if getattr(sys, 'frozen', False):
        candidates.append(os.path.join(os.path.dirname(sys.executable), ".env"))
    
    # Check parent folders (up to 3 levels)
    current_dir = os.path.abspath(os.getcwd())
    for _ in range(3):
        current_dir = os.path.dirname(current_dir)
        if not current_dir:
            break
        candidates.append(os.path.join(current_dir, ".env"))
        
    for env_path in candidates:
        if os.path.exists(env_path):
            try:
                with _original_open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, val = line.split("=", 1)
                            os.environ[key.strip()] = val.strip().strip("\"'")
                print(f"[ENV LOAD] Loaded API key successfully from: {env_path}")
                return True
            except Exception as e:
                print(f"[ENV LOAD] Warning: Failed to load from {env_path}: {e}")
    return False

load_env_file()

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
    Inclut un "Latex JSON Shield" pour proteger \frac, \nu, \rho, etc.
    """
    VALID_JSON_ESCAPES = set('"\\/bfnrtu')
    # Les commandes LaTeX qui commencent par une lettre d'echappement JSON valide
    LATEX_KEYWORDS = {
        't': ['heta', 'au', 'an', 'imes', 'ext', 'ilde', 'op', 'riangle', 'o', 'extbf', 'extit', 'herefore'],
        'f': ['rac', 'lat', 'orall', 'rown'],
        'n': ['u', 'abla', 'e', 'otin', 'atural', 'eq', 'orm', 'ull', 'i', 'eg'],
        'r': ['ho', 'ight', 'angle', 'ceil', 'e', 'ule', 'ank', 'ightarrow', 'floor', 'm'],
        'b': ['eta', 'egin', 'oldsymbol', 'ar', 'reve', 'ot', 'ullet', 'f', 'mod', 'ox', 'matrix', 'ig', 'igg', 'iggl', 'iggr', 'ackslash', 'etween'],
        'u': ['psilon', 'parrow', 'pdownarrow', 'nderbrace', 'p', 'plus']
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
                
                # Verifier si c'est une fausse sequence JSON
                is_latex_command = False
                if next_ch in LATEX_KEYWORDS:
                    for keyword in LATEX_KEYWORDS[next_ch]:
                        if raw_content.startswith(keyword, i + 2):
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

def resolve_img_filename(img_num):
    # Check if there is a file in the run directory matching img-img_num.*
    try:
        import os
        run_folder = get_current_run_folder() or '.'
        for f in os.listdir(run_folder):
            if f.lower().startswith(f"img-{img_num}.") and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg')):
                return f
    except:
        pass
    # Fallback to img-img_num.jpg
    return f"img-{img_num}.jpg"

def normalize_image_references(text):
    if not text:
        return text
    import re
    
    # 1. Match custom tags like <img-33.jpeg></img-33.jpeg> or <img-33.jpeg> or <img-33>
    tag_pattern = r'<(?:img|/img)[-_](\d+)(?:\.[a-zA-Z0-9]+)?>\s*</img[-_]\1(?:\.[a-zA-Z0-9]+)?>|<img[-_](\d+)(?:\.[a-zA-Z0-9]+)?\s*/?>'
    
    def replace_tag(match):
        num = match.group(1) or match.group(2)
        resolved = resolve_img_filename(num)
        return f"<img src='{resolved}'>"
        
    text = re.sub(tag_pattern, replace_tag, text, flags=re.IGNORECASE)
    
    # 2. Match markdown images like ![img-33](img-33) or ![alt](img-33.jpeg)
    md_pattern = r'!\[[^\]]*\]\(img[-_](\d+)(?:\.[a-zA-Z0-9]+)?\)'
    def replace_md(match):
        num = match.group(1)
        resolved = resolve_img_filename(num)
        return f"<img src='{resolved}'>"
    text = re.sub(md_pattern, replace_md, text, flags=re.IGNORECASE)
    
    # 3. Match naked references to img-33 (including corrupted markdown like ![img-33.jpeg] or [img-33.jpeg])
    # ensuring we do not match inside src="...", src='...', src=..., or inside parenthesis (...)
    naked_pattern = r'(?<!src=")(?<!src=\')(?<!src=)(?<!\()(?:!?\[)?\bimg[-_](\d+)(?:\.(?:jpeg|jpg|png|gif|webp|svg))?\b(?:\])?'
    def replace_naked(match):
        num = match.group(1)
        resolved = resolve_img_filename(num)
        return f"<img src='{resolved}'>"
    text = re.sub(naked_pattern, replace_naked, text, flags=re.IGNORECASE)
    
    return text

def extract_images_from_math(text):
    if not text:
        return text
    import re
    
    # Find inline math \( ... \)
    inline_math_pattern = r'\\\((.*?)\\\)'
    def replace_inline_math(match):
        content = match.group(1)
        if '<img' in content:
            # Split by <img> tags
            parts = re.split(r'(<img[^>]*>)', content)
            new_parts = []
            for part in parts:
                if part.startswith('<img'):
                    new_parts.append(part)
                elif part.strip():
                    new_parts.append(f'\\({part}\\)')
            return ' '.join(new_parts)
        return match.group(0)
        
    text = re.sub(inline_math_pattern, replace_inline_math, text, flags=re.DOTALL)
    
    # Do the same for block math \[ ... \]
    block_math_pattern = r'\\\[(.*?)\\\]'
    def replace_block_math(match):
        content = match.group(1)
        if '<img' in content:
            # Split by <img> tags
            parts = re.split(r'(<img[^>]*>)', content)
            new_parts = []
            for part in parts:
                if part.startswith('<img'):
                    new_parts.append(f'<br>{part}<br>')
                elif part.strip():
                    new_parts.append(f'\\[{part}\\]')
            return ' '.join(new_parts)
        return match.group(0)
        
    text = re.sub(block_math_pattern, replace_block_math, text, flags=re.DOTALL)
    
    return text

def parse_and_repair_json(client, raw_content, model="mistral-small-latest"):
    """
    Tente de nettoyer et parser le JSON de manière extrêmement robuste.
    """
    # 1. Nettoyage de base du Markdown
    clean_content = raw_content.strip()
    if clean_content.startswith("```json"):
        clean_content = clean_content[7:]
    elif clean_content.startswith("```"):
        clean_content = clean_content[3:]
    if clean_content.endswith("```"):
        clean_content = clean_content[:-3]
    clean_content = clean_content.strip()
    
    # Exécuter systématiquement en tout premier fix_llm_json_escaping sur la chaîne nettoyée
    secured_content = fix_llm_json_escaping(clean_content)
    
    # Étape A : Essai direct de parsing standard sur la chaîne sécurisée
    try:
        return json.loads(secured_content)
    except json.JSONDecodeError:
        pass

    # Étape B : Essai avec json_repair sur la chaîne sécurisée (très robuste aux guillemets/escapes)
    try:
        repaired_data = json_repair.loads(secured_content)
        if repaired_data is not None:
            # Détection intelligente et robuste de troncature réelle
            normalized_end = re.sub(r'\s+', '', clean_content)
            if not (normalized_end.endswith("}") or normalized_end.endswith("]") or normalized_end.endswith("}```") or normalized_end.endswith("]```")):
                print("      [Parsing JSON] ⚠️ DANGER: Le JSON généré par l'IA est TRONQUÉ (incomplet).")
                print("      [Parsing JSON] json_repair a forcé la fermeture. Rejet volontaire pour régénération complète.")
                raise json.JSONDecodeError("JSON tronqué détecté", clean_content, len(clean_content))
            
            # Réparation réussie ! Écriture dans les logs
            try:
                with open("json_repair_logs.md", "a", encoding="utf-8") as f_log:
                    f_log.write(f"## REPARATION REUSSIE (sur secured_content)\n\n### AVANT:\n```json\n{clean_content[:1000]}...\n```\n\n### APRES:\n```json\n{json.dumps(repaired_data, ensure_ascii=False, indent=2)[:1000]}...\n```\n\n---\n")
            except Exception:
                pass
            return repaired_data
    except Exception as repair_err:
        # Si c'était un rejet volontaire de troncature, on lève l'erreur pour retenter le bloc parent
        if isinstance(repair_err, json.JSONDecodeError) and "JSON tronqué" in str(repair_err):
            raise repair_err

    # Étape C : Fallback final en cas d'échec total (on a déjà appliqué fix_llm_json_escaping sur secured_content)
    print("      [Parsing JSON] Parsing direct et réparation sur secured_content échoués. Tentative de secours...")
    try:
        repaired_data = json_repair.loads(secured_content)
        
        # --- LOGS DEMANDÉS PAR L'UTILISATEUR ---
        try:
            with open("json_repair_logs.md", "a", encoding="utf-8") as f_log:
                f_log.write(f"## ERREUR PARSING INITIAL SECURISE\n\n### SECURED CONTENT:\n```json\n{secured_content}\n```\n\n### APRES REPAIR (repaired_data):\n```json\n{json.dumps(repaired_data, ensure_ascii=False, indent=2)}\n```\n\n---\n")
        except Exception:
            pass
        
        # Détection finale de troncature sur le contenu original
        if not (clean_content.endswith("}") or clean_content.endswith("]")):
            print("      [Parsing JSON] ⚠️ DANGER: Le JSON généré par l'IA est TRONQUÉ (incomplet).")
            print("      [Parsing JSON] json_repair a forcé la fermeture, limitant le résultat à 1 carte.")
            print("      [Parsing JSON] Rejet volontaire pour forcer l'IA à relancer le chunk complet.")
            raise json.JSONDecodeError("JSON tronqué détecté", clean_content, len(clean_content))
        
        if repaired_data is not None:
            print("      [Parsing JSON] Réparation réussie via secours sur secured_content !")
            return repaired_data
        else:
            raise json.JSONDecodeError("json_repair a retourné None", secured_content, len(secured_content))
    except Exception as repair_err:
        print(f"      [Parsing JSON] Échec total du parsing : {repair_err}")
        raise repair_err


# ==========================================
# CONFIGURATION DES MODELES ANKI (genanki)
# ==========================================

CSS = """
.card {
  font-family: arial;
  font-size: 20px;
  text-align: justify; /* Modifié pour la V1.11 : alignement justifié */
  color: black;
  background-color: white;
  padding: 20px;
}
.cloze {
  font-weight: bold;
  color: blue;
}
img {
  max-width: 100%;
  height: auto;
  display: block;
  margin: 10px auto;
}
"""

MODEL_BASIC_ID = 1593820471
model_basic = genanki.Model(
  MODEL_BASIC_ID,
  'Basique (Mistral)',
  fields=[
    {'name': 'Front'},
    {'name': 'Back'},
    {'name': 'Sequence'},
  ],
  sort_field_index=2,
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
    {'name': 'Sequence'},
  ],
  sort_field_index=2,
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
    {'name': 'Sequence'},
  ],
  sort_field_index=2,
  templates=[
    {
      'name': 'Cloze',
      'qfmt': '{{cloze:Text}}',
      'afmt': '{{cloze:Text}}<br><hr><br>{{Back Extra}}',
    },
  ],
  css=CSS
)


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

        if current_length > max_chunk_size and not line.strip():
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append("\n".join(current_chunk))
        
    return chunks

def semantic_split_with_ai(client, markdown_text, learning_depth, model="mistral-large-latest", retries=2):
    lines = markdown_text.split("\n")
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    numbered_text = "\n".join(numbered_lines)
    if learning_depth == "Zero Lecture":
        system_prompt = r"""
ROLE
You are a structural parser Agent. Your only job is to semantically split an academic course text (provided with line numbers) into logical "chunks" or "blocks".
Each chunk must be a coherent pedagogical unit that can later be fed completely to an Anki card generator.

RULES:
1. MAXIMUM AGGREGATION FOR MATHEMATICAL CONCEPTS: A Theorem (or Proposition/Property), its associated Proof, and its direct Examples/Remarks form ONE INDIVISIBLE UNIT. You MUST group them together into ONE SINGLE CHUNK.
   - Example scenario: Line 10 is `## THEOREM 1`, Line 40 is `# EXAMPLE 1`, Line 70 is `# PROOF`, Line 120 is `# EXAMPLE 2` and example 2 finish at line 140. You MUST create a SINGLE chunk starting at line 10 and ending at line 140 inclusive.
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
    elif learning_depth == "Intermediaire":
        system_prompt = r"""
ROLE
You are a structural parser Agent. Your only job is to semantically split an academic course text (provided with line numbers) into logical "chunks" or "blocks".
Each chunk must be a coherent pedagogical unit that can later be fed completely to an Anki card generator.

RULES:
1. MAXIMUM AGGREGATION : A Theorem (or Proposition/Property), its associated Proof, and its direct Examples/Remarks form ONE INDIVISIBLE UNIT. You MUST group them together into ONE SINGLE CHUNK.
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
                temperature=0.0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Here is the numbered text as input, divide it strictly following the rules:\n\n{numbered_text}"}
                ],
            )
            content = response.choices[0].message.content
            data = parse_and_repair_json(client, content, model=model)
            
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

def split_text_in_half(text):
    lines = text.split("\n")
    if len(lines) <= 2:
        mid = len(text) // 2
        return text[:mid], text[mid:]
    
    mid_line_idx = len(lines) // 2
    best_split = mid_line_idx
    for offset in range(min(15, len(lines) // 2)):
        idx1 = mid_line_idx - offset
        if idx1 > 0 and (not lines[idx1].strip() or lines[idx1].startswith("#")):
            best_split = idx1
            break
        idx2 = mid_line_idx + offset
        if idx2 < len(lines) - 1 and (not lines[idx2].strip() or lines[idx2].startswith("#")):
            best_split = idx2
            break
            
    part1 = "\n".join(lines[:best_split])
    part2 = "\n".join(lines[best_split:])
    return part1, part2

def restore_html_tags(text):
    if not text:
        return text
    import re
    
    # 1. Nettoyer les espaces anormaux à l'intérieur des balises HTML
    # Regex pour cibler les balises HTML potentielles
    tag_pattern = r'<(\s*/?\s*[a-zA-Z][^>]*?)>'
    
    def clean_tag(match):
        content = match.group(1)
        # Supprimer tous les espaces pour vérifier s'il s'agit d'une balise simple
        stripped = re.sub(r'\s+', '', content).lower()
        simple_tags = {
            'b', '/b', 'i', '/i', 'u', '/u', 'br', 'br/', '/br', 
            'hr', 'hr/', '/hr', 'ul', '/ul', 'li', '/li', 'ol', '/ol',
            'span', '/span', 'div', '/div', 'p', '/p', 'sub', '/sub', 'sup', '/sup'
        }
        if stripped in simple_tags:
            # Normaliser les balises auto-fermantes simples comme <br/>
            if stripped == 'br/':
                return '<br/>'
            if stripped == 'hr/':
                return '<hr/>'
            return f"<{stripped}>"
        
        # Pour les balises complexes (ex: <img src="..."> ou <a href="...">)
        # Nettoyer l'espacement initial et final, et normaliser le slash de fin
        cleaned = content.strip()
        # Remplacer les espaces multiples par un seul espace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        # Supprimer l'espace avant et après le slash pour les balises de fermeture : </ b> -> </b >
        cleaned = re.sub(r'^/\s*', '/', cleaned)
        # Nettoyer l'espace pour les balises auto-fermantes à la fin : ` /` -> `/`
        cleaned = re.sub(r'\s*/\s*$', '/', cleaned)
        return f"<{cleaned}>"
        
    text = re.sub(tag_pattern, clean_tag, text)
    return text

def remove_code_tags_around_mathjax(text):
    if not text:
        return text
    import re
    text = re.sub(r'<code[^>]*>\s*(\\(.*?\\)|\\[.*?\\])\s*</code>', r'\1', text, flags=re.DOTALL)
    return text

def fix_mismatched_math_delimiters(text):
    if not text:
        return text
    import re
    
    # 1. Masquage temporaire des parenthèses/crochets LaTeX complexes (ex: \left[, \right])
    # Cela évite que les expressions imbriquées de type \left[ ... \right] ne perturbent
    # la détection des délimiteurs globaux \[ et \] dans la regex.
    masks = [
        (r'\\left\[', '__LEFT_BRACKET__'),
        (r'\\right\]', '__RIGHT_BRACKET__'),
        (r'\\left\(', '__LEFT_PAREN__'),
        (r'\\right\)', '__RIGHT_PAREN__'),
        (r'\\left\|', '__LEFT_PIPE__'),
        (r'\\right\|', '__RIGHT_PIPE__'),
        (r'\\left\\\{', '__LEFT_BRACE__'),
        (r'\\right\\\}', '__RIGHT_BRACE__')
    ]
    
    masked_text = text
    for pattern, placeholder in masks:
        masked_text = re.sub(pattern, placeholder, masked_text)
        
    # Corriger \( ... \] en \( ... \) en s'assurant de ne pas croiser d'autres blocs
    pattern1 = r'\\\(((?:(?!\\\(|\\\)|\\\[|\\\]).)*?)\\\]'
    masked_text = re.sub(pattern1, r'\\(\1\\)', masked_text, flags=re.DOTALL)
    
    # Corriger \[ ... \) en \[ ... \] en s'assurant de ne pas croiser d'autres blocs
    pattern2 = r'\\\[((?:(?!\\\(|\\\)|\\\[|\\\]).)*?)\\\)'
    masked_text = re.sub(pattern2, r'\\[\1\\]', masked_text, flags=re.DOTALL)
    
    # 2. Démasquage
    for pattern, placeholder in masks:
        orig = pattern.replace(r'\\', '\\').replace(r'\{', '{').replace(r'\}', '}').replace(r'\[', '[').replace(r'\]', ']').replace(r'\(', '(').replace(r'\)', ')').replace(r'\|', '|')
        masked_text = masked_text.replace(placeholder, orig)
        
    return masked_text

def clean_mathjax_environments(text):
    if not text:
        return text
    import re
    
    # Matches block math \[...\] or inline math \(...\)
    pattern = r'(\\\[.*?\\\]|\\\(.*?\\\))'
    
    def repl(match):
        math_content = match.group(1)
        # Inside the math environment, replace HTML line breaks with \\
        # Handles standard <br>, <br/>, and escaped ones: \lt br \gt, \\lt br \\gt, etc.
        br_pattern = r'(?i)(?:<\s*br\s*/?\s*>|\\+lt\s*br\s*/?\s*\\+gt)'
        math_content = re.sub(br_pattern, ' ', math_content)
        return math_content

    return re.sub(pattern, repl, text, flags=re.DOTALL)

def fix_inline_block_math(text):
    # Désactivation du forçage inline.
    # Laissons le choix du LLM (qui respecte le prompt) piloter la mise en page.
    return text

def clean_for_anki_tsv(text):
    if not text:
        return text
    import re
    
    # 1. Remplacer les retours à la ligne par <br> UNIQUEMENT en dehors des environnements MathJax
    # Cela évite de briser la syntaxe des matrices ou des environnements multignes (cases, aligned)
    parts = re.split(r'(\\\[.*?\\\]|\\\(.*?\\\))', text, flags=re.DOTALL)
    for i in range(0, len(parts), 2):
        if parts[i]:
            parts[i] = parts[i].replace('\n', '<br>')
    text = "".join(parts)
    
    # Supprimer les \r
    text = text.replace('\r', '')
    # Remplacer les tabulations par des espaces simples
    text = text.replace('\t', ' ')
    # Supprimer les guillemets superflus au début et à la fin
    text = text.strip()
    if text.startswith('"') and text.endswith('"'):
        text = text[1:-1]
    text = text.replace('"', "'")
    text = re.sub(r'(\})\}\}', r'\1 }}', text)
    
    # 2. Dédupliquer les délimiteurs mathématiques accidentellement doublés par les LLM
    text = re.sub(r'\\\]\s*\\\]', r'\\]', text)
    text = re.sub(r'\\\[\s*\\\[', r'\\[', text)
    text = re.sub(r'\\\)\s*\\\)', r'\\)', text)
    text = re.sub(r'\\\(\s*\\\(\s*', r'\\(', text)
    
    return text

def sanitize_html_tags(text):
    if not text:
        return text
    import re
    
    # 1. Corriger les balises HTML orphelines ou tronquées (ex: </sup , </sub , </b , </i sans chevron de fermeture)
    text = re.sub(r'</sup(?![a-zA-Z>])', '</sup>', text)
    text = re.sub(r'</sub(?![a-zA-Z>])', '</sub>', text)
    text = re.sub(r'</b(?![a-zA-Z>])', '</b>', text)
    text = re.sub(r'</i(?![a-zA-Z>])', '</i>', text)
    
    # 2. Équilibrer les balises simples : <b>, <i>, <u>, <sup>, <sub>
    tags_to_check = [('<b>', '</b>'), ('<i>', '</i>'), ('<u>', '</u>'), ('<sup>', '</sup>'), ('<sub>', '</sub>')]
    
    for open_tag, close_tag in tags_to_check:
        opens = text.count(open_tag)
        closes = text.count(close_tag)
        
        if opens > closes:
            text += close_tag * (opens - closes)
        elif closes > opens:
            for _ in range(closes - opens):
                idx = text.rfind(close_tag)
                if idx != -1:
                    text = text[:idx] + text[idx + len(close_tag):]
                    
    return text

def space_mathjax_double_braces(text):
    if not text:
        return text
    import re
    # Espacer les doubles accolades }} consécutives à l'intérieur des environnements MathJax
    # pour éviter qu'Anki ne les confonde avec la fin d'un texte à trous (cloze note).
    parts = re.split(r'(\\\[.*?\\\]|\\\(.*?\\\))', text, flags=re.DOTALL)
    for i in range(1, len(parts), 2):
        while '}}' in parts[i]:
            parts[i] = parts[i].replace('}}', '} }')
    return "".join(parts)


def fix_markdown_bold(text):
    if not text: return text
    import re
    return re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)

def extract_cards_from_chunk(client, chunk_text, learning_depth, filename_tag="Course", model="mistral-large-latest", retries=3):
    tag_instruction = (
        f"TAGS RULES: Every card MUST have a 'tags' field. "
        f"The first tag MUST always be '{filename_tag}'. "
        f"Then add 1-2 topic tags using the format 'Topic_Subtopic' (underscores, NO spaces). "
        f"Example: '{filename_tag} Pressure_Gradient Hydrostatics'"
    )
    if learning_depth == "Zero Lecture":
        system_prompt = r"""
ROLE
You are a bulletproof, scholarly Anki Flashcard Generator. 
Your goal is to parse academic engineering course content into highly detailed Anki flashcards.

RULES (CRITICAL):
1. LANGUAGE (STRICT LIMITATION): The generated text MUST be in the EXACT SAME LANGUAGE as the source text. NEVER translate.
2. ZERO-PRONOUN & CONTEXT SCRUBBING (ABSOLUTELY CRITICAL): Flashcards are viewed out of order. You MUST aggressively SCRUB and REMOVE any phrases like "In Example 1", "As we saw in the previous section", "The following theorem", or "This equation". If the textbook says "In Example 1, Green's theorem is verified...", you MUST rephrase it to be standalone: "Verify Green's theorem for the functions...". Never assume the student has the surrounding textbook! ABSOLUTELY NO BLIND REFERENCES: If the text says 'By Theorem 2.1', you MUST replace it by stating exactly what the theorem says. Never use blind pointers like 'Proposition 5.1' or 'Equation 17'.
3. PRESERVATION: Include ALL theorems, definitions, proofs, remarks, and examples exactly as they appear in the course. Do not condense important details.
4. TAG INSTRUCTIONS : [TAG_INSTRUCTION]
5. TEXT FORMATTING (PLAIN TEXT / HTML):
    - Use natural plain text for all readable content.
    - NEVER use `\text{}` or `\begin{aligned}`. They are strictly forbidden.
    - You may use `\begin{array}` or `\begin{matrix}` ONLY inside block math `\[ ... \]` for actual mathematical matrices. NEVER use them to layout natural text.
    - You may use basic HTML tags for styling (e.g., `<b>`, `<i>`, `<br>`). Do not use Markdown `**bold**`.
    - Use `\\lt` and `\\gt` instead of `<` and `>` in mathematical expressions to prevent HTML parsing errors.
    - NEVER end a line with a lone backslash `\`.
6. MATH FORMATTING (MATHJAX):
    - For INLINE math (variables, short equations within text), you MUST wrap the expression in `\( ... \)` (e.g., `\( T_H \)` or `\( E=mc^2 \)`).
    - For BLOCK math (large equations, derivations), you MUST wrap the expression in `\[ ... \]`.
    - Double-escape your backslashes for JSON compatibility (e.g., `\\frac`, `\\rho`, `\\(`, `\\[`).
7. IMAGES: You MUST NOT drop any image! Embed any image reference (e.g. `![img-0.jpeg](img-0.jpeg)`) in the most relevant flashcard EXACTLY as `![image_name](image_name)`. You can place it on a new line using `<br>`.
8. CLOZE FORMAT: Use standard Anki cloze syntax `{{c1::hidden text}}`. 
    - NEVER use double square brackets.
    - Group structurally related words under the SAME cloze index.
    - You can freely use MathJax inside a cloze (e.g., `{{c1::\( E=mc^2 \)}}`).
    - CRITICAL BRACE SPACING: If your cloze content ends with a closing brace `}`, you MUST add a space before the Anki cloze closing braces `}}` to prevent parsing errors (e.g., `{{c1:: \frac{1}{2} }}` instead of `{{c1::\frac{1}{2}}}`).
9. IMAGE-DESCRIPTION PROHIBITION (CRITICAL): NEVER create cards that ask "What does this image show?", "Describe this image", "What is depicted?", "What is being illustrated?" or any variant. The front MUST contain a specific conceptual question about the TOPIC, not about an image. Images are supplementary visual aids placed as support, not the subject of questions.
10. NO LATEX LISTS: NEVER use `\begin{itemize}`, `\begin{enumerate}`, or `\item`. Use standard HTML lists (`<ul><li>...</li></ul>`) or plain text bullets (`- `).
11. AGGREGATION: Consolidate related information. Avoid making 5 separate cards for a single topic; instead make 1 rich 'Basique' card asking a comprehensive question with all the details synthesized on the back.
12. ABSOLUTELY NO MULTIPLE CHOICE QUESTIONS (MCQ): NEVER generate cards that ask "Which of the following statements is true/false?", "Identify the incorrect statement", or any variation of a multiple choice question. You MUST convert all multiple-choice questions from the source text into direct, open-ended conceptual questions. DO NOT list choices (A, B, C, D) on the front or back.
13. NO TRUNCATED CONTENT: If you announce a list (with ':'), you MUST provide it IN FULL. NEVER write 'The Carnot cycle is composed of four processes:' without listing ALL four processes. The back MUST always completely answer the question asked on the front.
14. MULTI-IMAGE FIGURES: A single figure in the source text may contain MULTIPLE images (e.g. `![img-5.jpeg](img-5.jpeg)` and `![img-6.jpeg](img-6.jpeg)` appearing together). You MUST include ALL images from the figure in the same card.
15. CONTEXTUAL SCAFFOLDING (MANDATORY FOR ALL "Basique" CARDS):
    The "back" field of every "Basique" card must NEVER be limited to a bare answer.
    After the main answer/proof/resolution, you MUST add a visual separator `<hr>`, then a section titled `<b>Explanatory Context :</b><br>` containing 2-3 sentences that:
    - Re-explain the INTUITION behind the concept in plain, accessible language.
    - State WHERE this concept fits in the global architecture of the course chapter.
    - Provide an analogy, real-world application, or connection to related concepts when possible.
16. CLOZE HARD LIMIT (CRITICAL):
    - A "Texte à trous" card must NEVER contain more than 3 cloze deletions.
    - "Texte à trous" is STRICTLY RESERVED for: vocabulary terms, physical constants, unit conversions, and simple syntactic patterns.
    - For theorems, demonstrations, causal explanations, multi-step processes, and any concept requiring systemic understanding, you MUST use "Basique" format with open-ended questions forcing free recall.
17. AUTHENTIC ELABORATIVE INTERROGATION (at least 20% of cards):
   You MUST generate cards that force CAUSAL REASONING, not disguised recall.
   TRUE ELABORATION (forces deep processing):
     - 'Why is the Nyquist rate 2B and not B?' (forces reasoning about positive/negative spectral symmetry)
     - 'Why does quantization introduce a non-recoverable error while sampling does not?' (forces comparative causal analysis)
     - 'What would happen to the reconstructed signal if the anti-aliasing filter had a non-zero transition band?' (forces consequence prediction)
   FALSE ELABORATION (just recall with Why syntax — FORBIDDEN):
     - 'How does Fs influence the spectrum?' (just asks for a description, no causal chain)
     - 'Why is sampling important?' (too vague, invites a textbook summary)
   Tag authentic elaborative cards with 'Catégorie::Elaborative_Interrogation' as first tag after filename.
18. BLOOM LEVEL TARGETING: Target this distribution:
   - 25% Recall (definitions, constants) — use Texte à trous or Généralités
   - 45% Understand (explain concepts) — use Basique
   - 10% Apply (solve a specific problem, compute a value) — use Basique in '05_Exercices_et_Exemples'
   - 20% Analyze (compare methods, identify trade-offs, explain why one approach fails) — use Basique
19. ANTI-REDUNDANCY: Before generating a new card, mentally check if you have already generated a card testing the SAME underlying concept. If yes, DO NOT generate a near-duplicate. Prefer ONE rich comprehensive card over 3 shallow variations.\n\n{chunk_text}"

20. JSON STRING ESCAPING (CRITICAL):
    - You MUST NOT use unescaped double quotes (") inside the 'front' or 'back' JSON string values.
    - If you need to quote a word or write a list, use single quotes ('word') or STRICTLY escape the double quotes (\\"word\\").
    - For all HTML tags and attributes, you MUST use SINGLE QUOTES instead of double quotes (e.g., <img src='image.jpg'>).
21. COMPLETENESS & ANTI-TRUNCATION (CRITICAL): 
    - You must NEVER stop generating mid-sentence.
    - If you announce a list (e.g., "This involves:"), you MUST finish writing it.
    - You MUST successfully complete the JSON structure and end your entire response exactly with the closing brackets `]}`.


RULES SPECIFIC TO THEOREMS AND DEFINITIONS:

IF THE CONTENT IS A THEOREM, PROPOSITION, COROLLARY, OR PROPERTY:
- ZERO-FRAGMENTATION RULE: You MUST GENERATE EXACTLY ONE COMPREHENSIVE CARD for the entire Theorem/Proposition unit. DO NOT fragment the proof or remarks into separate flashcards or separate cloze cards.
- Subdeck: MUST be "02_Théorèmes_et_Preuves"
- Card Type: MUST be "Basique" or "Texte à trous"
- `front`: A clear question, the theorem name, or the clozed statement.
- `back` CRITICAL REQUIREMENT:
   1. If `front` used a clozed statement, put the ENTIRE UNC-LOZED statement here first.
   2. THEN, you MUST INCLUDE THE ENTIRE COMPLETE DEMONSTRATION/PROOF from the text, exactly as provided. DO NOT summarize it. DO NOT skip equations.
   3. THEN, include any remarks, corollaries, or examples that immediately follow it in the text.

IF THE CONTENT IS AN EXAMPLE OR AN EXERCISE:
- Subdeck: MUST be "05_Exercices_et_Exemples"
- Card Type: MUST be "Basique"
- `front` CRITICAL SELF-CONTAINMENT RULE: You MUST write out the ENTIRE problem statement, all contextual equations, given values, and the exact question to solve explicitly on the front. ABSOLUTELY NEVER refer to an example name (e.g., REMOVE "In Example 1...").
- `back`: Provide the complete, step-by-step resolution of the example/exercise.

IF THE CONTENT IS A GENERAL CONCEPT, DEFINITION, VOCABULARY, OR FACTUAL KNOWLEDGE:
- CONCEPTUAL AGGREGATION RULE: Do NOT create many small cards for properties of the same concept. Group closely related facts into a SINGLE comprehensive flashcard.
- STRONG PREFERENCE FOR "Basique". Prefer a broad question on the front. "Texte à trous" is ONLY for isolated vocabulary.
- Subdeck: MUST be "01_Définitions" (for concepts/definitions) or "03_Vocabulaire_et_Constantes" (for isolated vocabulary/constants)
- Card Type: "Basique" (STRONGLY preferred) or "Généralités" or "Texte à trous" (max 3 clozes)
- `front`: Ask a comprehensive conceptual question or ask for the definition.
- `back`: Provide the exact, concise definition or full aggregated text, followed by the Contexte Explicatif section.

JSON OUTPUT ONLY:
{
    "cards": [
        {
            "type": "Texte à trous" | "Basique" | "Généralités",
            "subdeck": "01_Définitions" | "02_Théorèmes_et_Preuves" | "03_Vocabulaire_et_Constantes" | "04_Synthèse_et_Relations" | "05_Exercices_et_Exemples",
            "front": "Complete text formatted with HTML and MathJax \\( ... \\) or \\[ ... \\]",
            "back": "Detailed proof/answer formatted with HTML and MathJax. Use <hr> for separators.",
            "tags": "Math Course_Unit (NO SPACES IN INDIVIDUAL TAGS)"
        }
    ]
}
"""
    elif learning_depth == "Intermediaire":
        system_prompt = r"""
    ROLE
You are a bulletproof, scholarly Anki Flashcard Generator. 
Your goal is to parse academic engineering course content into highly detailed Anki flashcards.

RULES (CRITICAL):
1. LANGUAGE (STRICT LIMITATION): The generated text MUST be in the EXACT SAME LANGUAGE as the source text. NEVER translate.
2. ZERO-PRONOUN & CONTEXT SCRUBBING (ABSOLUTELY CRITICAL): Flashcards are viewed out of order. You MUST aggressively SCRUB and REMOVE any phrases like "In Example 1", "As we saw in the previous section", "The following theorem", or "This equation". If the textbook says "In Example 1, Green's theorem is verified...", you MUST rephrase it to be standalone: "Verify Green's theorem for the functions...". Never assume the student has the surrounding textbook! ABSOLUTELY NO BLIND REFERENCES: If the text says 'By Theorem 2.1', you MUST replace it by stating exactly what the theorem says. Never use blind pointers like 'Proposition 5.1' or 'Equation 17'.
3. PRESERVATION: Include ALL theorems, definitions, proofs, remarks, and examples exactly as they appear in the course. Do not condense important details.
4. TAG INSTRUCTION : [TAG_INSTRUCTION]
5. TEXT FORMATTING (PLAIN TEXT / HTML):
    - Use natural plain text for all readable content.
    - NEVER use `\text{}` or `\begin{aligned}`. They are strictly forbidden.
    - You may use `\begin{array}` or `\begin{matrix}` ONLY inside block math `\[ ... \]` for actual mathematical matrices. NEVER use them to layout natural text.
    - You may use basic HTML tags for styling (e.g., `<b>`, `<i>`, `<br>`). Do not use Markdown `**bold**`.
    - Use `\\lt` and `\\gt` instead of `<` and `>` in mathematical expressions to prevent HTML parsing errors.
    - NEVER end a line with a lone backslash `\`.
6. MATH FORMATTING (MATHJAX):
    - For INLINE math (variables, short equations within text), you MUST wrap the expression in `\( ... \)` (e.g., `\( T_H \)` or `\( E=mc^2 \)`).
    - For BLOCK math (large equations, derivations), you MUST wrap the expression in `\[ ... \]`.
    - Double-escape your backslashes for JSON compatibility (e.g., `\\frac`, `\\rho`, `\\(`, `\\[`).
7. IMAGES: You MUST NOT drop any image! Embed any image reference (e.g. `![img-0.jpeg](img-0.jpeg)`) in the most relevant flashcard EXACTLY as `![image_name](image_name)`. You can place it on a new line using `<br>`.
8. CLOZE FORMAT: Use standard Anki cloze syntax `{{c1::hidden text}}`. 
    - NEVER use double square brackets.
    - Group structurally related words under the SAME cloze index.
    - You can freely use MathJax inside a cloze (e.g., `{{c1::\( E=mc^2 \)}}`).
    - CRITICAL BRACE SPACING: If your cloze content ends with a closing brace `}`, you MUST add a space before the Anki cloze closing braces `}}` to prevent parsing errors (e.g., `{{c1:: \frac{1}{2} }}` instead of `{{c1::\frac{1}{2}}}`).
9. IMAGE-DESCRIPTION PROHIBITION (CRITICAL): NEVER create cards that ask "What does this image show?", "Describe this image", "What is depicted?", "What is being illustrated?" or any variant. The front MUST contain a specific conceptual question about the TOPIC, not about an image. Images are supplementary visual aids placed as support, not the subject of questions.
10. NO LATEX LISTS: NEVER use `\begin{itemize}`, `\begin{enumerate}`, or `\item`. Use standard HTML lists (`<ul><li>...</li></ul>`) or plain text bullets (`- `).
11. AGGREGATION: Consolidate related information. Avoid making 5 separate cards for a single topic; instead make 1 rich 'Basique' card asking a comprehensive question with the answer first, then all the details synthesized, on the back. For example, a question asking for a theorem, the back should contain, first, the theorem, then, just below, the proof and remarks if there is any, about the theorem.
12. ABSOLUTELY NO MULTIPLE CHOICE QUESTIONS (MCQ): NEVER generate cards that ask "Which of the following statements is true/false?", "Identify the incorrect statement", or any variation of a multiple choice question. You MUST convert all multiple-choice questions from the source text into direct, open-ended conceptual questions. DO NOT list choices (A, B, C, D) on the front or back.
13. NO TRUNCATED CONTENT: If you announce a list (with ':'), you MUST provide it IN FULL. NEVER write 'The Carnot cycle is composed of four processes:' without listing ALL four processes. The back MUST always completely answer the question asked on the front.
14. MULTI-IMAGE FIGURES: A single figure in the source text may contain MULTIPLE images (e.g. `![img-5.jpeg](img-5.jpeg)` and `![img-6.jpeg](img-6.jpeg)` appearing together). You MUST include ALL images from the figure in the same card. To decide wether an image is related to a concept, refer to the images annotations.
15. CONTEXTUAL SCAFFOLDING (MANDATORY FOR ALL "Basique" CARDS):
    The "back" field of every "Basique" card must NEVER be limited to a bare answer.
    After the main answer/proof/resolution, you MUST add a visual separator `<hr>`, then a section titled `<b>Explanatory Context :</b><br>` containing 2-3 sentences that:
    - Re-explain the INTUITION behind the concept in plain, accessible language.
    - State WHERE this concept fits in the global architecture of the course chapter.
    - Provide an analogy, real-world application, or connection to related concepts when possible.
16. CLOZE HARD LIMIT (CRITICAL):
    - A "Texte à trous" card must NEVER contain more than 3 cloze deletions.
    - "Texte à trous" is STRICTLY RESERVED for: vocabulary terms, physical constants, unit conversions, and simple syntactic patterns.
    - For theorems, demonstrations, causal explanations, multi-step processes, and any concept requiring systemic understanding, you MUST use "Basique" format with open-ended questions forcing free recall.

17. JSON STRING ESCAPING (CRITICAL):
    - You MUST NOT use unescaped double quotes (") inside the 'front' or 'back' JSON string values.
    - If you need to quote a word or write a list, use single quotes ('word') or STRICTLY escape the double quotes (\\"word\\").
    - For all HTML tags and attributes, you MUST use SINGLE QUOTES instead of double quotes (e.g., <img src='image.jpg'>).
18. COMPLETENESS & ANTI-TRUNCATION (CRITICAL): 
    - You must NEVER stop generating mid-sentence.
    - If you announce a list (e.g., "This involves:"), you MUST finish writing it.
    - You MUST successfully complete the JSON structure and end your entire response exactly with the closing brackets `]}`.

RULES SPECIFIC TO THEOREMS AND DEFINITIONS:

IF THE CONTENT IS A THEOREM, PROPOSITION, COROLLARY, OR PROPERTY:
- ZERO-FRAGMENTATION RULE: You MUST GENERATE EXACTLY ONE SINGLE COMPREHENSIVE CARD for the entire Theorem/Proposition unit. DO NOT fragment the proof or remarks into separate flashcards or separate cloze cards.
- Subdeck: MUST be "02_Théorèmes_et_Preuves"
- Card Type: MUST be "Basique" or "Texte à trous"
- `front`: A clear question, the theorem name, or the clozed statement.
- `back` CRITICAL REQUIREMENT:
   1. If `front` used a clozed statement, put the ENTIRE UN-CLOZED statement here first.
   2. THEN, you MUST INCLUDE THE ENTIRE COMPLETE DEMONSTRATION/PROOF from the text, exactly as provided. DO NOT summarize it. DO NOT skip equations.
   3. THEN, include any remarks, corollaries, or examples that immediately follow it in the text.

IF THE CONTENT IS AN EXAMPLE OR AN EXERCISE:
- Skip it, and don't write any card about it

IF THE CONTENT IS A GENERAL CONCEPT, DEFINITION, VOCABULARY, OR FACTUAL KNOWLEDGE:
- CONCEPTUAL AGGREGATION RULE: Do NOT create many small cards for properties of the same concept. Group closely related facts into a SINGLE comprehensive flashcard.
- STRONG PREFERENCE FOR "Basique". Prefer a broad question on the front. "Texte à trous" is ONLY for isolated vocabulary.
- Subdeck: MUST be "01_Définitions" (for concepts/definitions) or "03_Vocabulaire_et_Constantes" (for isolated vocabulary/constants)
- Card Type: "Basique" (STRONGLY preferred) or "Généralités" or "Texte à trous" (max 3 clozes)
- `front`: Ask a comprehensive conceptual question or ask for the definition.
- `back`: Provide the exact, concise definition or full aggregated text, followed by the Contexte Explicatif section.

JSON OUTPUT ONLY:
{
    "cards": [
        {
            "type": "Texte à trous" | "Basique" | "Généralités",
            "subdeck": "01_Définitions" | "02_Théorèmes_et_Preuves" | "03_Vocabulaire_et_Constantes" ,
            "front": "Complete text formatted with HTML and MathJax \\( ... \\) or \\[ ... \\]",
            "back": "Detailed proof/answer formatted with HTML and MathJax. Use <hr> for separators.",
            "tags": "Math Course_Unit (NO SPACES IN INDIVIDUAL TAGS)"
        }
    ]
}
    """
    system_prompt = system_prompt.replace("[TAG_INSTRUCTION]", tag_instruction)
    for attempt in range(retries):
        try:
            response = client.chat.complete(
                model=model,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": chunk_text}
                ],
                max_tokens=32000
            )
            
            content = response.choices[0].message.content
            data = parse_and_repair_json(client, content, model=model)
        
            if "cards" in data:
                normalized_cards = []
                for c in data["cards"]:
                    tags_val = c.get("tags", "")
                    if isinstance(tags_val, list):
                        c["tags"] = " ".join(str(t) for t in tags_val)
                    elif not isinstance(tags_val, str):
                        c["tags"] = str(tags_val)
                    
                    c["front"] = fix_mismatched_math_delimiters(c.get("front", ""))
                    c["front"] = remove_code_tags_around_mathjax(c["front"])
                    c["front"] = clean_mathjax_environments(c["front"])
                    c["front"] = restore_html_tags(c["front"])
                    c["front"] = fix_inline_block_math(c["front"])
                    c["front"] = normalize_image_references(c["front"])
                    c["front"] = clean_for_anki_tsv(c["front"])
                    
                    c["back"] = fix_mismatched_math_delimiters(c.get("back", ""))
                    c["back"] = remove_code_tags_around_mathjax(c["back"])
                    c["back"] = clean_mathjax_environments(c["back"])
                    c["back"] = restore_html_tags(c["back"])
                    c["back"] = fix_inline_block_math(c["back"])
                    c["back"] = normalize_image_references(c["back"])
                    c["back"] = clean_for_anki_tsv(c["back"])
                    
                    c["front"] = fix_markdown_bold(c["front"])
                    c["back"] = fix_markdown_bold(c["back"])
                    
                    normalized_cards.append(c)
                return normalized_cards
            else:
                print(f"Format JSON invalide. Tentative {attempt+1}/{retries}...")
        except Exception as e:
            import time
            print(f"Erreur d'API ou de parsing Mistral. Tentative {attempt+1}/{retries}... ({e})")
            time.sleep(2)
            
    # Repli sémantique récursif (Divide & Conquer) en cas d'échec systématique
    if len(chunk_text) > 2000:
        print(f"\n      [REPLI DIVIDE & CONQUER] ⚠️ Le bloc est trop volumineux ou complexe (taille: {len(chunk_text)} chars) et a échoué systématiquement.")
        print("      [REPLI DIVIDE & CONQUER] Subdivision automatique du bloc en 2 sous-blocs plus simples...")
        
        part1, part2 = split_text_in_half(chunk_text)
        
        print(f"      [REPLI DIVIDE & CONQUER] -> Lancement du sous-bloc A (taille: {len(part1)} chars)...")
        cards1 = extract_cards_from_chunk(client, part1, learning_depth, filename_tag=filename_tag, model=model, retries=retries)
        
        print(f"      [REPLI DIVIDE & CONQUER] -> Lancement du sous-bloc B (taille: {len(part2)} chars)...")
        cards2 = extract_cards_from_chunk(client, part2, learning_depth, filename_tag=filename_tag, model=model, retries=retries)
        
        if cards1 is None:
            print("      [REPLI DIVIDE & CONQUER] Sous-bloc A a échoué. Mise en attente pour un rattrapage à la fin du découpage...")
        if cards2 is None:
            print("      [REPLI DIVIDE & CONQUER] Sous-bloc B a échoué. Mise en attente pour un rattrapage à la fin du découpage...")

        if cards1 is None:
            print("      [REPLI DIVIDE & CONQUER] Rattrapage final du sous-bloc A...")
            cards1 = extract_cards_from_chunk(client, part1, learning_depth, filename_tag=filename_tag, model=model, retries=retries)
        if cards2 is None:
            print("      [REPLI DIVIDE & CONQUER] Rattrapage final du sous-bloc B...")
            cards2 = extract_cards_from_chunk(client, part2, learning_depth, filename_tag=filename_tag, model=model, retries=retries)
        
        combined_cards = []
        if cards1:
            combined_cards.extend(cards1)
        if cards2:
            combined_cards.extend(cards2)
            
        if combined_cards:
            print(f"      [REPLI DIVIDE & CONQUER] ✅ Récupération réussie de {len(combined_cards)} cartes au total pour ce bloc !")
            return combined_cards

    print("Erreur: Impossible de traiter le chunk après plusieurs tentatives. Sautant ce chunk...")
    return None

def ai_quality_control_cards(client, cards, learning_depth, chunk_text="", image_descriptions=None, model="mistral-small-latest", retries=2):
    if not cards: return []
    
    print(f"   (Mistral Small : Agent QA actif sur {len(cards)} cartes...)")
    cards_payload = [{"id": i, "front": c.get("front", ""), "back": c.get("back", ""), "type": c.get("type", "")} for i, c in enumerate(cards)]
    payload_json = json.dumps(cards_payload, ensure_ascii=False)
    
    if learning_depth == "Zero Lecture":
        system_prompt = r"""
ROLE: Flashcard Quality Assurance Agent & Expert Typographe HTML/MathJax.
Vos flashcards contiennent parfois des références aveugles à un livre ("D'après la proposition 2.14") OU des erreurs de formatage.

TACHE: Evaluez chaque carte dans le JSON fourni pour les aspects suivants :
A. Le contexte visuel (CRITIQUE) : Si une carte contient une référence aveugle à une figure (ex: "Fig 2.3", "Points a, b, c"), vous DEVEZ vérifier dans le [TEXTE D'ORIGINE DU BLOC] fourni plus bas si cette image (représentée par `![img-x.jpeg](...)`) existe.
   - Si elle existe, REECRIVEZ la carte en injectant obligatoirement le lien exact de l'image à la fin du texte, sur sa propre ligne (ou avec un `<br>`).
   - Si l'image n'est VRAIMENT PAS dans le texte, alors seulement supprimez la référence aveugle ou rejetez la carte.
   - ATTENTION MULTI-IMAGES : Une figure peut comporter PLUSIEURS images côte à côte ou empilées dans le texte source. Vous DEVEZ IMPÉRATIVEMENT toutes les inclure dans la carte.
   - IMAGE INJECTION FORMAT (ABSOLUMENT CRITIQUE) : Les images `![img-x.jpeg](img-x.jpeg)` doivent être insérées librement dans le HTML, jamais dans une balise mathématique.

B. Références aveugles et autonomie (STRICT) : le texte (front/back) doit être 100% autonome.
   - Retirez toute phrase du type "Dans cet exemple", "the given example", "the provided example".
   - Remplacez ces références par le contenu réel.
   - Si la carte décrit un exercice mais que l'énoncé COMPLET n'est pas sur la carte, VOUS DEVEZ LE RÉÉCRIRE.

C. FORMATAGE STRICT (CRITIQUE) :
   - L'utilisation de `\text{}` ou de `\begin{aligned}` est STRICTEMENT INTERDITE.
   - Les environnements `\begin{array}` ou `\begin{matrix}` sont tolérés UNIQUEMENT à l'intérieur des blocs mathématiques `\[ ... \]` pour de vraies matrices mathématiques. Ils sont STRICTEMENT INTERDITS pour formater ou structurer du texte naturel.
   - Vous devez vous assurer que le texte naturel est en texte brut/HTML (utilisez `<b>` au lieu de `**`).
   - Vous devez vous assurer que CHAQUE expression mathématique (même une simple variable) est encadrée par `\( ... \)` pour l'inline, ou `\[ ... \]` pour le mode bloc. Vérifiez que toutes les balises `\(` sont bien fermées par `\)`. Corrigez les erreurs comme `\( X_a(t) \"` en `\( X_a(t) \)`.

D. Environnements LaTeX INVALIDS : (CRITIQUE)
   - NE JAMAIS UTILISER `\begin{itemize}` ou `\item`. Utilisez des balises HTML (`<ul>`, `<li>`) ou du texte brut (`-`).
   - NE JAMAIS UTILISER de délimiteurs mathématiques comme `$`, `$$`. Utilisez UNIQUEMENT `\(` et `\[`.

E. INJECTION D'IMAGE PROACTIVE INTERDITE : N'ajoutez JAMAIS d'image de votre propre chef à une carte "autonome".

F. Les cartes sans utilité pédagogique : Si la carte ne sollicite pas une notion du cours, rejetez-la.

G. CARTES IMAGE-SEULE (REJET SYSTÉMATIQUE) : Si le front d'une carte ne contient QU'UNE IMAGE sans question en langage naturel, REJETEZ LA avec "action": "reject".

H. CARTES "DÉCRIVEZ L'IMAGE" (REJET OU RÉÉCRITURE OBLIGATOIRE) : Si le front demande de "décrire", "expliquer" ou "identifier" ce que montre une image, cette carte est PÉDAGOGIQUEMENT FAIBLE et doit être réécrite pour poser une question conceptuelle.

I. CARTES QCM (RÉÉCRITURE OBLIGATOIRE OU REJET) : Les choix multiples (A, B, C, D) sont INTERDITS. Réécrivez en question ouverte directe.

J. FRONT INCOMPLET (REJET OU RÉÉCRITURE) : Si le front se termine par ":" ou "For example:" sans que le contenu annoncé soit présent, complétez-le ou corrigez-le.

K. BACK INCOMPLET (RÉÉCRITURE OBLIGATOIRE) : Si le back annonce une liste mais ne fournit pas la liste complète, complétez le back en utilisant le texte d'origine.

L. CONTEXTE EXPLICATIF CHECK (RÉÉCRITURE OBLIGATOIRE) : Si une carte de type "Basique" ne contient PAS de section "Contexte Explicatif" sur le back, vous DEVEZ la RÉÉCRIRE en ajoutant cette section à la fin du back. Format : `<hr><b>Contexte Explicatif :</b><br>...`

M. CLOZE OVERLOAD CHECK (REJET) : Si une carte "Texte à trous" contient plus de 3 clozes (ex: `{{c4::...}}`), REJETEZ LA.

Règles d'action :
1. Si la carte est une localisation ("Où est défini X?") ou est insolvable SANS image (et l'image est introuvable), renvoyez "action": "reject".
2. S'il faut insérer une image, corriger une référence, réparer le formatage (supprimer \text{}, ajouter \( \)), ou ajouter un Contexte Explicatif manquant, renvoyez "action": "rewrite", et donnez le texte parfaitement formaté.
3. Si la carte est parfaitement autonome, parfaitement formatée, ET contient le Contexte Explicatif, renvoyez "action": "keep".

IMPORTANT : Conserver rigoureusement la syntaxe des clozes (`{{c1::...}}`). Doubler les backslashes Latex dans le JSON (`\\(`, `\\[`, `\\frac`).

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
    elif learning_depth == "Intermediaire":
        system_prompt = r"""
        ROLE: Flashcard Quality Assurance Agent & HTML/MathJax Typography Expert.
Your flashcards sometimes contain blind references to a book ("According to proposition 2.14") OR formatting errors.

TASK: Evaluate each card in the provided JSON for the following aspects:
A. Visual context (CRITICAL): If a card contains a blind reference to a figure (e.g. "Fig 2.3", "Points a, b, c"), you MUST check in the [ORIGINAL CHUNK TEXT] provided below if this image (represented by `![img-x.jpeg](...)`) exists.
   - If it exists, REWRITE the card by obligatorily injecting the exact link to the image at the end of the text, on its own line (or with a `<br>`).
   - If the image is REALLY NOT in the text, then and only then remove the blind reference or reject the card.
   - MULTI-IMAGE WARNING: A figure can contain MULTIPLE images side-by-side or stacked in the source text. You MUST IMPERATIVELY include all of them in the card.
   - IMAGE INJECTION FORMAT (ABSOLUTELY CRITICAL): Images `![img-x.jpeg](img-x.jpeg)` must be inserted freely in HTML, never inside a mathematical tag.

B. Blind references and autonomy (STRICT): the text (front/back) must be 100% autonomous.
   - Remove any sentence like "In this example", "the given example", "the provided example".
   - Replace these references with the actual content.
   - If the card describes an exercise but the COMPLETE statement is not on the card, YOU MUST REWRITE IT.

C. STRICT FORMATTING (CRITICAL):
   - The use of `\text{}` or `\begin{aligned}` is STRICTLY FORBIDDEN.
   - `\begin{array}` or `\begin{matrix}` environments are tolerated ONLY inside mathematical blocks `\[ ... \]` for real mathematical matrices. They are STRICTLY FORBIDDEN to format or structure natural text.
   - You must ensure that natural text is in plain text/HTML (use `<b>` instead of `**`).
   - You must ensure that EVERY mathematical expression (even a simple variable) is enclosed by `\( ... \)` for inline, or `\[ ... \]` for block mode. Verify that all `\(` or '\[' tags are properly closed by `\)` or '\]' respectively. Fix errors like `\( X_a(t) \"` to `\( X_a(t) \)`.

D. INVALID LaTeX Environments: (CRITICAL)
   - NEVER USE `\begin{itemize}` or `\item`. Use HTML tags (`<ul>`, `<li>`) or plain text (`-`).
   - NEVER USE mathematical delimiters like `$`, `$$`. Use ONLY `\(` and `\[`.


F. Cards without pedagogical utility: If the card does not test a course concept, reject it.

G. IMAGE-ONLY CARDS (SYSTEMATIC REJECTION): If the front of a card ONLY contains an IMAGE without a natural language question, REJECT IT with "action": "reject".

H. "DESCRIBE THE IMAGE" CARDS (MANDATORY REJECTION OR REWRITE): If the front asks to "describe", "explain" or "identify" what an image shows, this card is PEDAGOGICALLY WEAK and must be rewritten to ask a conceptual question.

I. MCQ CARDS (MANDATORY REWRITE OR REJECT): Multiple choices (A, B, C, D) are FORBIDDEN. Rewrite as a direct open question.

J. INCOMPLETE FRONT (REJECT OR REWRITE): If the front ends with ":" or "For example:" without the announced content present in the front or in the back, complete it or fix it.

K. INCOMPLETE BACK (MANDATORY REWRITE): If the back announces a list but does not provide the full list, complete the back using the original text.

L. EXPLANATORY CONTEXT CHECK (MANDATORY REWRITE): If a "Basique" card does NOT contain an "Contexte Explicatif" / "Explanatory Context" section on the back, you MUST REWRITE IT by adding this section at the end of the back. Format: `<hr><b>Contexte Explicatif :</b><br>...`

M. CLOZE OVERLOAD CHECK (REJECT): If a "Texte à trous" card contains more than 5 clozes (e.g., {{c6::...}}), REJECT IT or REWRITE IT by grouping the extra clozes to ensure there are no more than 5 in total

N. DE-DUPLICATION AND MERGING (CRITICAL):
- Identification: If multiple cards cover the same concept or are redundant variants, you must merge them.
- Merging Strategy (IMPERATIVE):
- Master Card: The first card in the group (the one with the lowest ID) becomes the "Master Card." You must update it (action: "rewrite") to incorporate all relevant information from the redundant cards.
- Duplicates: All other cards covering this same concept must be rejected (action: "reject").
- Reasoning: For each rejected card, you must state: "Merged into Master Card ID [ID]".
- Ordering: The Master Card retains its original ID. Do not create new IDs.


Action Rules:
1. If the card is a location ("Where is X defined?") or is unsolvable WITHOUT an image (and the image is missing), return "action": "reject".
2. If an image needs to be inserted, a reference fixed, merged, formatting repaired (remove \text{}, add \( \)), or a missing Explanatory Context added, return "action": "rewrite", and provide the perfectly formatted text.
3. If the card is perfectly autonomous, perfectly formatted, AND contains the Explanatory Context, return "action": "keep".

IMPORTANT: Strictly preserve cloze syntax (`{{c1::...}}`). Double the LaTeX backslashes in the JSON (`\\(`, `\\[`, `\\frac`).

PRECISE JSON OUTPUT:
{
    "results": [
        {
            "id": 0,
            "action": "keep" | "reject" | "rewrite",
            "front": "the corrected text if rewrite",
            "back": "the corrected text if rewrite",
            "reasoning": "rationale for the decision"
        }
    ]
}"""
    dynamic_max_tokens = 16000
    retries = 3
    current_model = model
    
    base_user_msg = f"[ORIGINAL CHUNK TEXT FOR IMAGE REFERENCE AND CONTEXT]\n{chunk_text}\n\n" + (f"[IMAGE INDEX AND THEIR DESCRIPTIONS]\n" + "\n".join([f"- {k}: {v}" for k, v in (image_descriptions or {}).items() if v]) + "\n\n" if image_descriptions else "") + f"=======================\nHere are the cards to evaluate and correct:\n{payload_json}"
    current_messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": base_user_msg}
    ]
    accumulated_content = ""
    
    for attempt in range(retries):
        if attempt == 2 and current_model == "mistral-small-latest":
            print("   ⚠️ Mistral Small indisponible (2 échecs). Bascule de secours (failover) sur Mistral Large...")
            current_model = "mistral-large-latest"
            
        try:
            response = client.chat.complete(
                model=current_model,
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
                messages=current_messages,
                max_tokens=dynamic_max_tokens
            )
            content = response.choices[0].message.content
            full_content = accumulated_content + content
            data = parse_and_repair_json(client, full_content, model=current_model)
            
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
                                f.write("## [MISTRAL QA] Carte Rejetée\n\n")
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
                                f.write("## [MISTRAL QA] Carte Corrigée\n\n")
                                f.write("### Avant:\n```json\n" + json.dumps({"front": old_front, "back": old_back}, ensure_ascii=False, indent=2) + "\n```\n\n")
                                f.write("### Après:\n```json\n" + json.dumps({"front": c["front"], "back": c["back"]}, ensure_ascii=False, indent=2) + "\n```\n\n---\n")
                        except Exception as e:
                            print(f"Log Error: {e}")
                    else:
                        valid_cards.append(c)
                
                print(f"   => Contrôle Qualité terminé : {len(valid_cards)} cartes conservées dont {rewritten_count} corrigées. {rejected_count} rejetées.")
                return valid_cards
        except Exception as e:
            if "Prefix does not match the response format" in str(e) or "invalid_request_invalid_args" in str(e):
                print(f"      [TRONCATURE QA] Le préfixe a été rejeté par l'API (Erreur 400). Régénération complète sans préfixe (Tentative {attempt+1}/{retries})...")
                current_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": base_user_msg}
                ]
                accumulated_content = ""
                time.sleep(2)
                continue

            print(f"   Erreur QA Mistral ({current_model}) (Tentative {attempt+1}/{retries}): {e}")
            full_content_ref = locals().get("full_content", locals().get("content", ""))
            if "JSON tronqué" in str(e) and len(full_content_ref) >= 50000:
                print("   => Le JSON retourné a été tronqué à plus de 50 000 caractères. Augmentation de max_tokens à 32000 pour les prochaines tentatives.")
                dynamic_max_tokens = 32000
                
            if isinstance(e, json.JSONDecodeError) and "JSON tronqué détecté" in str(e):
                print(f"      [TRONCATURE QA] JSON tronqué détecté. Demande de réécriture complète à l'IA (Tentative {attempt+1}/{retries})...")
                truncated_json = full_content_ref if full_content_ref else e.doc
                accumulated_content = ""
                current_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": base_user_msg},
                    {"role": "assistant", "content": truncated_json},
                    {"role": "user", "content": "Your previous JSON response was truncated. Please rewrite it ENTIRELY from the beginning, starting exactly with the JSON you already wrote above, and then complete the object. Output ONLY the valid completed JSON."}
                ]
            time.sleep(2)
            
    print("   QA a échoué. Retour des cartes non filtrées.")
    return cards

def filter_image_only_cards(cards):
    """Filtre post-QA : rejette les cartes dont le front ne contient que des images sans texte."""
    filtered = []
    rejected_count = 0
    for c in cards:
        front = c.get("front", "")
        # Retirer les images
        robust_pattern_img = r'\\*!?\\*\[([^\]]*?)\\*\]\\*\(([^)]+?\.(?:jpeg|jpg|png|gif|webp|svg))\\*\)'
        text_only = re.sub(robust_pattern_img, '', front, flags=re.IGNORECASE)
        # Nettoyage des balises HTML basiques pour l'évaluation de la longueur
        text_only = re.sub(r'<[^>]+>', '', text_only)
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
    
    mcq_front_patterns = [
        r'(?i)which\s+(?:of\s+the\s+following|statement)',
        r'(?i)select\s+the\s+(?:correct|incorrect)',
        r'(?i)identify\s+the\s+(?:correct|incorrect)',
        r'(?i)(?:the\s+)?incorrect\s+specification',
        r'(?i)laquelle?\s+(?:de\s+ces|des\s+suivant)',
        r'(?i)choisissez?\s+la\s+(?:bonne|correcte)',
        r'(?i)(?:true|false|vrai|faux)\s*(?:\?|$)',
    ]
    
    for c in cards:
        front = c.get("front", "")
        back = c.get("back", "")
        is_mcq = False
        matched_pattern = ""
        
        for pattern in mcq_front_patterns:
            if re.search(pattern, front):
                is_mcq = True
                matched_pattern = pattern
                break
        
        # La détection naïve de (a)(b)(c) a été retirée car elle provoque des faux positifs avec les sous-figures.
        
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

def repair_truncated_card(client, card, chunk_text, reason, model="mistral-large-latest"):
    """
    Calls Mistral to repair a truncated/incomplete card using the original chunk text.
    Returns the repaired card dict, or None if repair fails.
    """
    front = card.get("front", "")
    back = card.get("back", "")
    card_type = card.get("type", "Basique")
    
    prompt = f"""ROLE: Anki Card Repair Expert.
The following flashcard of type "{card_type}" was flagged as incomplete or truncated:
- Reason for truncation: {reason}
- Current Front: {front}
- Current Back: {back}

Original context segment from the course:
\"\"\"
{chunk_text}
\"\"\"

TASK:
Perfecty repair this flashcard using the original course context.

CRITICAL RULES FOR REPAIR:
1. COMPLETENESS:
   - The Front must contain a complete, grammatically sound and pedagogically rich question or statement.
   - The Back must provide a fully complete explanation without leaving anything cut off (never end with ":" or incomplete lists).
2. CARD TYPE RULES:
   - If type is "Basique" (Basic): The Back MUST include a "Contexte Explicatif" section at the very end. Format it EXACTLY as:
     `<hr><b>Contexte Explicatif :</b><br>[1-3 sentences of plain-language intuition and everyday analogies]`
   - If type is "Texte à trous" (Cloze): You MUST preserve and repair any standard Anki cloze deletions (e.g., `{{c1::...}}`). Do not lose them, and do not change the card type.
3. MATHEMATICAL & LATEX FORMATTING (CRITICAL):
   - Double-escape ALL LaTeX backslashes in the output JSON (e.g., write `\\(`, `\\)`, `\\frac`, `\\[`, `\\]`).
   - Use `\\(` and `\\)` for inline math, and `\\[` and `\\]` for block math.
   - STRICTLY FORBIDDEN: Do NOT use `$`, `$$`, `\\text{{}}`, `\\begin{{aligned}}`, `\\begin{{itemize}}`, or `\\item`.
   - Use HTML tags like `<ul>` and `<li>` for lists, and `<b>` for bold text.
4. IMAGES:
   - Retain any existing image tags (like `![img-x.jpeg](img-x.jpeg)`) exactly if they are present in the original card.
5. LANGUAGE:
   - Keep the exact same language as the original card 

Output strictly a JSON object in this format (do not wrap in markdown blocks, output raw JSON):
{{
    "front": "Repaired front text...",
    "back": "Repaired back text..."
}}
"""
    try:
        response = client.chat.complete(
            model=model,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a professional Anki card editor. Repair truncated flashcards perfectly."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8000
        )
        content = response.choices[0].message.content
        data = parse_and_repair_json(client, content, model=model)
        if "front" in data and "back" in data:
            repaired = card.copy()
            repaired["front"] = data["front"]
            repaired["back"] = data["back"]
            print(f"      [RÉPARATION RÉUSSIE] Carte réparée avec succès ! (Raison : {reason})")
            return repaired
    except Exception as e:
        print(f"      [ÉCHEC RÉPARATION] Impossible de réparer la carte : {e}")
    return None

def filter_truncated_cards(client, cards, chunk_text=""):
    """Post-QA filter: detect cards with truncated fronts or incomplete backs, and try to repair them."""
    filtered = []
    rejected_count = 0
    repaired_count = 0
    
    for c in cards:
        front = c.get("front", "")
        back = c.get("back", "")
        is_truncated = False
        reason = ""
        
        front_clean = re.sub(r'<[^>]+>', '', front).strip()
        back_clean = re.sub(r'<[^>]+>', '', back).strip()
        
        if re.search(r'(?:For example|Par exemple)\s*:?\s*$', front_clean, re.IGNORECASE):
            is_truncated = True
            reason = "Front se termine par 'For example:' sans contenu"
        
        if not is_truncated and back_clean.endswith(':'):
            if len(back_clean) < 200:
                is_truncated = True
                reason = f"Back se termine par ':' sans lister les éléments annoncés ('{back_clean[-60:]}...')"
        
        if not is_truncated and len(back_clean) < 30 and len(front_clean) > 50:
            is_truncated = True
            reason = f"Back anormalement court ({len(back_clean)} chars) pour un front de {len(front_clean)} chars"
        
        if is_truncated:
            if client and chunk_text:
                print(f"      [TRONCATURE DÉTECTÉE] Tentative de réparation de la carte : {front_clean[:80]}...")
                repaired_card = repair_truncated_card(client, c, chunk_text, reason)
                if repaired_card:
                    filtered.append(repaired_card)
                    repaired_count += 1
                    try:
                        with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                            f.write("## [FILTRE TRONCATURE] Carte Réparée avec Succès\n\n")
                            f.write(f"**Raison de troncature :** {reason}\n\n")
                            f.write(f"**Ancien Front :**\n{front}\n\n**Ancien Back :**\n{back}\n\n")
                            f.write(f"**Nouveau Front :**\n{repaired_card.get('front')}\n\n**Nouveau Back :**\n{repaired_card.get('back')}\n\n---\n")
                    except: pass
                    continue
            
            rejected_count += 1
            print(f"      [FILTRE TRONCATURE] Carte rejetée : {front_clean[:80]}...")
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [FILTRE TRONCATURE] Carte Rejetée\n\n")
                    f.write(f"### Raison:\n{reason}\n\n")
                    f.write(f"### Front:\n```\n{front}\n```\n\n")
                    f.write(f"### Back:\n```\n{back}\n```\n\n---\n")
            except Exception as e:
                print(f"Log Error: {e}")
            continue
        filtered.append(c)
    
    if rejected_count > 0 or repaired_count > 0:
        print(f"   => Filtre troncature : {repaired_count} carte(s) réparée(s), {rejected_count} rejetée(s), {len(filtered)} conservée(s).")
    return filtered

def filter_cloze_overload(cards):
    """V1.1: Post-QA filter: reject Cloze cards with more than 3 cloze deletions."""
    filtered = []
    rejected_count = 0
    
    for c in cards:
        if "trous" not in c.get("type", "").lower():
            filtered.append(c)
            continue
        
        front = c.get("front", "")
        back = c.get("back", "")
        combined = front + " " + back
        
        # Count unique cloze indices for standard Anki clozes {{c1::...}}
        cloze_indices = set(re.findall(r'\{\{c(\d+)::', combined))
        
        if len(cloze_indices) > 3:
            tags = c.get("tags", "")
            if isinstance(tags, list):
                tags = " ".join(str(t) for t in tags)
            else:
                tags = str(tags)
            if "Cloze_Overload" not in tags:
                c["tags"] = (tags + " Catégorie::Cloze_Overload").strip()
            print(f"      [FILTRE CLOZE V1.1] Carte marquée comme surchargée ({len(cloze_indices)} clozes > 3 max) : {front[:80]}...")
            try:
                with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                    f.write("## [FILTRE CLOZE OVERLOAD V1.1] Carte Marquée\n\n")
                    f.write(f"### Raison:\nTrop de cloze deletions ({len(cloze_indices)} > 3 max). Marquée avec le tag 'Catégorie::Cloze_Overload'.\n\n")
                    f.write(f"### Front:\n```\n{front[:200]}\n```\n\n---\n")
            except Exception as e:
                print(f"Log Error: {e}")
        filtered.append(c)
    
    if rejected_count > 0:
        print(f"   => Filtre cloze overload V1.1 : {rejected_count} carte(s) rejetée(s), {len(filtered)} conservée(s).")
    return filtered

def audit_elaboration_quota(cards):
    if not cards:
        return cards
    
    true_elab_patterns = [
        r'(?i)why\s+(?:does|do|is|are|can|cannot|would|must)\s',
        r'(?i)what\s+would\s+happen\s+(?:if|when)',
        r'(?i)what\s+is\s+the\s+(?:physical|mathematical|fundamental|underlying)\s+reason',
        r'(?i)explain\s+why\s+\w+\s+(?:does|is|are|cannot|requires)',
        r'(?i)how\s+does\s+\w+\s+(?:cause|lead|result|affect|prevent|ensure)',
        r'(?i)what\s+(?:distinguishes|is\s+the\s+trade-off)',
        r'(?i)compare\s+(?:and\s+contrast|the\s+(?:advantages|limitations))',
        r'(?i)under\s+what\s+conditions?\s+(?:does|would|can)',
        r'(?i)pourquoi\s+(?:est-ce|faut-il|ne\s+peut-on)',
        r'(?i)quelle?\s+(?:est|sont)\s+(?:la|les?)\s+(?:raison|cause)',
    ]
    false_elab_patterns = [
        r'(?i)(?:how|comment)\s+(?:does|is|are)\s+\w+\s+(?:defined|calculated|expressed|represented)',
        r'(?i)what\s+(?:is|are)\s+the\s+(?:effect|definition|formula|expression|value)',
        r'(?i)(?:why|pourquoi)\s+is\s+\w+\s+important',
    ]
    
    elaborative_count = 0
    total_basique = 0
    
    for c in cards:
        if c.get("type", "").strip() != "Basique":
            continue
        total_basique += 1
        front = c.get("front", "")
        front_clean = re.sub(r'<[^>]+>', '', front).strip()
        
        is_false = any(re.search(p, front_clean) for p in false_elab_patterns)
        is_true = (not is_false) and any(re.search(p, front_clean) for p in true_elab_patterns)
        
        if is_true:
            elaborative_count += 1
            tags = c.get("tags", "")
            if isinstance(tags, list):
                tags = " ".join(str(t) for t in tags)
            else:
                tags = str(tags)
            if "Elaborative_Interrogation" not in tags:
                c["tags"] = (tags + " Catégorie::Elaborative_Interrogation").strip()
    
    quota_pct = (elaborative_count / total_basique * 100) if total_basique > 0 else 0
    status = "ATTEINT" if quota_pct >= 15.0 else "SOUS LE SEUIL"
    print(f"   => Audit Elaboration V1.1 : {elaborative_count}/{total_basique} Basique elaboratives ({quota_pct:.1f}%) -- {status}")
    
    try:
        with open("pipeline_logs.md", "a", encoding="utf-8") as f:
            f.write(f"## [AUDIT ELABORATION V1.1]\n\n")
            f.write(f"- **Basique totales:** {total_basique}\n- **Elaboratives:** {elaborative_count} ({quota_pct:.1f}%)\n")
            f.write(f"- **Statut:** {status}\n\n---\n")
    except Exception as e:
        print(f"Log Error: {e}")
    return cards

def coverage_audit_agent(client, all_cards, chunks, full_markdown, learning_depth ="Zero Lecture", filename_tag="Course", image_descriptions=None):
    if not chunks or not all_cards:
        return all_cards
    
    print(f"\n   (Agent Couverture V1.1 -- Audit sur {len(chunks)} blocs...)")
    
    chunk_headers = []
    for chunk in chunks:
        header = ""
        for line in chunk.split("\n"):
            line = line.strip()
            if line and not line.startswith("!["):
                header = line[:120]
                break
        chunk_headers.append(header)
    
    chunk_card_counts = [0] * len(chunks)
    for c in all_cards:
        card_text = (c.get("front", "") + " " + c.get("back", "")).lower()
        for ci, chunk in enumerate(chunks):
            chunk_terms = set(re.findall(r'[a-zA-Z]{4,}', chunk[:500].lower()))
            if chunk_terms and sum(1 for t in chunk_terms if t in card_text) >= 3:
                chunk_card_counts[ci] += 1
    
    under_covered = []
    for ci, (count, chunk) in enumerate(zip(chunk_card_counts, chunks)):
        text_len = len(re.sub(r'!\[.*?\]\(.*?\)', '', chunk))
        if count < 2 and text_len > 200:
            under_covered.append((ci, chunk, count, chunk_headers[ci]))
    
    if not under_covered:
        print(f"   => Couverture complete : tous les blocs ont >= 2 cartes.")
        return all_cards
    
    print(f"   => {len(under_covered)} bloc(s) sous-couverts. Generation complementaire...")
    def _process_under_covered(ci, chunk, count, header):
        print(f"      -> Bloc {ci+1} ({header[:60]}...): {count} carte(s), relance...")
        try:
            supplementary = extract_cards_from_chunk(client, chunk, "Zero Lecture", filename_tag=filename_tag)
            if supplementary:
                supplementary = ai_quality_control_cards(client, supplementary, chunk_text=chunk, image_descriptions=image_descriptions)
                supplementary = filter_image_only_cards(supplementary)
                supplementary = filter_mcq_cards(supplementary)
                supplementary = filter_truncated_cards(supplementary)
                supplementary = filter_cloze_overload(supplementary)
                print(f"        + {len(supplementary)} cartes complementaires.")
                return supplementary
        except Exception as e:
            print(f"        Erreur bloc {ci+1}: {e}")
        return []

    new_cards = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_process_under_covered, ci, chunk, count, header) for ci, chunk, count, header in under_covered]
        for future in as_completed(futures):
            res = future.result()
            if res:
                new_cards.extend(res)
    
    try:
        with open("pipeline_logs.md", "a", encoding="utf-8") as f:
            f.write(f"## [COVERAGE AUDIT V1.1]\n\n")
            f.write(f"- **Sous-couverts:** {len(under_covered)}\n- **Complementaires:** {len(new_cards)}\n\n---\n")
    except Exception as e:
        print(f"Log Error: {e}")
    return all_cards + new_cards

def generate_bridge_cards(client, chunks, all_cards, filename_tag="Course"):
    if len(chunks) < 2:
        return []
    
    print(f"\n   (Agent Bridge V1.1 -- Generation cartes-pont inter-sections...)")
    
    pairs = [(chunks[i], chunks[i+1]) for i in range(len(chunks)-1)]
    
    bridge_prompt = r"""
ROLE: Bridge Card Generator.
You are evaluating two consecutive sections of a course.
TASK: Determine if there is a STRONG, pedagogically useful conceptual link between Section A and Section B that warrants a synthesis "Bridge" flashcard.

RULES:
1. If the connection is weak, superficial, or if they are just unrelated topics next to each other, set "is_bridge_useful" to false and return an empty cards list.
2. If the connection is strong and useful for the student's understanding, set "is_bridge_useful" to true, explain why in "reasoning", and generate EXACTLY ONE Bridge Card.
3. Card type MUST be "Basique", subdeck MUST be "04_Synthèse_et_Relations".
4. tags: a SPACE-SEPARATED STRING (not a list). Include "Catégorie::Bridge" after the filename tag.
5. front: comparative, relational, or synthesizing question
6. back: synthesized explanation + a Contexte Explicatif section (2-3 sentences of plain-language intuition)
7. JSON: double-escape ALL backslashes (e.g. `\\frac`, `\\[`, `\\(`)
8. Format: Plain text / HTML with MathJax `\( ... \)` or `\[ ... \]`. NO `\text{}` or `\begin{aligned}`.
9. LANGUAGE: MUST be the same language as the sections.

OUTPUT JSON FORMAT:
{
  "is_bridge_useful": true,
  "reasoning": "...",
  "cards": [
    {"type": "Basique", "subdeck": "04_Synthèse_et_Relations", "front": "...", "back": "...", "tags": "FilenameTag Catégorie::Bridge"}
  ]
}
"""
    
    def _generate_single_bridge(idx, secA, secB):
        # Truncate to first 4000 chars to avoid overwhelming the context but give enough meat to understand.
        contentA = secA[:4000] + ("..." if len(secA) > 4000 else "")
        contentB = secB[:4000] + ("..." if len(secB) > 4000 else "")
        
        retries = 3
        current_model = "mistral-small-latest"
        for attempt in range(retries):
            if attempt == 2 and current_model == "mistral-small-latest":
                print(f"      ⚠️ Mistral Small indisponible pour la carte Bridge. Bascule de secours (failover) sur Mistral Large...")
                current_model = "mistral-large-latest"
            try:
                response = client.chat.complete(
                    model=current_model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": bridge_prompt},
                        {"role": "user", "content": f"Section A:\n{contentA}\n\n=======================\nSection B:\n{contentB}\n\nFilename tag: {filename_tag}"}
                    ],
                    max_tokens=8000
                )
                content = response.choices[0].message.content
                data = parse_and_repair_json(client, content, model=current_model)
                if data.get("is_bridge_useful") and "cards" in data and data["cards"]:
                    bc = data["cards"][0]
                    tags_val = bc.get("tags", "")
                    if isinstance(tags_val, list):
                        tags_val = " ".join(str(t) for t in tags_val)
                    if "Bridge" not in tags_val:
                        tags_val = tags_val + " Catégorie::Bridge"
                    bc["tags"] = tags_val
                    print(f"      [BRIDGE OK] Lien utile trouvé entre bloc {idx+1} et {idx+2}.")
                    return bc
                else:
                    print(f"      [BRIDGE REJETÉ] Aucun lien pertinent entre bloc {idx+1} et {idx+2}.")
                    return None
            except Exception as e:
                print(f"      [TENTATIVE BRIDGE {attempt+1}/{retries}] Erreur : {e}")
                time.sleep(2)
        return None

    bridge_cards = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_generate_single_bridge, i, secA, secB) for i, (secA, secB) in enumerate(pairs)]
        for future in as_completed(futures):
            res = future.result()
            if res:
                bridge_cards.append(res)
    
    print(f"   => Bridge Cards V1.1 : {len(bridge_cards)} cartes-pont pour {len(pairs)} transitions.")
    
    try:
        with open("pipeline_logs.md", "a", encoding="utf-8") as f:
            f.write(f"## [BRIDGE CARDS V1.1]\n\n- **Generees:** {len(bridge_cards)}/{len(pairs)}\n\n---\n")
    except Exception as e:
        print(f"Log Error: {e}")
    return bridge_cards

def audit_image_coverage(cards, chunk_text, image_descriptions=None):
    if not cards or not chunk_text:
        return cards
    
    import re
    
    chunk_images = set(re.findall(r'!\[.*?\]\(([^)]+\.(?:jpeg|jpg|png|gif|webp|svg))\)', chunk_text, re.IGNORECASE))
    
    if chunk_images:
        covered_images = set()
        for c in cards:
            front = normalize_image_references(c.get("front", ""))
            back = normalize_image_references(c.get("back", ""))
            card_imgs = set(re.findall(r'([\w.-]+\.(?:jpeg|jpg|png|gif|webp|svg))', front + " " + back, re.IGNORECASE))
            covered_images.update(card_imgs)
        
        missing_images = chunk_images - covered_images
        
        if missing_images:
            injected_count = 0
            warned_count = 0
            
            for missing_img in missing_images:
                img_desc = (image_descriptions or {}).get(missing_img, "")
                best_card_idx = -1
                best_score = 0
                
                desc_words = set()
                if img_desc:
                    desc_words = set(w.lower() for w in re.findall(r'[a-zA-Z]{3,}', img_desc))
                
                for idx_c, c in enumerate(cards):
                    card_text = (c.get("front", "") + " " + c.get("back", "")).lower()
                    if desc_words:
                        score = sum(1 for w in desc_words if w in card_text)
                        if score > best_score:
                            best_score = score
                            best_card_idx = idx_c
                    else:
                        break
                
                if best_card_idx >= 0 and best_score >= 2:
                    c = cards[best_card_idx]
                    img_ref = f"<br>![{missing_img}]({missing_img})"
                    c["back"] = c.get("back", "") + img_ref
                    injected_count += 1
                    print(f"      [AUDIT IMAGE] Image manquante '{missing_img}' injectee dans carte {best_card_idx} (score: {best_score})")
                    try:
                        with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                            f.write(f"## [AUDIT IMAGE V1.1] Image manquante injectee\n\n")
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
                            f.write(f"## [AUDIT IMAGE V1.1] Image non couverte (avertissement)\n\n")
                            f.write(f"- **Image:** {missing_img}\n")
                            f.write(f"- **Description:** {img_desc if img_desc else '(aucune annotation)'}\n")
                            f.write(f"- **Raison:** Aucune carte avec un score de correspondance suffisant (meilleur: {best_score})\n\n---\n")
                    except Exception as e:
                        print(f"Log Error: {e}")
            
            if injected_count > 0 or warned_count > 0:
                print(f"   => Audit images : {injected_count} image(s) injectee(s), {warned_count} avertissement(s).")

    mention_terms = [
        r'figure', r'fig\.', r'schéma', r'schema', r'graphe', r'graphique', 
        r'image', r'diagramme', r'courbe', r'illustration', r'dessin', 
        r'photo', r'photographie', r'représentation', r'trace',
        r'diagram', r'graph', r'chart', r'plot', r'picture', 
        r'drawing', r'photograph', r'representation', r'sketch'
    ]
    mention_pattern = r'(?i)\b(?:' + '|'.join(mention_terms) + r')\b'
    
    draw_terms = [
        r'dessiner', r'dessinez',
        r'tracer', r'tracez',
        r'schématiser', r'schématisez', r'schematiser', r'schematisez',
        r'reproduire', r'reproduisez',
        r'représenter', r'représentez', r'representer', r'representez',
        r'esquisser', r'esquissez',
        r'construire', r'construisez',
        r'illustrer', r'illustrez',
        r'draw', r'draws', r'drawn',
        r'sketch', r'sketched', r'sketching',
        r'plot', r'plotted', r'plotting',
        r'reproduce', r'reproduces', r'reproduced', r'reproducing',
        r'represent', r'represents', r'represented', r'representing',
        r'construct', r'constructs', r'constructed', r'constructing',
        r'illustrate', r'illustrates', r'illustrated', r'illustrating'
    ]
    draw_pattern = r'(?i)\b(?:' + '|'.join(draw_terms) + r')\b'
    front_pushed_count = 0
    for c in cards:
        front = normalize_image_references(c.get("front", ""))
        if re.search(mention_pattern, front) and not re.search(draw_pattern, front):
            back = normalize_image_references(c.get("back", ""))
            back_imgs = set(re.findall(r'!\[.*?\]\(([^)]+\.(?:jpeg|jpg|png|gif|webp|svg))\)', back, re.IGNORECASE) + \
                            re.findall(r'<img[^>]+src=["\']([^"\']+\.(?:jpeg|jpg|png|gif|webp|svg))["\']', back, re.IGNORECASE))
            front_imgs = set(re.findall(r'!\[.*?\]\(([^)]+\.(?:jpeg|jpg|png|gif|webp|svg))\)', front, re.IGNORECASE) + \
                             re.findall(r'<img[^>]+src=["\']([^"\']+\.(?:jpeg|jpg|png|gif|webp|svg))["\']', front, re.IGNORECASE))
            
            missing_in_front = back_imgs - front_imgs
            for img in missing_in_front:
                c["front"] = c.get("front", "") + f"<br>![{img}]({img})"
                front_pushed_count += 1
                print(f"      [AUDIT IMAGE] Image '{img}' copiée vers le front (mention textuelle détectée)")
                try:
                    with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                        f.write(f"## [AUDIT IMAGE V1.13] Image poussée vers le front\n")
                        f.write(f"- L'image **{img}** a été ajoutée au front car ce dernier mentionne une figure.\n")
                        f.write(f"- **Nouveau Front:** {c.get('front', '')[:80]}...\n\n---\n")
                except:
                    pass

    if front_pushed_count > 0:
        print(f"   => Audit images : {front_pushed_count} image(s) copiée(s) vers le front.")
    
    return cards

def supervisor_deduplicate_cards(client, cards, similarity_threshold = 0.88, image_descriptions=None, model="mistral-large-latest", retries=5):
    if len(cards) <= 1:
        return cards
        
    report_progress(3, "Identification doublons : calcul des embeddings...", 0.1)
    print(f"\n   (Agent Superviseur - Étape 1 : Identification sémantique des doublons...)")
    texts = []
    for c in cards:
        front = re.sub(r'<[^>]+>', ' ', c.get("front", "")).strip()
        texts.append(front[:200])
    
    all_embeddings = []
    batch_size = 64
    try:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            response = client.embeddings.create(model="mistral-embed", inputs=batch)
            for item in response.data:
                all_embeddings.append(item.embedding)
            
            ratio = min(0.1 + 0.4 * (i + len(batch)) / len(texts), 0.5)
            report_progress(3, f"Calcul des embeddings... ({len(all_embeddings)}/{len(texts)})", ratio)
            
            if i + batch_size < len(texts):
                time.sleep(0.5)
    except Exception as e:
        print(f"   Erreur embeddings dans le Superviseur: {e}. On continue sans déduplication.")
        return cards
        
    if len(all_embeddings) != len(cards):
        print(f"   Mismatch embeddings vs cards. On continue sans déduplication.")
        return cards
        
    def cosine_sim(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        import math
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na and nb else 0.0
        
    n = len(cards)
    assigned = [False] * n
    duplicate_groups = []
    
    for i in range(n):
        if assigned[i]:
            continue
        cluster = [i]
        assigned[i] = True
        for j in range(i + 1, n):
            if assigned[j]:
                continue
            if cosine_sim(all_embeddings[i], all_embeddings[j]) >= similarity_threshold:
                cluster.append(j)
                assigned[j] = True
        if len(cluster) > 1:
            duplicate_groups.append(cluster)

    if not duplicate_groups:
        report_progress(3, "Aucun doublon détecté.", 1.0)
        print("   => Aucun doublon détecté, passage direct à l'assemblage.")
        return cards

    print(f"   (Agent Superviseur - Étape 1.5 : Vérification sémantique profonde sur {len(duplicate_groups)} groupes...)")
    
    all_group_indices = []
    for group in duplicate_groups:
        all_group_indices.extend(group)
    
    unique_indices = sorted(list(set(all_group_indices)))
    idx_to_emb_map = {}
    
    texts_to_embed = []
    for idx in unique_indices:
        c = cards[idx]
        full_content = (c.get("front", "") + " " + c.get("back", "")).strip()
        full_content = re.sub(r'<[^>]+>', ' ', full_content)
        texts_to_embed.append(full_content[:25000])

    try:
        batch_size = 64
        all_full_embeddings = []
        for i in range(0, len(texts_to_embed), batch_size):
            batch = texts_to_embed[i:i+batch_size]
            response = client.embeddings.create(model="mistral-embed", inputs=batch)
            for item in response.data:
                all_full_embeddings.append(item.embedding)
            
            ratio = min(0.5 + 0.4 * (i + len(batch)) / len(texts_to_embed), 0.9)
            report_progress(3, f"Vérification profonde... ({len(all_full_embeddings)}/{len(texts_to_embed)})", ratio)
            
            if i + batch_size < len(texts_to_embed):
                time.sleep(0.5)
        
        for idx, emb in zip(unique_indices, all_full_embeddings):
            idx_to_emb_map[idx] = emb
            
        refined_groups = []
        full_similarity_threshold = similarity_threshold+0.02 
        
        for group in duplicate_groups:
            master_idx = group[0]
            master_emb = idx_to_emb_map.get(master_idx)
            if master_emb is None:
                refined_groups.append(group)
                continue
                
            valid_members = [master_idx]
            for i in range(1, len(group)):
                other_idx = group[i]
                other_emb = idx_to_emb_map.get(other_idx)
                if other_emb is not None:
                    sim = cosine_sim(master_emb, other_emb)
                    if sim >= full_similarity_threshold:
                        valid_members.append(other_idx)
                    else:
                        print(f"      [INFO] Carte {other_idx} écartée du groupe {master_idx} (sim content: {sim:.3f} < {full_similarity_threshold})")
            
            if len(valid_members) > 1:
                refined_groups.append(valid_members)
            else:
                print(f"      [INFO] Groupe {master_idx} dissous après vérification profonde.")
        
        duplicate_groups = refined_groups
        
    except Exception as e:
        print(f"   [ERREUR] Échec vérification profonde: {e}. On continue avec les groupes originaux par précaution.")

    all_deleted_ids = set()
    completed_groups = 0
    progress_lock = threading.Lock()
    report_progress(4, f"Fusion des doublons : groupe 0/{len(duplicate_groups)}", 0.0)
    print(f"   => {len(duplicate_groups)} groupes de doublons confirmés. Lancement de la fusion ciblée...")
    
    prompt_fuse = r"""
ROLE: Combiner Agent.
YOUR TASK: You are given a set of POTENTIALLY REDUNDANT Anki flashcards. Decide if they TRULY cover the exact same structural concept and merge them if so.

CRITICAL RULES FOR COMBINING (IF MERGING):
1. THEOREM/PROOF PRESERVATION: If any input card contains a PROOF, include the FULL proof on the back of the merged card.
2. CONTEXTUAL RECONSTRUCTION: For theorems, the Front MUST contain the statement, and the Back MUST contain the FULL PROOF.
3. EXAMPLES ZERO-CONTEXT RULE: The merged card MUST be 100% self-contained. ABSOLUTELY NEVER write things like "In Example 1...". 
4. JSON BACKSLASH ESCAPING: You MUST double-escape EVERY single backslash (e.g. `\\frac`, `\\[`, `\\(`).
5. FORMATTING: Use plain text/HTML for natural language. Use `\( ... \)` for inline math and `\[ ... \]` for block equations. NEVER use `\text{}`, `\begin{aligned}`, `\begin{array}`. Use `<b>` instead of `**`.
6. CLOZE HARD LIMIT: A merged card must NEVER contain more than 3 cloze deletions. Use standard Anki syntax: `{{c1::...}}`. Add spaces for math braces (e.g. `{{c1:: \frac{1}{2} }}`).
7. ABSOLUTELY NO MULTIPLE CHOICE QUESTIONS.
8. IMAGE PLACEMENT: Place images outside math expressions using `<br>`.

OUTPUT STRICTLY JSON in this format:
{
    "reasoning": "Explain your decision...",
    "final_cards": [
        {
            "id": <INTEGER: MUST be the ID of the master card, or the original ID of the card if kept separate>,
            "type": "<Select from inputs>",
            "subdeck": "<Select from inputs>",
            "front": "...",
            "back": "...",
            "tags": "..."
        }
    ]
}
"""

    original_len = len(cards)
    fusion_lock = threading.Lock()
    
    def process_fusion_group(group):
        nonlocal completed_groups
        if not group or len(group) <= 1:
            return
            
        group_cards = [{"id": i, "front": cards[i].get("front", ""), "back": cards[i].get("back", ""), "type": cards[i].get("type", ""), "subdeck": cards[i].get("subdeck", ""), "tags": cards[i].get("tags", "")} for i in group if i < len(cards)]
        master_id = group[0]
        
        image_ctx = ""
        if image_descriptions:
            image_ctx = "\n\n[IMAGE INDEX AND THEIR DESCRIPTIONS]\n" + "\n".join([f"- {k}: {v}" for k, v in image_descriptions.items() if v])
        
        group_json = json.dumps(group_cards, ensure_ascii=False)
        
        print(f"\n      ────────────────────────────────────────")
        print(f"      [FUSION] Groupe Master ID: {master_id} ({len(group)} cartes)")
        
        for attempt in range(retries):
            try:
                response = client.chat.complete(
                    model=model,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": prompt_fuse},
                        {"role": "user", "content": f"Cards to merge:{image_ctx}\n\n{group_json}"}
                    ],
                    max_tokens=32000
                )
                content = response.choices[0].message.content
                
                DEBUG_SUPERVISOR = os.environ.get("ANKI_DEBUG_SUPERVISOR", "0") == "1"
                if DEBUG_SUPERVISOR:
                    with open(f"last_supervisor_fusion_group_{master_id}.txt", "w", encoding="utf-8") as f:
                        f.write(content)

                data = parse_and_repair_json(client, content, model=model)
                final_cards = data.get("final_cards", [])
                reasoning = data.get("reasoning", "Non spécifié")
                
                if final_cards:
                    for fc in final_cards:
                        t_val = fc.get("tags", "")
                        if isinstance(t_val, list):
                            fc["tags"] = " ".join(str(t) for t in t_val)
                        elif not isinstance(t_val, str):
                            fc["tags"] = str(t_val)
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
                                if master_id not in all_deleted_ids:
                                    cards[master_id] = c
                                else:
                                    cards[master_id] = c
                                    all_deleted_ids.remove(master_id)
                                    kept_ids.append(master_id)
                        
                        deleted_in_group = [gid for gid in group if gid in all_deleted_ids]
                        
                        decision = "FUSION" if len(final_cards) < len(group) else "CONSERVÉES SÉPARÉMENT"
                        print(f"      → Décision: {decision} ({len(group)} → {len(final_cards)} carte(s))")
                        
                        try:
                            with open("pipeline_logs.md", "a", encoding="utf-8") as f:
                                f.write(f"## [FUSION SUPERVISEUR] Groupe Master ID: {master_id}\n\n")
                                f.write(f"**Décision:** {decision} ({len(group)} → {len(final_cards)} carte(s))\n\n")
                                f.write(f"**Rationnel du Combiner:**\n> {reasoning}\n\n")
                                f.write(f"### Résultat Combiner:\n```json\n{json.dumps(final_cards, ensure_ascii=False, indent=2)}\n```\n\n---\n")
                        except Exception as e:
                            print(f"Log Error: {e}")
                        
                    break
                else:
                    print(f"      - Échec de parsing JSON Combiner pour le groupe {master_id} (Tentative {attempt+1})...")
            except Exception as e:
                import time
                print(f"      - Erreur Fusion groupe {master_id} (Tentative {attempt+1}): {e}")
                time.sleep(2)
        with progress_lock:
            completed_groups += 1
            ratio = completed_groups / len(duplicate_groups)
            report_progress(4, f"Fusion des doublons : groupe {completed_groups}/{len(duplicate_groups)}", ratio)
        print(f"      ────────────────────────────────────────")
        
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(process_fusion_group, duplicate_groups))
        
    report_progress(4, "Fusion et déduplication terminées.", 1.0)
                
    deduplicated_cards = [c for i, c in enumerate(cards) if i not in all_deleted_ids and i < original_len]
    for i in range(original_len, len(cards)):
        if i not in all_deleted_ids:
            deduplicated_cards.append(cards[i])
    
    try:
        with open("pipeline_logs.md", "a", encoding="utf-8") as f:
            f.write("## [RÉSULTAT DU PROCESSUS DE FUSION / DÉDUPLICATION]\n\n")
            f.write(f"**Nombre de cartes après déduplication:** {len(deduplicated_cards)}\n\n---\n")
    except: pass

    return deduplicated_cards


def add_card_to_decks(deck_definitions, deck_theoremes, deck_vocabulaire, deck_synthese, deck_exercices, card, sequence=""):
    card_type = card.get("type", "Basique").strip()
    subdeck_choice = card.get("subdeck", "01_Définitions").strip()
    mapped_tag = "Catégorie::" + subdeck_choice.replace(" ", "_").replace(",", "")
    
    import re
    
    def fix_asymmetric_mathjax(text):
        text = re.sub(r'\\\((.*?)\\\]', r'\\[\1\\]', text, flags=re.DOTALL)
        text = re.sub(r'\\\[(.*?)\\\)', r'\\[\1\\]', text, flags=re.DOTALL)
        return text

    raw_front = card.get("front", "").strip()
    raw_back = card.get("back", "").strip()
    
    # Appliquer le pipeline de traitement du texte dans l'ordre exact demandé avant l'exportation
    raw_front = fix_mismatched_math_delimiters(raw_front)
    raw_front = remove_code_tags_around_mathjax(raw_front)
    raw_front = clean_mathjax_environments(raw_front)
    raw_front = restore_html_tags(raw_front)
    raw_front = fix_inline_block_math(raw_front)
    raw_front = normalize_image_references(raw_front)
    raw_front = clean_for_anki_tsv(raw_front)
    
    raw_back = fix_mismatched_math_delimiters(raw_back)
    raw_back = remove_code_tags_around_mathjax(raw_back)
    raw_back = clean_mathjax_environments(raw_back)
    raw_back = restore_html_tags(raw_back)
    raw_back = fix_inline_block_math(raw_back)
    raw_back = normalize_image_references(raw_back)
    raw_back = clean_for_anki_tsv(raw_back)
    
    tags_val = card.get("tags", "")
    if isinstance(tags_val, list):
        tags_str = " ".join(str(t) for t in tags_val)
    else:
        tags_str = str(tags_val)
    tags_str = tags_str.strip()
    is_cloze = "trous" in card_type.lower() or "{{c" in raw_front or "{{c" in raw_back
    
    a_refaire_keywords = ["théorème", "theorem", "proposition", "corollaire", "propriété", "lemme", "demonstration", "démonstration"]
    exercice_keywords = ["exemple", "exercice"]

    if "Bridge" in tags_str or "Elaborative_Interrogation" in tags_str or subdeck_choice == "04_Synthèse_et_Relations":
        deck = deck_synthese
    elif subdeck_choice == "05_Exercices_et_Exemples":
        deck = deck_exercices
    elif is_cloze or subdeck_choice == "03_Vocabulaire_et_Constantes":
        deck = deck_vocabulaire
    elif subdeck_choice == "02_Théorèmes_et_Preuves":
        deck = deck_theoremes
    else:
        if any(kw in raw_front.lower() for kw in exercice_keywords):
            deck = deck_exercices
        elif any(kw in raw_front.lower() for kw in a_refaire_keywords):
            deck = deck_theoremes
        else:
            deck = deck_definitions
    
    def escape_math_chevrons(html_text):
        # Sépare le texte par blocs mathématiques. Les blocs se retrouvent aux indices impairs.
        parts = re.split(r'(\\\[.*?\\\]|\\\(.*?\\\))', html_text, flags=re.DOTALL)
        for i in range(1, len(parts), 2):
            # On échappe < et > UNIQUEMENT à l'intérieur des blocs mathématiques
            parts[i] = parts[i].replace('<', '\\lt ').replace('>', '\\gt ')
        return "".join(parts)

    def clean_nested_mathjax(text):
        def replacer(match):
            inner = match.group(1).replace('\\(', '(').replace('\\)', ')')
            return f"\\[{inner}\\]"
        return re.sub(r'\\\[(.*?)\\\]', replacer, text, flags=re.DOTALL)

    def clean_leaked_tags(text):
        # Supprime les lignes du type "Tags: Catégorie::Par_Cœur" ou les tags isolés
        text = re.sub(r'(?i)(?:<br>\s*)*Tags?\s*[:\-].*', '', text)
        text = re.sub(r'Catégorie::\w+', '', text)
        return text.strip()

    raw_front = escape_math_chevrons(raw_front)
    raw_back = escape_math_chevrons(raw_back)

    raw_front = clean_nested_mathjax(raw_front)
    raw_back = clean_nested_mathjax(raw_back)

    raw_front = clean_leaked_tags(raw_front)
    raw_back = clean_leaked_tags(raw_back)

    # Normalisation et extraction des images
    raw_front = normalize_image_references(raw_front)
    raw_front = extract_images_from_math(raw_front)
    raw_back = normalize_image_references(raw_back)
    raw_back = extract_images_from_math(raw_back)

    # Correction 6 : Nettoyage des doubles antislashs (Sur-échappement JSON)
    def clean_double_backslashes(text):
        # Remplace \\pi par \pi, \\( par \( etc., mais préserve les \\ de fin de ligne (matrices)
        return re.sub(r'\\\\(?=[a-zA-Z()\[\]])', r'\\', text)

    raw_front = clean_double_backslashes(raw_front)
    raw_back = clean_double_backslashes(raw_back)

    # Correction 7 : Auto-encapsulation des mathématiques orphelines (Auto-Wrap)
    def auto_wrap_math(text):
        text = re.sub(r'\$\$(.*?)\$\$', r'\\[\1\\]', text, flags=re.DOTALL)
        text = re.sub(r'(?<!\\)\$(.*?)\$', r'\\(\1\\)', text)
        
        parts = re.split(r'(\\\[.*?\\\]|\\\(.*?\\\)|<[^>]+>)', text, flags=re.DOTALL)
        
        # Concaténation classique (évite les bugs d'f-string) et \x5c pour le backslash
        nested_braces = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        pattern = r'([a-zA-Z0-9\x5c]+(?:\^' + nested_braces + r'|_' + nested_braces + r'))'
        
        for i in range(0, len(parts), 2):
            if not parts[i].strip():
                continue
            
            def replacer(match):
                return f" \\({match.group(1)}\\) "
            
            parts[i] = re.sub(pattern, replacer, parts[i])
            
        return "".join(parts)

    raw_front = auto_wrap_math(raw_front)
    raw_back = auto_wrap_math(raw_back)

    # Correction supplémentaire : Auto-encapsulation des commandes LaTeX orphelines (ex: \frac, \tilde, \hat, \pi, \sin)
    def auto_wrap_latex_commands(text):
        # Pattern pour faire correspondre une commande LaTeX et ses accolades/paramètres associés
        latex_term_pattern = r'\\[a-zA-Z]+(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}|\[[^\]]*\]|\([^)]*\)|_\{[^{}]*\}|_[a-zA-Z0-9]+|\^\{[^{}]*\}|\^[a-zA-Z0-9]+|[a-zA-Z0-9])*'
        parts = re.split(r'(\\\[.*?\\\]|\\\(.*?\\\)|<[^>]+>)', text, flags=re.DOTALL)
        for i in range(0, len(parts), 2):
            if not parts[i].strip():
                continue
            parts[i] = re.sub(latex_term_pattern, lambda m: f"\\({m.group(0)}\\)", parts[i])
        return "".join(parts)

    raw_front = auto_wrap_latex_commands(raw_front)
    raw_back = auto_wrap_latex_commands(raw_back)

    # Transformation des balises d'images Markdown en balises HTML
    robust_img_pattern = r'\\*!?\\*\[([^\]]*?)\\*\]\\*\(([^)]+?\.(?:jpeg|jpg|png|gif|webp|svg))\\*\)'
    front_html = re.sub(robust_img_pattern, r'<img src="\2">', raw_front, flags=re.IGNORECASE)
    back_html = re.sub(robust_img_pattern, r'<img src="\2">', raw_back, flags=re.IGNORECASE)
    
    # Remplacement du gras Markdown par HTML
    front_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', front_html, flags=re.DOTALL)
    back_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', back_html, flags=re.DOTALL)
    
    # Correction de l'erreur Anki avec les triples accolades }}} à la fin des clozes mathématiques
    front_html = front_html.replace('}}}', '} }}')
    back_html = back_html.replace('}}}', '} }}')
    
    front_html = front_html.replace('""', '"')
    back_html = back_html.replace('""', '"')

    # Sanity checks and structural repairs for HTML tags and cloze brackets
    front_html = sanitize_html_tags(front_html)
    back_html = sanitize_html_tags(back_html)
    
    front_html = space_mathjax_double_braces(front_html)
    back_html = space_mathjax_double_braces(back_html)

    tags = [t for t in tags_str.replace(",", " ").split(" ") if t]
    if mapped_tag not in tags:
        tags.append(mapped_tag)

    if is_cloze:
        # Si l'IA a inversé le front et le back (le cloze est dans le back), on les échange
        if "{{c" in back_html and "{{c" not in front_html:
            front_html, back_html = back_html, front_html
            
        # Pour les clozes (Texte à trous), on utilise le modèle Cloze d'Anki.
        # Le Front de la réponse JSON devient le champ 'Text', le Back devient 'Back Extra'.
        my_note = genanki.Note(model=model_cloze, fields=[front_html, back_html, sequence], tags=tags)
        deck.add_note(my_note)
    else:
        is_generalite = "Généralités" in card_type or "G\u00e9n\u00e9ralit\u00e9s" in card_type
        if is_generalite:
            my_note = genanki.Note(model=model_generalites, fields=[front_html, back_html, sequence], tags=tags)
        else:
            my_note = genanki.Note(model=model_basic, fields=[front_html, back_html, sequence], tags=tags)
        deck.add_note(my_note)

def process_course(g_file, learning_depth="Zero Lecture"):
    print("\n" + "="*50)
    print("GÉNÉRATEUR DE CARTES ANKI V1.3 — FAST & ROBUST DESIGN (HTML/MathJax + Clozes Natifs)")
    print(f"Profondeur d'apprentissage : {learning_depth}")
    print("="*50 + "\n")
    
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("ERREUR CRITIQUE: La variable d'environnement MISTRAL_API_KEY est introuvable.")
        print("Vérifiez votre fichier .env")
        return None

    if not g_file:
        print("Opération annulée : Aucun fichier selectionné.")
        return None
    
    print("\n" + "="*50)
    print("--- ANKI CARD GENERATOR FAST & ROBUST V1.3 ---")
    print("Optimization: Double-check Embeddings & High Parallelism enabled")
    print("="*50 + "\n")
        
    client = Mistral(api_key=api_key)
    filename = os.path.basename(g_file)
    filename_without_ext = os.path.splitext(filename)[0]

    import datetime
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    run_folder_name = f"{filename_without_ext}_{timestamp_str}"
    
    # Master global folder
    user_home = os.path.expanduser("~")
    master_folder = os.path.join(user_home, "Anki_Generated_Decks")
    
    abs_run_folder = os.path.abspath(os.path.join(master_folder, run_folder_name))
    
    try:
        os.makedirs(abs_run_folder, exist_ok=True)
        set_current_run_folder(abs_run_folder)
        print(f"--> Dossier de travail : {abs_run_folder}")
        print(f"--> Environnement isolé : tous les fichiers (logs, images, deck) seront dans `{abs_run_folder}`\n")
    except Exception as e:
        print(f"Erreur de création de dossier isolé : {e}")
        return None

    try:
        report_progress(1, "Téléchargement du PDF pour OCR...", 0.1)
        print(f"1) Téléchargement de {filename} pour OCR Mistral...")
        with open(g_file, "rb") as f:
            uploaded_pdf = client.files.upload(
                file={
                    "file_name": filename,
                    "content": f,
                },
                purpose="ocr"
            )

        report_progress(1, "Traitement OCR en cours... (Mistral OCR)", 0.3)
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

        report_progress(1, "Extraction et annotation des images...", 0.6)
        import base64
        full_markdown = ""
        media_files = []
        image_descriptions = {} 
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
                    media_files.append(get_abs_path(img_filename))
                    
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
                    
                    page_md = page_md.replace(f"({img.id})", f"({img_filename})")
            full_markdown += page_md + "\n\n"
            
        with open("extracted_course_text.md", "w", encoding="utf-8") as f:
            f.write(full_markdown)
        
        md_lines = full_markdown.split("\n")
        for img_name in list(image_descriptions.keys()):
            img_ref_pattern = f"![{img_name}]({img_name})"
            img_ref_pattern_noalt = f"![]({img_name})"
            found_line_idx = -1
            for li, line in enumerate(md_lines):
                if img_ref_pattern in line or img_ref_pattern_noalt in line:
                    found_line_idx = li
                    break
            if found_line_idx >= 0:
                caption_parts = []
                for offset in range(1, 4):
                    next_idx = found_line_idx + offset
                    if next_idx >= len(md_lines):
                        break
                    next_line = md_lines[next_idx].strip()
                    if next_line.startswith('![') or next_line.startswith('#') or not next_line:
                        break
                    if len(next_line) > 3:
                        caption_parts.append(next_line)
                if caption_parts:
                    caption_text = " — ".join(caption_parts)
                    existing = image_descriptions[img_name]
                    image_descriptions[img_name] = f"{existing} | Caption: {caption_text}" if existing else f"Caption: {caption_text}"
                    print(f"   [IMAGE] {img_name}: légende enrichie avec '{caption_text[:60]}...'")
        
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
        
        report_progress(1, "Découpage intelligent en blocs sémantiques...", 0.8)
        print("4) Découpage intelligent du cours en blocs sémantiques (Agent Splitter)...")
        if len(full_markdown) < 2000:
            print("   => Cours très court (< 2000 caractères), on ignore le découpage sémantique.")
            chunks = [full_markdown]
        else:
            raw_chunks = semantic_split_with_ai(client, full_markdown, learning_depth)
            chunks = []
            current_chunk = ""
            for rc in raw_chunks:
                if current_chunk:
                    current_chunk += "\n\n" + rc
                else:
                    current_chunk = rc
                
                if len(current_chunk) >= 200:
                    chunks.append(current_chunk)
                    current_chunk = ""
            
            if current_chunk:
                if chunks:
                    chunks[-1] += "\n\n" + current_chunk
                else:
                    chunks.append(current_chunk)
        print(f"   => Cours découpé en {len(chunks)} blocs parfaits.")
        report_progress(1, "Découpage terminé.", 1.0)

        all_cards = []
        completed_chunks = 0
        progress_lock = threading.Lock()
        report_progress(2, f"Création des cartes : bloc 0/{len(chunks)}", 0.0)
        
        print("\n5) Analyse AI et génération JSON des cartes en cours (Mistral Large) :")
        
        def process_single_chunk(idx, chunk):
            nonlocal completed_chunks
            if not chunk.strip():
                with progress_lock:
                    completed_chunks += 1
                    ratio = completed_chunks / len(chunks)
                    report_progress(2, f"Création : bloc {completed_chunks}/{len(chunks)}", ratio)
                return idx, []
            print(f"   -> Traitement du bloc {idx+1}/{len(chunks)} (taille: {len(chunk)} chars)...")
            cards = extract_cards_from_chunk(client, chunk, learning_depth, filename_tag=filename_without_ext)
            if cards is None:
                with progress_lock:
                    completed_chunks += 1
                    ratio = completed_chunks / len(chunks)
                    report_progress(2, f"Création : bloc {completed_chunks}/{len(chunks)}", ratio)
                return idx, None
            cards = ai_quality_control_cards(client, cards, learning_depth, chunk_text=chunk, image_descriptions=image_descriptions)
            cards = filter_image_only_cards(cards)
            cards = filter_mcq_cards(cards)
            cards = filter_truncated_cards(client, cards, chunk_text=chunk)
            cards = filter_cloze_overload(cards)
            cards = audit_image_coverage(cards, chunk, image_descriptions=image_descriptions)
            cards = audit_elaboration_quota(cards)
            
            with progress_lock:
                completed_chunks += 1
                ratio = completed_chunks / len(chunks)
                report_progress(2, f"Création : bloc {completed_chunks}/{len(chunks)}", ratio)
                
            return idx, cards

        chunk_results = []
        failed_chunks = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            future_to_idx = {executor.submit(process_single_chunk, i, chunk): i for i, chunk in enumerate(chunks)}
            for future in as_completed(future_to_idx):
                idx, cards = future.result()
                if cards is None:
                    failed_chunks.append((idx, chunks[idx]))
                else:
                    chunk_results.append((idx, cards))
                
        if failed_chunks:
            print(f"\n   [RATTRAPAGE] {len(failed_chunks)} bloc(s) n'ont pas pu être traités. Tentative de rattrapage finale...")
            
            def retry_single_chunk(idx, chunk):
                nonlocal completed_chunks
                print(f"      -> Rattrapage du bloc {idx+1}...")
                cards = extract_cards_from_chunk(client, chunk, learning_depth, filename_tag=filename_without_ext)
                if cards is None:
                    print(f"      -> Échec définitif pour le bloc {idx+1}")
                    with progress_lock:
                        completed_chunks += 1
                        ratio = completed_chunks / len(chunks)
                        report_progress(2, f"Création : bloc {completed_chunks}/{len(chunks)}", ratio)
                    return idx, []
                cards = ai_quality_control_cards(client, cards, learning_depth, chunk_text=chunk, image_descriptions=image_descriptions)
                cards = filter_image_only_cards(cards)
                cards = filter_mcq_cards(cards)
                cards = filter_truncated_cards(client, cards, chunk_text=chunk)
                cards = filter_cloze_overload(cards)
                cards = audit_image_coverage(cards, chunk, image_descriptions=image_descriptions)
                cards = audit_elaboration_quota(cards)
                
                with progress_lock:
                    completed_chunks += 1
                    ratio = completed_chunks / len(chunks)
                    report_progress(2, f"Création : bloc {completed_chunks}/{len(chunks)}", ratio)
                    
                return idx, cards
                
            for idx, chunk in failed_chunks:
                idx, cards = retry_single_chunk(idx, chunk)
                chunk_results.append((idx, cards))
            
        chunk_results.sort(key=lambda x: x[0])
        for _, cards in chunk_results:
            if cards:
                all_cards.extend(cards)
            
        report_progress(4, "Audit de couverture sémantique...", 0.92)
        if learning_depth == "Zero Lecture":
            print(f"\n5.5) Audit de couverture V1.1 : vérification des sections sous-représentées...")
            all_cards = coverage_audit_agent(client, all_cards, chunks, full_markdown, filename_tag=filename_without_ext, image_descriptions=image_descriptions)
            report_progress(4, "Génération de cartes-pont...", 0.95)
            print(f"\n5.6) Génération de cartes-pont inter-sections V1.1...")
            bridge_cards = generate_bridge_cards(client, chunks, all_cards, filename_tag=filename_without_ext)
            if bridge_cards:
                all_cards.extend(bridge_cards)
            
        report_progress(4, "Déduplication lexicale globale...", 0.96)
        print(f"\n5.7) Déduplication lexicale globale (Superviseur) : {len(all_cards)} cartes en revue...")
        if learning_depth == "Zero Lecture":
            all_cards = supervisor_deduplicate_cards(client, all_cards, 0.88, image_descriptions=image_descriptions)
        else:
            all_cards = supervisor_deduplicate_cards(client, all_cards, 0.86, image_descriptions=image_descriptions)
        
        report_progress(4, "Compilation finale du deck Anki...", 0.98)
        print(f"\n5.8) Assemblage final V1.1 : {len(all_cards)} cartes finales, compilation du paquet Anki...")
        
        deck_id_1 = random.randrange(1 << 30, 1 << 31)
        deck_id_2 = random.randrange(1 << 30, 1 << 31)
        deck_id_3 = random.randrange(1 << 30, 1 << 31)
        deck_id_4 = random.randrange(1 << 30, 1 << 31)
        deck_id_5 = random.randrange(1 << 30, 1 << 31)
        deck_name = f"{filename_without_ext}"
        
        deck_definitions = genanki.Deck(deck_id_1, f"{deck_name}::01_Définitions")
        deck_theoremes = genanki.Deck(deck_id_2, f"{deck_name}::02_Théorèmes_et_Preuves")
        deck_vocabulaire = genanki.Deck(deck_id_3, f"{deck_name}::03_Vocabulaire_et_Constantes")
        if learning_depth=="Zero Lecture":
            deck_synthese = genanki.Deck(deck_id_4, f"{deck_name}::04_Synthèse_et_Relations")
            deck_exercices = genanki.Deck(deck_id_5, f"{deck_name}::05_Exercices_et_Exemples")
        
        for i, card in enumerate(all_cards):
            add_card_to_decks(deck_definitions, deck_theoremes, deck_vocabulaire, deck_synthese, deck_exercices, card, sequence=f"{i:04d}")
            
        output_filename = f"{filename_without_ext}_Infaillible.apkg"
        if learning_depth=="Zero Lecture":
            my_package = genanki.Package([deck_definitions, deck_theoremes, deck_vocabulaire, deck_synthese, deck_exercices])
        else:
            my_package = genanki.Package([deck_definitions, deck_theoremes, deck_vocabulaire])
        my_package.media_files = [get_abs_path(f) for f in media_files]
        
        abs_output_filename = get_abs_path(output_filename)
        my_package.write_to_file(abs_output_filename)
        
        report_progress(4, "Sauvegarde du paquet Anki réussie !", 1.0)
                
        print(f"\n[SUCCÈS TOTAL] Votre deck Anki est prêt : {output_filename}")
        print("Vous pouvez double-cliquer dessus pour l'importer directement et parfaitement dans Anki !")
        return run_folder_name

    except Exception as e:
        print(f"\n/!\\ UTILITAIRE INTERROMPU PAR UNE ERREUR /!\\ \n{e}")
        raise e
