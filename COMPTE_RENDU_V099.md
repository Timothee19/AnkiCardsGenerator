# 📋 Compte Rendu — AnkiGeneratorRobust V0.99

> **Document de reprise** pour futurs développeurs IA (Claude Opus, Gemini, etc.)  
> **Fichier principal** : `AnkiGeneratorRobustV0.99.py` (~1900 lignes)  
> **Date** : 7 mai 2026  
> **Dernière version stable** : V0.99

---

## 1. Objectif de la Mise à Jour V0.99

La version V0.98, bien que robuste et complète sur le plan pédagogique, souffrait d'un goulot d'étranglement majeur : le traitement séquentiel des requêtes API Mistral. Le traitement de gros documents PDF pouvait prendre beaucoup de temps (parfois 30 minutes ou plus). 

L'objectif de la **V0.99** est l'implémentation de la **parallélisation (multi-threading)** pour accélérer drastiquement la génération des cartes et leur déduplication, tout en préservant l'intégrité des données, l'ordre d'insertion des cartes, et les logs.

---

## 2. Modifications Architecturales (Multi-threading)

La V0.99 intègre la librairie standard Python `concurrent.futures` et `threading` pour exécuter plusieurs appels API simultanément.

### 2.1. Thread-Safety globale via contexte manager

Pour éviter des conditions de course (race conditions) lors de l'écriture dans les fichiers de logs (`pipeline_logs.md`) ou lors des affichages sur le terminal :
- Création de `FILE_LOCK = threading.Lock()` et `PRINT_LOCK = threading.Lock()`.
- Surcharge de la fonction `print()` par `safe_print()` qui acquiert le verrou d'affichage.
- Surcharge de la fonction `open()` par `safe_open()`, un gestionnaire de contexte personnalisé qui acquiert le verrou d'écriture si le fichier ciblé est `pipeline_logs.md` en mode "append" (`"a"`). Ceci permet de sécuriser tous les blocs `with open(...)` du code originel sans avoir à en réécrire chaque occurrence.

### 2.2. Parallélisation de la Phase de Génération (Étape 5)

- **Avant :** La boucle `for idx, chunk in enumerate(chunks):` traitait chaque bloc de texte l'un après l'autre.
- **Maintenant :** Un `ThreadPoolExecutor(max_workers=5)` est utilisé. La logique de traitement d'un bloc a été isolée dans la fonction locale `process_single_chunk(idx, chunk)`. 
- **Maintien de l'ordre :** Les requêtes se terminent dans le désordre. Pour conserver l'ordre naturel du cours, `process_single_chunk` retourne un tuple `(idx, cards)`. Une fois toutes les requêtes terminées, la liste des résultats est triée (`chunk_results.sort(key=lambda x: x[0])`) avant d'étendre la liste globale `all_cards`.

### 2.3. Parallélisation du Combiner (Étape 5.5)

- **Le Superviseur (Étape 1)** reste séquentiel car il a besoin de la vision globale de tous les rectos (`fronts`) pour générer les groupes de doublons (`duplicate_groups`).
- **Le Combiner (Étape 2)**, qui évalue si un groupe de cartes doit être fusionné ou non, a été parallélisé.
- La logique de fusion a été isolée dans la fonction `process_fusion_group(group)`.
- **Thread-Safety local :** Lors de l'écriture des modifications dans le tableau global `cards` et le set `all_deleted_ids`, un verrou local `fusion_lock = threading.Lock()` est utilisé pour empêcher les conflits si plusieurs fusions manipulent les structures de données simultanément.

---

## 3. Améliorations du Rendu LaTeX (Post-Processing)

Au cours du développement de la V0.99, des optimisations ciblées ont été apportées au `LatexSanitizer` (via `wrap_latex`) pour corriger certaines hallucinations ou erreurs récurrentes des LLMs :

### 3.1. Extraction Intelligente depuis les Balises `\text{...}`
Les LLMs insèrent parfois par erreur des expressions mathématiques ou de la mise en forme de texte à l'intérieur de balises `\text{}` (qui sont conçues pour du texte brut). 
- Le script utilise désormais une expression régulière robuste qui parcourt le contenu de ces balises et **extrait dynamiquement** :
  - Les commandes grecques et les variables indicées/exposées (ex: `\eta_{th}`, `W_{net}`).
  - Les fractions (`\frac{...}{...}`).
  - Les balises de mise en forme de texte (`\textbf{...}`, `\textit{...}`, `\underline{...}`, `\mathbf{...}`, `\mathit{...}`).
- Ces éléments sont ressortis de la balise (ex: `} \textbf{...} \text{`) pour garantir leur interprétation correcte par MathJax.

### 3.2. Alignement et Longueur des Lignes
- **Nettoyage de l'Alignement** : Les erreurs de génération produisant des doubles espérluettes (`& &q_{in}`) en début de ligne causent des décalages dans l'environnement `aligned`. La V0.99 filtre la ligne pour s'assurer qu'un unique `& ` la préfixe.
- **Longueur maximale stricte** : Suite aux retours de la V0.98, la longueur maximale d'une ligne mathématique a été stricto sensu rétablie à **75 caractères** (`math_max_len = max_len`). Le système intelligent évitant de couper après une intégrale ou avant un différentiel (`dx`) est conservé.

---

## 4. Paramètres à Surveiller

- **Rate Limits de l'API :** Le paramètre `max_workers` est fixé à 5. Si l'API Mistral (notamment l'accès gratuit ou 'pay-as-you-go' de bas niveau) renvoie des erreurs HTTP 429 (Too Many Requests), il faudra réduire ce chiffre à 3, voire 2, ou implémenter une logique de *backoff exponentiel* plus sophistiquée dans les appels API.
- **Désordre des logs :** Bien que l'affichage et l'écriture dans le fichier de logs soient protégés par des verrous pour éviter la corruption de texte, l'ordre d'apparition des logs de chunks individuels sera non linéaire (les blocs plus rapides s'afficheront en premier). C'est le comportement attendu d'un système asynchrone.

---

## 4. Instructions de Reprise

### Pour continuer le développement :
1. **Fichier de travail** : `AnkiGeneratorRobustV0.99.py`
2. L'essentiel du gain de temps ayant été accompli avec la parallélisation, les prochaines optimisations pourraient concerner la gestion fine des timeouts ou la migration vers l'API batch si celle-ci devient disponible et plus adaptée aux longs cours universitaires.
3. Le reste du code (Sanitizer, Règles d'IA) fonctionne exactement comme dans la V0.98.
