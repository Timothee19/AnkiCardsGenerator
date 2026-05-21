<h1 align="center">📚 Anki Cards Generator V1.195</h1>

<p align="center">
  <b>Automatically generate high-quality, cognitively optimized Anki flashcard decks from university-level PDF courses using Mistral AI.</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Mistral_AI-OCR_%2B_LLM-orange?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0id2hpdGUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjgiLz48L3N2Zz4=" alt="Mistral AI"/>
  <img src="https://img.shields.io/badge/LaTeX-MathJax-green?logo=latex&logoColor=white" alt="LaTeX MathJax"/>
  <img src="https://img.shields.io/badge/Anki-.apkg_export-blueviolet?logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTYiIGhlaWdodD0iMTYiIHZpZXdCb3g9IjAgMCAxNiAxNiIgZmlsbD0id2hpdGUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+PGNpcmNsZSBjeD0iOCIgY3k9IjgiIHI9IjgiLz48L3N2Zz4=" alt="Anki .apkg"/>
  <img src="https://img.shields.io/badge/version-1.195-brightgreen" alt="Version 1.195"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License MIT"/>
</p>

---

## 🎯 What is this?

**Anki Cards Generator** is an end-to-end Python pipeline that transforms any **university-level PDF** (engineering, mathematics, physics, computer science…) into a **ready-to-import Anki deck** (`.apkg`) with perfectly rendered **LaTeX/MathJax** equations.

With the **Terminal Version (V1.195)**, the project has evolved from a simple text extractor to a **Cognitive AI Tutor**. Based on advanced pedagogical research (Cognitive Load Theory, Spaced Repetition, Mnemonic Medium), the AI generates cards designed to allow a student to learn an entire course *exclusively* through flashcards, without ever reading the source material.

---

## 🎓 The "Zero-Reading" Paradigm (New in V1.195)

The V1.195 update represents a **massive pedagogical overhaul**. We redesigned the AI prompts based on cognitive science to shift from "mechanical memorization" (rote learning) to "deep conceptual understanding".

- 🧠 **Elaborative Interrogation**: The AI is forced to generate "Why" and "How" questions, establishing causal logic instead of just extracting facts.
- 🌉 **Bridge Cards (Cartes de Liaison)**: The AI automatically creates synthesis cards that connect isolated concepts together, building a macroscopic view of the chapter.
- 🏗️ **Contextual Scaffolding (Mnemonic Medium)**: Every standard (Basique) card now includes a mandatory `Contexte Explicatif` section on the back. It re-explains the intuition, analogies, and the global architecture of the course right when you need it.
- 🛡️ **Anti-Pattern Matching**: Strict limitations on Cloze Deletions (Texte à trous). They are banned for complex theorems and limited to a maximum of 3 blanks per card (reserved for syntax and physical constants). Complex concepts use "Free Recall" (Basique).
- 🏷️ **Bloom Taxonomy Tagging**: Cards are automatically tagged according to their cognitive depth (e.g., `Bloom_Comprendre`, `Bloom_Appliquer`), allowing you to filter your study sessions by difficulty.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-agent AI pipeline** | 5 specialized AI agents (Splitter, Generator, QA, Supervisor, Combiner) each with strict role-based prompts |
| 📄 **Mistral OCR** | Native PDF → markdown extraction with image annotation (type, description, key concepts) |
| 🧮 **LaTeX / MathJax rendering** | All math is wrapped in `\( \begin{aligned} … \end{aligned} \)` for pixel-perfect Anki rendering |
| 🃏 **Smart Card Types** | Basic (Q&A with Context), Cloze (Strictly limited), Two-sided (Généralités), Bridge Cards |
| 🔍 **13-rule QA agent** | Catches blind references, missing `\text{}`, broken braces, MCQ format, truncated content, and more |
| 🛡️ **Advanced JSON Shield** | Custom `fix_llm_json_escaping()` protects `\text`, `\frac`, `\nu`, `\rho` from JSON escape collisions |
| 🧹 **Post-QA filters** | Rejects image-only fronts, multiple-choice questions, and truncated/incomplete cards |
| 🔀 **Semantic deduplication** | 2-stage pipeline (Supervisor identifies duplicates by front → Combiner merges with full context) |
| 🚀 **Multithreading** | Parallelized API calls (`ThreadPoolExecutor`) drastically reduces generation time for large PDFs |
| 🖼️ **Image injection** | Images extracted by OCR are annotated, enriched with captions, and injected into the most relevant cards |

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
              │  Bloom + Bridge + Scaffolding │
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
              │  • Truncation detection       │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  6. Deduplication             │  mistral-large
              │  • Supervisor (fronts only)   │
              │  • Combiner (full context)    │
              └───────────────┬───────────────┘
                              ▼
              ┌───────────────────────────────┐
              │  7. LaTeX Sanitizer + Export  │  genanki
              │  • Brace balancing            │
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
pip install mistralai genanki pydantic json_repair

# Set up your API key
echo "MISTRAL_API_KEY=your_api_key_here" > .env
```

### Usage

```bash
python AnkiGeneratorRobustV1.195.py
```

A file dialog will appear — select your PDF and let the pipeline run. The output will be saved in a timestamped folder:

```
YourPDF_20260521_144200/
├── extracted_course_text.md    # Full OCR output in markdown
├── image_annotations.json     # Image descriptions (OCR + captions)
├── img-0.jpeg, img-1.jpeg...  # Extracted images
├── pipeline_logs.md           # Detailed pipeline trace
└── YourPDF_Infaillible.apkg   # ✅ Ready-to-import Anki deck
```

Double-click the `.apkg` file to import it into Anki!

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MISTRAL_API_KEY` | ✅ | Your Mistral AI API key |
| `ANKI_DEBUG_SUPERVISOR` | ❌ | Set to `1` to dump raw supervisor responses |

---

## 📋 Version History

| Version | Key Changes |
|---------|-------------|
| V0.95 - V0.99 | Strict structured output, 2-stage deduplication, Mistral OCR integration, MathJax wrapping, Multithreading, image coverage audit. |
| V1.0 - V1.19 | Various pipeline fixes, JSON robust repair, HTML tag leak fixes, `json_repair` integration, markdown bold & MathJax delimiters fixes. |
| **V1.195** | **Terminal Release**: Massive Cognitive & Pedagogical Overhaul. Addition of Elaborative Interrogation, Bridge Cards, Mnemonic Context Scaffolding, Cloze restriction, and Bloom Taxonomy tagging. |

---

## 🤝 Contributing

Contributions are welcome! 

1. **Fork** the repository
2. **Duplicate** the main script before modifying: `cp AnkiGeneratorRobustV1.195.py AnkiGeneratorRobustV1.XX.py`
3. **Test syntax**: `python -c "import py_compile; py_compile.compile('AnkiGeneratorRobustV1.XX.py', doraise=True)"`
4. **Submit** a pull request with a description of your changes

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with 🧠 and ☕ — Powered by <a href="https://mistral.ai/">Mistral AI</a>
</p>
