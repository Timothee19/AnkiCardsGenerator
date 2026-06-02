<h1 align="center">🤖 Anki Robot AI V1.2 (Final Release)</h1>

<p align="center">
  <b>Automatically generate high-quality, cognitively optimized Anki flashcard decks from university-level PDF courses using Mistral AI. Now with a beautiful desktop GUI!</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Windows-Installer_Available-blue" alt="Windows Installer Available"/>
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+"/>
  <img src="https://img.shields.io/badge/Mistral_AI-OCR_%2B_LLM-orange?logo=mistral" alt="Mistral AI"/>
  <img src="https://img.shields.io/badge/React%20%2B%20Vite-GUI-61DAFB?logo=react&logoColor=black" alt="React GUI"/>
  <img src="https://img.shields.io/badge/LaTeX-MathJax-green?logo=latex&logoColor=white" alt="LaTeX MathJax"/>
  <img src="https://img.shields.io/badge/Anki-.apkg_export-blueviolet" alt="Anki .apkg"/>
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="License MIT"/>
</p>

---

## 🎯 What is this?

**Anki Robot AI** is an end-to-end pipeline that transforms any **university-level PDF** (engineering, mathematics, physics, computer science…) into a **ready-to-import Anki deck** (`.apkg`) with perfectly rendered **LaTeX/MathJax** equations.

With the **Final Application update**, the project has evolved from a terminal script to a **full-fledged Desktop Application** featuring a sleek, responsive React/Vite UI. The backend remains our best **Cognitive AI Tutor** (V1.196), based on pedagogical research (Cognitive Load Theory, Spaced Repetition, Mnemonic Medium), designed to allow a student to learn an entire course *exclusively* through flashcards.

---

## 🎓 The "Zero-Reading" Paradigm

The backend engine features a **massive pedagogical overhaul** based on cognitive science, shifting from "mechanical memorization" to "deep conceptual understanding".

- 🧠 **Elaborative Interrogation**: The AI generates "Why" and "How" questions, establishing causal logic instead of just extracting facts.
- 🌉 **Bridge Cards (Cartes de Liaison)**: The AI automatically creates synthesis cards that connect isolated concepts together, building a macroscopic view of the chapter.
- 🏗️ **Contextual Scaffolding (Mnemonic Medium)**: Every standard card now includes a mandatory `Contexte Explicatif` section on the back. It re-explains the intuition, analogies, and the global architecture of the course.
- 🛡️ **Anti-Pattern Matching**: Strict limitations on Cloze Deletions (Texte à trous). Banned for complex theorems and limited to a maximum of 3 blanks per card (reserved for syntax and physical constants).
- 🏷️ **Bloom Taxonomy Tagging**: Cards are automatically tagged according to their cognitive depth (e.g., `Bloom_Comprendre`, `Bloom_Appliquer`), allowing you to filter your study sessions by difficulty.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🖥️ **Modern Desktop UI** | Beautiful React/Vite webview interface with animated robot states and built-in deck library manager |
| 🤖 **Multi-agent AI pipeline** | 5 specialized AI agents (Splitter, Generator, QA, Supervisor, Combiner) |
| 📄 **Mistral OCR** | Native PDF → markdown extraction with image annotation (type, description, key concepts) |
| 🧮 **LaTeX / MathJax rendering** | All math is wrapped in `\( \begin{aligned} … \end{aligned} \)` for pixel-perfect Anki rendering |
| 🃏 **Smart Card Types** | Basic (Q&A with Context), Cloze (Strictly limited), Two-sided (Généralités), Bridge Cards |
| 🔍 **13-rule QA agent** | Catches blind references, missing `\text{}`, broken braces, MCQ format, and more |
| 🛡️ **Advanced JSON Shield** | Custom parser protects LaTeX elements from JSON escape collisions |
| 🔀 **Semantic deduplication** | 2-stage pipeline (Supervisor identifies duplicates → Combiner merges them) |
| 🚀 **Multithreading** | Parallelized API calls (`ThreadPoolExecutor`) drastically reduces generation time |
| 🖼️ **Image injection** | Images extracted by OCR are annotated, enriched with captions, and injected into the best cards |

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    💻 REACT / VITE DESKTOP GUI                       │
└─────────────────────────────┬────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                          PDF INPUT                                   │
└─────────────────────────────┬────────────────────────────────────────┘
                              ▼
                 ┌────────────────────────┐
                 │  1. Mistral OCR        │  mistral-ocr-latest
                 └────────────┬───────────┘
                              ▼
                 ┌────────────────────────┐
                 │  2. Agent Splitter     │  mistral-large
                 └────────────┬───────────┘
                              ▼
               ┌───────────────────────────────┐
               │  3. Agent Generator           │  mistral-large
               │  (Bloom + Bridge + Scaffolding)
               └───────────────┬───────────────┘
                              ▼
               ┌───────────────────────────────┐
               │  4. Agent QA                  │  mistral-small
               └───────────────┬───────────────┘
                              ▼
               ┌───────────────────────────────┐
               │  5. Post-QA Filters & Dedup   │  Pure Python & mistral-large
               └───────────────┬───────────────┘
                              ▼
               ┌───────────────────────────────┐
               │  6. LaTeX Sanitizer + Export  │  genanki
               └───────────────┬───────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    📦 .apkg ANKI DECK                                │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start (Windows)

The easiest way to use Anki Robot AI on Windows is via the standalone installer:

1. Download **`AnkiRobotAI_Setup.exe`** from the latest Release.
2. Run the installer and follow the instructions.
3. Launch **Anki Robot AI** from your Start menu or Desktop!
4. On first launch, enter your **Mistral AI API key** ([get one here](https://console.mistral.ai/)) in the application settings.

*(The application will save your generated decks to `~\Anki_Generated_Decks` on your computer.)*

---

## 🛠️ Build from Source (For Developers)

If you want to run the application from source or develop it further:

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** (for the React UI)
- A **Mistral AI API key**

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/AnkiCardsGenerator.git
cd AnkiCardsGenerator

# 1. Build the React UI
npm install
npm run build

# 2. Install Python dependencies
pip install pywebview mistralai genanki pydantic json_repair

# 3. Run the application
python AnkiRobotApp.py
```

---

## 📋 Version History

| Version | Key Changes |
|---------|-------------|
| V0.95 - V0.99 | Strict structured output, 2-stage deduplication, Mistral OCR integration, MathJax wrapping, Multithreading. |
| V1.0 - V1.19 | Various pipeline fixes, JSON robust repair, HTML tag leak fixes, `json_repair` integration. |
| V1.195 | Massive Cognitive & Pedagogical Overhaul (Elaborative Interrogation, Bridge Cards, Mnemonic Context). |
| **V1.2 (Final)** | **Desktop GUI Release**: Replaced terminal interface with a modern PyWebView + React/Vite interface. Added built-in deck library, animated UI, setup installer, and V1.196 backend stability patches. |

---

## 🤝 Contributing

Contributions are welcome! 

1. **Fork** the repository
2. **Modify** the frontend (`src/`, `index.html`) or the backend (`AnkiGeneratorRobust*.py`)
3. **Build** the frontend (`npm run build`) before testing the python wrapper.
4. **Submit** a pull request with a description of your changes

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with Gemini, Claude, 🧠 and ☕ — Powered by <a href="https://mistral.ai/">Mistral AI</a>
</p>
