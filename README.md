# 📚 Course Graph and AnkiDeck Generator

This project automatically transforms an academic course PDF file into a structured and aesthetically optimized Anki flashcard deck. The algorithm has been completely reviewed and now relies on a knwoledge graph architecure and still multi-agent pipeline powered by the Mistral API.

## 🚀 Project Status

*   The main script and current entry point of the program is `testMistralDeuxAgentBest.py`.
*   The script currently runs directly in the terminal.
*   **Next step:** Now that the frontend interface is finished, this terminal program is being converted into a real backend program able to communicate with the final web application.

## 🧠 Algorithm Workflow (Pipeline)

The architecture is divided into several sequential steps managed by different specialized scripts (`ocr.py`, `prompts.py`, `testMistralDeuxAgentBest.py`, and `scholarDesign.py`).

*   **1. OCR and Visual Extraction:** The user provides a PDF file. This file is read, base64 encoded, and transcribed into Markdown via the `mistral-ocr-latest` model. Images with high pedagogical value (diagrams, graphs, equations, etc.) are extracted, annotated, and saved locally, while visual "noise" is ignored.
*   **2. Semantic Splitting and Classification:** The Markdown course is split into indivisible semantic chunks via a first AI agent. Then, a classifier agent automatically identifies the main topic of the course (currently "Maths" or "Computer Science"). If the topic is not precisely identified, the terminal will prompt you to manually specify the closest topic for your course.
*   **3. Knowledge Graph Creation:** Two agents analyze the raw course to generate a flat, event-driven conceptual graph in JSON format. A "corrector" agent rigorously checks the completeness of the extraction; if any lines are missing, it retrieves the orphaned text and integrates it into the graph. The tree structure of this conceptual graph is finally saved as a `.png` image.
*   **4. Formatting and Anki Deck Generation:** A third agent (the Anki formatter) converts the graph nodes into concise flashcards (front/back) formatted in Markdown with LaTeX equation support. The final `.apkg` package is generated via the `genanki` library. The card design uses a custom typographic design system called "Fieldnote" (including a night mode), which is developed in the `scholarDesign.py` file.

## 🗂️ Supported Topics and Specializations

Because mathematics is not learned the same way as computer science, specialized agents with dedicated system instructions (defined in `prompts.py`) handle each subject. The labels used to name and organize the decks and sub-decks adapt automatically:

*   **Maths:** Theorems, Properties, Proposition, Corollary, Lemma, Concepts.
*   **Computer Science:** Algorithms, Architecture, Patterns, Definitions, Syntaxes, Concepts.
*   **Upcoming topics:** Physics, Finance, Chemistry.

---

## ⚙️ Installation

### 1. System Dependencies
Before installing the Python packages, ensure you have **Pandoc** installed on your system. It is required by the `pypandoc` library to compile Markdown and LaTeX equations into HTML.

*   *Mac:* `brew install pandoc`
*   *Linux:* `sudo apt-get install pandoc`
*   *Windows:* Download from the [Pandoc website](https://pandoc.org/installing.html) or use `winget install JohnMacFarlane.Pandoc`.

### 2. Python Packages
*(It is highly recommended to run this inside a virtual environment `venv`)*

Install the required Python libraries using `pip`:
```bash
pip install mistralai genanki networkx pypandoc python-dotenv json-repair pydantic markdown
```

### 3. Environment Setup
Create a `.env` file in the root directory of the project and add your Mistral API key:
```env
MISTRAL_API_KEY=your_mistral_api_key_here
```

## 🛠️ Usage

1. **Run the main script:**
   ```bash
   python testMistralDeuxAgentBest.py
   ```

2. **Follow the on-screen instructions:**
   * Provide the path to your PDF file.
   * In the terminal, **enter the name** you want to give to your Anki deck (e.g., `Maths_Linear_Algebra`).
   * The pipeline will start processing. If the AI cannot confidently detect the subject of your course, the terminal will pause and ask you to **manually input the topic** (e.g., type `1` for Maths or `2` for Computer Science).

3. **Retrieve your files:**
   Once the execution is complete, you will find the following files in your directory:
   *   `your_deck_name.apkg`: The final flashcard deck ready to be imported into Anki.
   *   `markdownCourse.md`: The raw OCR transcription.
   *   Various extracted media files (`.jpeg`, `.png`) used inside the flashcards.
   *   `pipeline_log.txt`: A detailed log of the pipeline execution for debugging purposes.
