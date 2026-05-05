

<h1 align="center">📚 Anki Cards Generator</h1>

<p align="center">
  <b>Automatically generate high-quality Anki flashcard decks from university-level PDF courses using Mistral AI.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Mistral_AI-OCR_%2B_LLM-orange?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0id2hpdGUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjgiLz48L3N2Zz4=" alt="Mistral AI"/>
  <img src="https://img.shields.io/badge/LaTeX-MathJax-green?logo=latex&logoColor=white" alt="LaTeX MathJax"/>
  <img src="https://img.shields.io/badge/Anki-.apkg_export-blueviolet?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0id2hpdGUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjgiLz48L3N2Zz4=" alt="Anki .apkg"/>
  <img src="https://img.shields.io/badge/version-0.97-brightgreen" alt="Version 0.97"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License MIT"/>
</p>

---

## 🎯 What is this?

**Anki Cards Generator** is an end-to-end Python pipeline that transforms any **university-level PDF** (engineering, mathematics, physics, computer science…) into a **ready-to-import Anki deck** (`.apkg`) with perfectly rendered **LaTeX/MathJax** equations.

It leverages a **multi-agent AI pipeline** powered by **Mistral AI** to:

1. **OCR** — Extract text and images from the PDF with `mistral-ocr-latest`
2. **Generate** — Create pedagogically rich flashcards (Basic, Cloze with sibling cards, Two-sided) via `mistral-large`
3. **Quality-control** — Automatically review, fix, and reject faulty cards via a QA agent (`mistral-small`)
4. **Deduplicate** — Identify and merge semantically redundant cards with a 2-stage Supervisor + Combiner pipeline
5. **Export** — Produce a polished `.apkg` file importable directly into Anki

> **One command, one PDF → a complete, study-ready Anki deck.**

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-agent AI pipeline** | 5 specialized AI agents (Splitter, Generator, QA, Supervisor, Combiner) each with strict role-based prompts |
| 📄 **Mistral OCR** | Native PDF → markdown extraction with image annotation (type, description, key concepts) |
| 🧮 **LaTeX / MathJax rendering** | All math is wrapped in `\( \begin{aligned} … \end{aligned} \)` for pixel-perfect Anki rendering |
| 🃏 **3 card types** | Basic (Q&A), Cloze with sibling cards (up to 10 siblings per note), Two-sided (Généralités) |
| 🔍 **13-rule QA agent** | Catches blind references, missing `\text{}`, broken braces, MCQ format, truncated content, and more |
| 🛡️ **LaTeX JSON Shield** | Custom `fix_llm_json_escaping()` protects `\text`, `\frac`, `\nu`, `\rho` from JSON escape collisions |
| 🧹 **Post-QA filters** | Rejects image-only fronts, multiple-choice questions, and truncated/incomplete cards |
| 🔀 **Semantic deduplication** | 2-stage pipeline (Supervisor identifies duplicates by front → Combiner merges with full context) |
| 🖼️ **Image injection** | Images extracted by OCR are annotated, enriched with captions, and injected into the most relevant cards |
| 📊 **Detailed logging** | Full pipeline trace in `pipeline_logs.md` (QA decisions, rewrites, rejections, fusions) |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                          PDF INPUT                                   │
└─────────────────────────────┬────────────────────────────────────────┘
                              ▼
                 ┌────────────────────────┐
                 │  1. Mistral OCR        │  mistral-ocr-latest
                 │  (Text + Images + Ann.)│
                 └────────────┬───────────┘
                              ▼
                 ┌────────────────────────┐
                 │  2. Agent Splitter     │  mistral-large
                 │  (Semantic chunking)   │
                 └────────────┬───────────┘
                              ▼
              ┌───────────────────────────────┐
              │  3. Agent Generator           │  mistral-large
              │  (Flashcard generation)       │  json_schema strict
              │  13 rules + theorem/def/ex    │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  4. Agent QA                  │  mistral-small
              │  (Quality control, 13 rules)  │  json_schema strict
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  5. Post-QA Filters           │  Pure Python
              │  • Image-only rejection       │
              │  • MCQ detection              │
              │  • Truncation detection        │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  6. Deduplication             │  mistral-large
              │  • Supervisor (fronts only)   │
              │  • Combiner (full context)    │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  7. LaTeX Sanitizer + Export   │  genanki
              │  • Brace balancing            │
              │  • Cloze → sibling cards      │
              │  • MathJax wrapping           │
              │  • .apkg packaging            │
              └───────────────┬───────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    📦 .apkg ANKI DECK                                │
│           (2 sub-decks: Definitions + Theorems/Concepts)             │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- A **Mistral AI API key** ([get one here](https://console.mistral.ai/))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AnkiCardsGenerator.git
cd AnkiCardsGenerator

# Install dependencies
pip install mistralai genanki pydantic

# Set up your API key
echo "MISTRAL_API_KEY=your_api_key_here" > .env
```

### Usage

```bash
python AnkiGeneratorRobustV0.97.py
```

A file dialog will appear — select your PDF and let the pipeline run. The output will be saved in a timestamped folder:

```
YourPDF_20260428_215749/
├── extracted_course_text.md    # Full OCR output in markdown
├── image_annotations.json     # Image descriptions (OCR + captions)
├── img-0.jpeg, img-1.jpeg...  # Extracted images
├── pipeline_logs.md           # Detailed pipeline trace
└── YourPDF_Infaillible.apkg   # ✅ Ready-to-import Anki deck
```

Double-click the `.apkg` file to import it into Anki!

---

## 🃏 Card Types & Sub-decks

### Card Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Basique** | Standard front/back Q&A | Theorems, proofs, exercises, examples |
| **Texte à trous** | Cloze deletions with sibling cards | Definitions, key formulas (up to 10 siblings per note) |
| **Généralités** | Two-sided card (reviewable both ways) | Fundamental vocabulary, high-level definitions |

### Sub-decks

Cards are automatically sorted into two sub-decks:

- **Par Cœur (Définitions)** — Definitions, vocabulary, factual knowledge
- **À Refaire (Théorèmes et Concepts)** — Theorems, proofs, examples, exercises

---

## 🛡️ The LaTeX JSON Shield

One of the most critical components of this project is `fix_llm_json_escaping()`. Here's why:

When an LLM generates LaTeX inside a JSON string, commands like `\text` become `\t` + `ext` — because `\t` is a **valid JSON escape sequence** (tab character). The same happens with:

| LaTeX command | JSON collision | Result without fix |
|---------------|---------------|-------------------|
| `\text{}` | `\t` = tab | `TAB` + `ext{}` |
| `\frac{}` | `\f` = form feed | `FF` + `rac{}` |
| `\nu` | `\n` = newline | `NEWLINE` + `u` |
| `\rho` | `\r` = carriage return | `CR` + `ho` |
| `\beta` | `\b` = backspace | `BS` + `eta` |

> **This function is always required**, even with `json_schema` strict mode. Strict mode guarantees JSON *structure* but not string *content*.

---

## 🔍 Quality Assurance Pipeline

The QA system operates at multiple levels:

### AI-Powered QA Agent (13 Rules)

| Rule | Category | Detects |
|------|----------|---------|
| A | Context | Blind figure references (e.g., "See Fig 2.3") |
| B | Autonomy | Non-self-contained cards ("In Example 1…") |
| C | Formatting | Missing `\text{}` blocks around natural language |
| D | Formatting | Unbalanced braces `{` / `}` |
| E | Compatibility | Invalid LaTeX environments (`\begin{itemize}`) and inline math (`$`) |
| F | Pedagogy | Cards without pedagogical value |
| G | Content | Image-only fronts (no textual question) |
| H | Content | "Describe this image" type questions |
| I | Injection | Over-injection of the same image |
| J | Format | Multiple-choice questions (MCQ) |
| K | Formatting | Preservation of alignment markers `& ` |
| L | Completeness | Fronts ending with ":" without promised content |
| M | Completeness | Backs announcing lists without providing them |

### Post-QA Filters (Python)

| Filter | Purpose |
|--------|---------|
| `filter_image_only_cards()` | Rejects cards whose front contains only images |
| `filter_mcq_cards()` | Catches MCQ patterns the QA agent missed |
| `filter_truncated_cards()` | Detects incomplete fronts/backs |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MISTRAL_API_KEY` | ✅ | Your Mistral AI API key |
| `ANKI_DEBUG_SUPERVISOR` | ❌ | Set to `1` to dump raw supervisor responses |

### Models Used

| Pipeline Stage | Model | Response Format |
|---------------|-------|-----------------|
| OCR | `mistral-ocr-latest` | Binary |
| Splitting | `mistral-large-latest` | `json_object` |
| Generation | `mistral-large-latest` | `json_schema` (strict) |
| Quality Control | `mistral-small-latest` | `json_schema` (strict) |
| Deduplication | `mistral-large-latest` | `json_object` |

---

## 📋 Version History

| Version | Key Changes |
|---------|-------------|
| V0.9 | Strict structured output (`json_schema`) for the Generator |
| V0.91 | Structured output for the Supervisor (deduplication) |
| V0.92 | 2-stage deduplication (Supervisor → Combiner) |
| V0.93 | Enhanced logging for QA rejections and fusions |
| V0.935 | Mistral OCR integration with image annotations (`ImageAnnotation`) |
| V0.95 | `LatexSanitizer` overhaul, clozes inside `\text{}`, sibling cards |
| V0.96 | QA upgrade to Mistral Medium, new anti-MCQ rules |
| V0.965 | Cloze parsing fixes, improved `fix_llm_json_escaping` |
| V0.967 | Image injection overhaul, targeted HTML escaping, rule K (alignment), ~50 LaTeX commands |
| **V0.97** | **Restored `fix_llm_json_escaping`** (critical bug fix), truncation filters, rules 13/L/M |

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|------------|
| LLM API | [Mistral AI](https://mistral.ai/) (`mistralai` Python SDK) |
| OCR | Mistral OCR (`mistral-ocr-latest`) |
| Anki export | [`genanki`](https://github.com/kerrickstaley/genanki) |
| Data validation | [`pydantic`](https://docs.pydantic.dev/) |
| Math rendering | MathJax (`\( \begin{aligned} … \end{aligned} \)`) |

---

## 📁 Project Structure

```
AnkiCardsGenerator/
├── AnkiGeneratorRobustV0.97.py   # 🎯 Main script (~1700 lines)
├── .env                           # API key configuration
├── docs/
│   └── banner.png                 # Repository banner
├── COMPTE_RENDU_V097.md           # Detailed technical report (FR)
└── [output folders]/              # Generated per run
    ├── extracted_course_text.md
    ├── image_annotations.json
    ├── img-*.jpeg
    ├── pipeline_logs.md
    └── *_Infaillible.apkg
```

---

## ⚠️ Known Limitations

- **Processing time**: No API call parallelization — a 50+ page PDF may take 30+ minutes
- **Language support**: Post-QA regex filters are optimized for English and French
- **Empty sibling cards**: Malformed clozes can produce empty fronts (not explicitly filtered)
- **Non-deterministic deduplication**: The Supervisor uses `json_object` mode, which may occasionally produce malformed JSON
- **Image coverage**: If the Generator doesn't reference an OCR-extracted image in any card, the image is silently dropped

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Duplicate** the main script before modifying: `cp AnkiGeneratorRobustV0.97.py AnkiGeneratorRobustV0.XX.py`
3. **Test syntax**: `python -c "import py_compile; py_compile.compile('AnkiGeneratorRobustV0.XX.py', doraise=True)"`
4. **Run** on a test PDF and inspect `pipeline_logs.md`
5. **Submit** a pull request with a description of your changes

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with 🧠 and ☕ — Powered by <a href="https://mistral.ai/">Mistral AI</a>
</p>
