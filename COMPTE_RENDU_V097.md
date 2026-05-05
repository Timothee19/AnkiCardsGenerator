# 📋 Compte Rendu — AnkiGeneratorRobust V0.97

> **Document de reprise** pour futurs développeurs IA (Claude Opus, Gemini, etc.)  
> **Fichier principal** : `AnkiGeneratorRobustV0.97.py` (~1700 lignes)  
> **Date** : 28 avril 2026  
> **Dernière version stable** : V0.97

---

## 1. Objectif du Script

Générer automatiquement des **decks Anki** (`.apkg`) à partir d'un **PDF de cours universitaire** (ingénierie, maths, physique) en utilisant l'API **Mistral AI** pour :
1. L'OCR du PDF (extraction texte + images)
2. La génération intelligente de flashcards LaTeX
3. Le contrôle qualité automatisé
4. L'export au format Anki avec rendu MathJax

Le script produit des cartes de 3 types : **Basique**, **Texte à trous** (cloze deletions avec cartes sœurs), et **Généralités** (recto-verso).

---

## 2. Architecture du Pipeline (7 étapes)

```
[1. OCR Mistral] → [2. Annotation images + légendes] → [3. Splitting sémantique]
    → [4. Génération cartes (Mistral Large)] → [5. QA Agent (Mistral Small)]
    → [6. Filtres post-QA (image-only, MCQ, troncature)]
    → [7. Déduplication (Superviseur + Combiner)] → [8. Sanitizer LaTeX + Export .apkg]
```

### Détail de chaque étape :

| Étape | Fonction | Modèle | Format réponse | `fix_llm_json_escaping` |
|-------|----------|--------|----------------|-------------------------|
| OCR | `client.ocr.process()` | `mistral-ocr-latest` | binaire | N/A |
| Splitting | `semantic_split_with_ai()` | `mistral-large` | `json_object` | Conservé (non strict) |
| Génération | `extract_cards_from_chunk()` | `mistral-large` | `json_schema` strict | **OBLIGATOIRE** |
| QA | `ai_quality_control_cards()` | `mistral-small` | `json_schema` strict | **OBLIGATOIRE** |
| Déduplication | `supervisor_deduplicate_cards()` | `mistral-large` | `json_object` | Conservé |
| Sanitizer | `LatexSanitizer` (classe) | N/A | N/A | N/A |
| Export | `add_card_to_decks()` + `genanki` | N/A | N/A | N/A |

---

## 3. Stack Technique

| Composant | Technologie |
|-----------|-------------|
| API LLM | Mistral AI (`mistralai` Python SDK) |
| OCR | Mistral OCR (`mistral-ocr-latest`) |
| Export Anki | `genanki` (génération programmatique de `.apkg`) |
| Validation | `pydantic` (modèle `ImageAnnotation` pour les annotations d'images) |
| Rendu math | MathJax (environnement `\( \begin{aligned} ... \end{aligned} \)`) |
| Clé API | Variable `MISTRAL_API_KEY` dans fichier `.env` |

---

## 4. Composants Clés (Guide de Navigation du Code)

### 4.1 `fix_llm_json_escaping()` (L50-102)
**Fonction critique.** Protège les commandes LaTeX des séquences d'échappement JSON.

**Problème résolu** : Quand un LLM écrit `\text` dans un string JSON, le parser JSON interprète `\t` comme une tabulation (séquence JSON valide), produisant TAB + "ext" au lieu de `\text`. Idem pour `\frac` (`\f` = form feed), `\nu` (`\n` = newline), `\rho` (`\r` = carriage return), `\beta` (`\b` = backspace).

**Mécanisme** : Scan caractère par caractère. Si un `\` est suivi d'une lettre d'échappement JSON valide (`t`, `f`, `n`, `r`, `b`) ET que la suite correspond à un mot-clé LaTeX connu (`ext`, `rac`, `u`, `ho`, `eta`...), le backslash est doublé pour protéger la commande.

> **ATTENTION** : Cette fonction est **TOUJOURS nécessaire**, même avec `json_schema` strict. Le mode strict garantit la structure JSON (objets, tableaux, types) mais PAS le contenu des strings. `\text` est du JSON structurellement valide, c'est juste que le *contenu* est détruit.

### 4.2 `ImageAnnotation` (L41-44)
Modèle Pydantic utilisé pour structurer les annotations d'images extraites par l'OCR Mistral. Champs : `image_type`, `short_description`, `key_concepts`.

### 4.3 `semantic_split_with_ai()` (L245-306)
Agent Splitter qui découpe le texte OCR en blocs sémantiques cohérents. Règle clé : un théorème + sa preuve + ses exemples = UN SEUL bloc indivisible.

### 4.4 `extract_cards_from_chunk()` (L308-457)
Agent Generator principal (Mistral Large). Produit les cartes JSON avec un prompt très détaillé contenant 13 règles :
- Langue identique au source
- Zéro-pronoun / contexte autonome
- Format LaTeX `\text{}` dans `aligned`
- Clozes en double crochets `[[c1::...]]`
- Interdiction MCQ, listes LaTeX, inline math
- **Règle 13** : Anti-troncature (ne jamais annoncer une liste sans la fournir)

### 4.5 `ai_quality_control_cards()` (L458-635)
Agent QA (Mistral Small). Évalue chaque carte selon 13 règles (A-M) :
- A-D : Contexte visuel, références aveugles, `\text{}` manquants, accolades
- E-J : Environnements invalides, injection proactive interdite, cartes inutiles, image-seule, describe-image, MCQ
- **K** : Préservation des marqueurs d'alignement `& `
- **L** : Front incomplet (se terminant par ":" sans contenu)
- **M** : Back incomplet (liste annoncée sans les éléments)

### 4.6 Filtres Post-QA (L637-787)

| Filtre | Fonction | Détecte |
|--------|----------|---------|
| Image-seule | `filter_image_only_cards()` | Fronts sans texte (juste une image) |
| MCQ | `filter_mcq_cards()` | "Which of the following", choix (a)(b)(c), numéraux romains |
| Troncature | `filter_truncated_cards()` | Fronts "For example:" tronqués, backs courts ou terminant par ":" |

### 4.7 `supervisor_deduplicate_cards()` (L789-983)
Pipeline de déduplication en 2 étapes :
1. **Superviseur** : Analyse uniquement les fronts pour identifier les groupes de doublons sémantiques
2. **Combiner** : Reçoit front+back des doublons détectés, décide si fusion ou conservation séparée

### 4.8 `LatexSanitizer` (classe, L985+)
Classe statique avec plusieurs méthodes :

| Méthode | Rôle |
|---------|------|
| `fix_double_backslash_text()` | Corrige `\\text` → `\text` (sur-échappement QA). Supporte ~50 commandes LaTeX |
| `extract_images_from_text_blocks()` | Extrait les `<img>` piégés dans des `\text{}` |
| `fix_spaces()` | Normalise les espaces entre commandes |
| `balance_braces()` | Équilibre les `{` et `}` |
| `wrap_latex()` | Découpe les lignes > 75 chars, ajoute les préfixes `& ` |
| `_robust_cloze_replacer()` | Protège les `}}` des clozes contre les conflits LaTeX |
| `process_aligned_wrapper()` | Encapsule dans `\( \begin{aligned} ... \end{aligned} \)`, nettoie les doubles `\\` |
| `extract_clozes()` | Extrait/masque les clozes pour les cartes sœurs |

### 4.9 `add_card_to_decks()` (L1306+)
Assemble les cartes finales :
- Conversion `[[c1::...]]` → `{{c1::...}}`
- Échappement HTML ciblé (`<` et `>` uniquement, **PAS** `&` qui est utilisé par LaTeX pour l'alignement)
- Conversion markdown images → `<img src="...">`
- Routage vers les bons decks (Par Cœur / À Refaire)
- Génération des cartes sœurs pour les clozes (jusqu'à 10)

### 4.10 `process_course()` (L1480+)
Fonction main : orchestrateur du pipeline complet.

---

## 5. Historique des Versions et Modifications

| Version | Changements majeurs |
|---------|---------------------|
| V0.9 | Structured output strict (json_schema) pour le Generator |
| V0.91 | Structured output pour le Superviseur (déduplication) |
| V0.92 | Déduplication en 2 étapes (Superviseur → Combiner) |
| V0.93 | Logging enrichi des rejets QA et fusions |
| V0.935 | Intégration OCR Mistral avec annotations d'images (`ImageAnnotation`) |
| V0.95 | Refonte `LatexSanitizer`, clozes à l'intérieur de `\text{}`, cartes sœurs |
| V0.96 | Upgrade QA vers Mistral Medium, nouvelles règles anti-MCQ |
| V0.965 | Corrections cloze parsing, `fix_llm_json_escaping` amélioré |
| **V0.967** | Suppression `limit_image_usage`, ajout `filter_mcq_cards`, enrichissement annotations avec légendes, fix `html.escape` → échappement ciblé, fix sauts de ligne parasites, règle K (préservation `&`), extension du pattern LaTeX (~50 commandes) |
| **V0.97** | **Restauration `fix_llm_json_escaping`** (bug `\text` → TAB), ajout `filter_truncated_cards`, règles 13/L/M anti-troncature |

### Erreur notable V0.967 → V0.97
En V0.967, `fix_llm_json_escaping` avait été **retiré à tort** des fonctions `extract_cards_from_chunk` et `ai_quality_control_cards` en pensant que le mode `json_schema` strict rendait la fonction inutile. **C'était faux** : le mode strict garantit la *structure* JSON mais pas le *contenu* des strings. Les séquences `\t`, `\f`, `\n`, `\r`, `\b` sont du JSON valide qui détruit silencieusement les commandes LaTeX.

---

## 6. Bugs Corrigés (Leçons Apprises)

| Bug | Cause | Fix |
|-----|-------|-----|
| `\text` → TAB+"ext" | `\t` = séquence JSON valide | `fix_llm_json_escaping` (toujours actif) |
| `&amp;` dans les cartes | `html.escape()` échappe `&` | Échappement ciblé `<` `>` uniquement |
| `\\\\ \\` (double line break) | `wrap_latex` + `replace("\n", " ")` | Cleanup regex dans `process_aligned_wrapper` |
| `& ` supprimés par QA | Agent QA réécrit sans les marqueurs | Règle K dans le prompt QA |
| Cartes MCQ résiduelles | Le prompt Generator ne suffisait pas | Filtre post-QA `filter_mcq_cards` |
| Front "For example:" tronqué | QA coupe le contenu annoncé | Règles L/M + `filter_truncated_cards` |
| Back incomplet ("4 processes:" sans les lister) | LLM lazy generation | Règle 13 Generator + Règle M QA |
| Images hallucinées par l'OCR | Annotation Mistral OCR incorrecte | Enrichissement avec légendes du texte source |

---

## 7. Bugs Potentiels / Points à Surveiller

> **AVERTISSEMENT** : Ces points n'ont pas été systématiquement testés et pourraient nécessiter des corrections.

1. **Cartes sœurs vides** : Si un cloze est mal formé, `extract_clozes()` peut produire des fronts vides. Le pipeline ne les filtre pas explicitement.

2. **`fix_llm_json_escaping` faux positifs** : La fonction pourrait doubler un backslash à tort si un mot mathématique commence par les mêmes lettres qu'un keyword LaTeX mais n'en est pas un. Le dictionnaire `LATEX_KEYWORDS` est figé et pourrait manquer des commandes futures.

3. **Déduplication non déterministe** : Le Superviseur utilise `json_object` (non strict), donc le JSON peut parfois être malformé. Le parsing a un retry mais pas de fallback robuste.

4. **Performance sur gros PDF** : Pas de parallélisation des appels API. Chaque chunk est traité séquentiellement (Generator → QA → Filtres). Un PDF de 50+ pages peut prendre 30+ minutes.

5. **Encodage Unicode dans les filtres** : Les patterns regex des filtres MCQ et troncature sont pensés pour l'anglais et le français. D'autres langues pourraient passer à travers.

6. **`wrap_latex` et clozes longs** : Le word-splitting de `wrap_latex` pourrait couper un cloze contenant des espaces à un endroit inattendu, bien que des protections existent (bracket depth tracking).

7. **Images non injectées** : Si l'OCR extrait une image mais que le Generator ne la référence dans aucune carte, elle est perdue silencieusement. Le pipeline ne vérifie pas la couverture des images.

---

## 8. Structure des Fichiers de Sortie

Chaque exécution crée un dossier `{NomPDF}_{timestamp}/` contenant :

| Fichier | Description |
|---------|-------------|
| `extracted_course_text.md` | Texte OCR complet en markdown |
| `image_annotations.json` | Annotations d'images (OCR + légendes) |
| `img-*.jpeg` | Images extraites du PDF |
| `pipeline_logs.md` | Log détaillé de chaque étape (QA, fusions, rejets) |
| `{NomPDF}_Infaillible.apkg` | **Deck Anki final** |

---

## 9. Modèles Anki (genanki)

| Modèle | ID | Usage |
|--------|-----|-------|
| `model_basic` | 1593820471 | Cartes Basique (Front/Back) |
| `model_generalites` | 1593820473 | Cartes Généralités (2 sens) |
| `model_cloze_siblings` | 1593820475 | Texte à trous avec cartes sœurs (10 fronts + 1 back) |

Les cartes sont réparties en 2 sub-decks :
- **Par Cœur (Définitions)** : Définitions, vocabulaire, concepts
- **À Refaire (Théorèmes et Concepts)** : Théorèmes, preuves, exemples, exercices

---

## 10. Instructions de Reprise

### Pour continuer le développement :
1. **Fichier de travail** : `AnkiGeneratorRobustV0.97.py`
2. **Dupliquer** avant de modifier : `Copy-Item "AnkiGeneratorRobustV0.97.py" "AnkiGeneratorRobustV0.XX.py"`
3. **Tester la syntaxe** : `python -c "import py_compile; py_compile.compile('AnkiGeneratorRobustV0.XX.py', doraise=True)"`
4. **Exécuter** : `python AnkiGeneratorRobustV0.XX.py` (sélectionner un PDF dans le file dialog)
5. **Analyser** : Les logs détaillés sont dans `pipeline_logs.md` du dossier de sortie
6. **Cartes exportées** : Importable dans Anki via double-clic sur le `.apkg`, exportée en .txt dans leur dossier pour l'analyse

### Variables d'environnement :
```
MISTRAL_API_KEY=sk-xxxxxxxxxxxx
ANKI_DEBUG_SUPERVISOR=1  # (optionnel) dump les réponses brutes du superviseur
```

### Dossier de test recommandé :
`Thermodynamics2_Chapter_10Extract_20260428_144559/` contient les logs les plus récents et peut servir de référence pour comparer avant/après corrections.

### Pipeline de filtrage complet (dans l'ordre d'exécution) :
```
extract_cards_from_chunk → ai_quality_control_cards → filter_image_only_cards 
    → filter_mcq_cards → filter_truncated_cards → [boucle sur tous les chunks]
    → supervisor_deduplicate_cards → add_card_to_decks (LatexSanitizer) → export .apkg
```
