#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build "Studio" — an original Anki deck UI for students (EdTech).

Design system: "Fieldnote" — a studious, modern identity built around
an indigo/ink palette, a warm off-white paper background, a serif reading
face for content, and a geometric grotesk for structural chrome (tags,
labels). Light and Night modes share the same tokens, remapped.

Run:  python3 build_deck.py
Output: Studio_Deck.apkg (in the current directory)
"""

import os
import random
import urllib.request

import genanki

random.seed(20260905)

# --------------------------------------------------------------------------
# ASSETS — fonts (downloaded once, cached locally) + the sine-wave figure
# --------------------------------------------------------------------------
ASSET_DIR = "studio_assets"
os.makedirs(ASSET_DIR, exist_ok=True)

FONT_SOURCES = {
    "_SpaceGrotesk.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/spacegrotesk/SpaceGrotesk%5Bwght%5D.ttf",
    "_SourceSerif4.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/SourceSerif4%5Bopsz%2Cwght%5D.ttf",
    "_SourceSerif4Italic.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/sourceserif4/SourceSerif4-Italic%5Bopsz%2Cwght%5D.ttf",
    "_JetBrainsMono.ttf": "https://raw.githubusercontent.com/google/fonts/main/ofl/jetbrainsmono/JetBrainsMono%5Bwght%5D.ttf",
}


def ensure_fonts():
    """Download the three brand typefaces the first time the script runs."""
    for filename, url in FONT_SOURCES.items():
        path = os.path.join(ASSET_DIR, filename)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            continue
        print(f"Downloading {filename} ...")
        try:
            urllib.request.urlretrieve(url, path)
        except Exception as exc:
            raise RuntimeError(
                f"Could not download font '{filename}' from {url}. "
                f"Check your internet connection, or place the file manually "
                f"at '{path}'. Original error: {exc}"
            )


def ensure_graph_image():
    """Render the y = sin(x) figure used by note 3, styled to the palette."""
    path = os.path.join(ASSET_DIR, "img-0.png")
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import numpy as np

    space_grotesk = os.path.join(ASSET_DIR, "_SpaceGrotesk.ttf")
    if os.path.exists(space_grotesk):
        fm.fontManager.addfont(space_grotesk)
        plt.rcParams["font.family"] = "Space Grotesk"

    PAPER, INK, PRIMARY, ACCENT, GRID = (
        "#FAF7F1", "#1B2233", "#263A5F", "#B24A2E", "#D9D3C5",
    )

    fig, ax = plt.subplots(figsize=(6.4, 4.0), dpi=200)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    x = np.linspace(-2 * np.pi, 2 * np.pi, 800)
    y = np.sin(x)

    ax.axhline(0, color=GRID, linewidth=1.1, zorder=1)
    ax.axvline(0, color=GRID, linewidth=1.1, zorder=1)
    ax.plot(x, y, color=PRIMARY, linewidth=3.2, zorder=3, solid_capstyle="round")
    ax.axhline(1, color=ACCENT, linewidth=1, linestyle=(0, (4, 3)), alpha=0.8, zorder=2)
    ax.axhline(-1, color=ACCENT, linewidth=1, linestyle=(0, (4, 3)), alpha=0.8, zorder=2)

    ax.set_xticks([-2 * np.pi, -np.pi, 0, np.pi, 2 * np.pi])
    ax.set_xticklabels(["-2π", "-π", "0", "π", "2π"], color=INK, fontsize=13)
    ax.set_yticks([-1, 0, 1])
    ax.set_yticklabels(["-1", "0", "1"], color=INK, fontsize=13)

    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    for spine in ["left", "bottom"]:
        ax.spines[spine].set_color(INK)
        ax.spines[spine].set_linewidth(1.2)

    ax.set_title("y = sin(x)", color=INK, fontsize=17, fontweight="bold", loc="left", pad=14)
    ax.tick_params(colors=INK, length=4)
    ax.set_ylim(-1.4, 1.4)
    ax.margins(x=0.02)

    plt.tight_layout(pad=1.2)
    plt.savefig(path, facecolor=PAPER, bbox_inches="tight")
    plt.close(fig)


ensure_fonts()
ensure_graph_image()


def new_id():
    return random.randrange(1 << 30, 1 << 31)


MODEL_ID_BASIC = new_id()
MODEL_ID_TWOWAY = new_id()
MODEL_ID_CLOZE = new_id()
DECK_ID = new_id()

# --------------------------------------------------------------------------
# DESIGN SYSTEM — semantic tokens (defined once, referenced everywhere)
# --------------------------------------------------------------------------
# Palette — "Fieldnote"
#   Paper    #FDFBF7  warm off-white / beige
#   Ink      #1B2233  near-black navy ink
#   Indigo   #263A5F  primary — studious, serious
#   Rust     #B24A2E  accent — used sparingly, for marks & emphasis
#   Sage     #7C8965  secondary — supporting / correct-state color
#   Gold     #D9A441  tertiary highlight — reserved for future use
#
# Type
#   Space Grotesk  — structural chrome: tags, sequence marks, buttons, code labels
#   Source Serif 4 — reading content: questions, answers, definitions
#   JetBrains Mono — code samples only
#
# Layout
#   Centered content column, generous margins, a hairline rule that only
#   appears once the answer is revealed, and a left "flag" bar (like a
#   highlighter stroke) that marks the answer block. Quiet and unadorned
#   otherwise — the type and color do the work.

CSS = r"""
.card {
  --paper: #FAF7F1;
  --paper-raised: #FDFBF8;
  --ink: #1B2233;
  --ink-soft: #4B5266;
  --hairline: #E6E1D6;

  --primary: #263A5F;
  --primary-ink: #FAF7F1;
  --primary-soft: #DCE2EC;

  --accent: #B24A2E;
  --accent-ink: #FBF1EC;
  --accent-soft: #F1DACF;

  --secondary: #7C8965;
  --secondary-ink: #F2F4EC;

  --gold: #D9A441;

  --shadow-card: 0 1px 0 rgba(27, 34, 51, 0.06), 0 10px 24px rgba(27, 34, 51, 0.08);
  --radius-lg: 20px;
  --radius-sm: 8px;
  --transition-smooth: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);

  --font-display: "Space Grotesk", "Segoe UI", sans-serif;
  --font-body: "Source Serif 4", Georgia, "Times New Roman", serif;
  --font-mono: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;

  font-family: var(--font-body);
  background: var(--paper);
  color: var(--ink);
  font-size: 20px;
  line-height: 1.55;
  -webkit-font-smoothing: antialiased;
  padding: 0;
  margin: 0;
}

@font-face {
  font-family: "Space Grotesk";
  src: url("_SpaceGrotesk.ttf") format("truetype");
  font-weight: 300 700;
}
@font-face {
  font-family: "Source Serif 4";
  src: url("_SourceSerif4.ttf") format("truetype");
  font-weight: 200 900;
}
@font-face {
  font-family: "Source Serif 4";
  src: url("_SourceSerif4Italic.ttf") format("truetype");
  font-weight: 200 900;
  font-style: italic;
}
@font-face {
  font-family: "JetBrains Mono";
  src: url("_JetBrainsMono.ttf") format("truetype");
  font-weight: 100 800;
}

/* ---------- shell ---------- */
.stage {
  max-width: 640px;
  margin: 0 auto;
  padding: 30px 26px 34px;
  position: relative;
  box-sizing: border-box;
}

/* ---------- tag chip (structural: encodes card state, not decoration) --- */
.tag-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 22px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-display);
  font-weight: 600;
  font-size: 12.5px;
  letter-spacing: 0.02em;
  color: var(--primary-ink);
  background: var(--primary);
  padding: 9px 16px;
  border-radius: 999px;
}
.chip.chip--accent { background: var(--accent); color: var(--accent-ink); }
.chip .dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: currentColor; opacity: 0.55;
}

/* ---------- content ---------- */
.content {
  font-family: var(--font-body);
  font-size: 21px;
  color: var(--ink);
}
.content p { margin: 0 0 12px; }
.content p:last-child { margin-bottom: 0; }

.prompt {
  font-size: 23px;
  font-weight: 500;
}

/* ---------- reveal rule + answer flag ---------- */
/* A thin, irregular oval — a stylized flat mark instead of a perfect
   geometric ellipse, in the same rust used for the answer flag and
   cloze pills, so it reads as part of the same system. Flat fill, no
   shadow. */
.divider {
  height: 12px;
  width: 168px;
  margin: 32px auto 26px;
  background: var(--accent);
  border-radius: 72% 28% 61% 39% / 72% 84% 16% 28%;
  transform: rotate(-2deg);
}
.answer-block {
  position: relative;
  padding: 4px 0 4px 20px;
}
.answer-block::before {
  content: "";
  position: absolute;
  left: 0; top: 2px; bottom: 2px;
  width: 4px;
  border-radius: 3px;
  background: var(--accent);
}

/* ---------- images ---------- */
.content img {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 16px auto;
  border-radius: var(--radius-sm);
  box-shadow: var(--shadow-card);
}

/* ---------- code blocks ---------- */
.content code {
  font-family: var(--font-mono);
  font-size: 0.82em;
  background: var(--primary-soft);
  color: var(--primary);
  padding: 0.1em 0.4em;
  border-radius: 5px;
}
.content pre {
  background: var(--ink);
  color: #E7E9DE;
  padding: 16px 18px;
  border-radius: var(--radius-sm);
  overflow-x: auto;
  margin: 14px 0;
  box-shadow: var(--shadow-card);
  text-align: left;
}
.content pre code {
  background: none;
  color: inherit;
  padding: 0;
  font-size: 0.78em;
  line-height: 1.6;
}

/* ---------- cloze ---------- */
.cloze {
  font-weight: 700;
  font-style: normal;
  color: var(--accent-ink);
  background: var(--accent);
  padding: 0.05em 0.5em;
  border-radius: 999px;
  box-decoration-break: clone;
  -webkit-box-decoration-break: clone;
}

/* ---------- extra / notes footer ---------- */
.extra {
  margin-top: 18px;
  font-family: var(--font-display);
  font-size: 14px;
  color: var(--ink-soft);
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.extra .mark {
  flex: none;
  width: 20px; height: 20px;
  border-radius: 6px;
  background: var(--secondary);
  color: var(--secondary-ink);
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
  margin-top: 1px;
}

/* ---------- night mode ---------- */
.night_mode .card,
.nightMode .card,
.card.night_mode,
.card.nightMode {
  --paper: #12151D;
  --paper-raised: #191D28;
  --ink: #E7E6DC;
  --ink-soft: #A6A9B8;
  --hairline: #2B2F3D;

  --primary: #7C97C9;
  --primary-ink: #10141D;
  --primary-soft: #232B3E;

  --accent: #E38B68;
  --accent-ink: #211008;
  --accent-soft: #3A251C;

  --secondary: #A7B48D;
  --secondary-ink: #171B10;

  --gold: #E6BB63;

  --shadow-card: 0 1px 0 rgba(0, 0, 0, 0.3), 0 10px 24px rgba(0, 0, 0, 0.45);
}
.night_mode .content pre,
.nightMode .content pre { background: #0B0D13; }

/* ========================================================================= */
/* --- Equations LaTeX : Responsive, sans rognage, avec scrollbar propre --- */
/* ========================================================================= */
.card mjx-container[display="true"] {
  display: block !important;
  max-width: 100% !important;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.5em 0;
  margin: 14px 0;
  box-sizing: border-box;
}

.card mjx-container:not([display="true"]) {
  display: inline-block !important;
  max-width: 100% !important;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 5px !important;
  margin-bottom: -5px !important;
  padding-top: 2px !important;
  margin-top: -2px !important;
  padding-left: 2px !important;
  padding-right: 2px !important;
  vertical-align: middle !important;
}

.card mjx-container::-webkit-scrollbar,
.card anki-mathjax::-webkit-scrollbar {
  height: 4px !important;
  -webkit-appearance: none;
}
.card mjx-container::-webkit-scrollbar-track,
.card anki-mathjax::-webkit-scrollbar-track {
  background: transparent;
}
.card mjx-container::-webkit-scrollbar-thumb,
.card anki-mathjax::-webkit-scrollbar-thumb {
  background: transparent !important;
  border-radius: 4px;
}
.card mjx-container:hover::-webkit-scrollbar-thumb,
.card anki-mathjax:hover::-webkit-scrollbar-thumb {
  background: #94A3B8 !important;
}

.card anki-mathjax[block="true"] {
  display: block !important;
  max-width: 100% !important;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.5em 0;
  margin: 14px 0;
  box-sizing: border-box;
}
.card anki-mathjax:not([block="true"]) {
  display: inline-block !important;
  max-width: 100% !important;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 5px !important;
  margin-bottom: -5px !important;
  padding-top: 2px !important;
  margin-top: -2px !important;
  padding-left: 2px !important;
  padding-right: 2px !important;
  vertical-align: middle !important;
  box-sizing: border-box;
}
"""

# --------------------------------------------------------------------------
# TEMPLATES
# --------------------------------------------------------------------------

BASIC_FRONT = """
<div class="stage">
  <div class="tag-row">
    <span class="chip"><span class="dot"></span>Question</span>
  </div>
  <div class="content prompt">{{Front}}</div>
</div>
"""

BASIC_BACK = """
<div class="stage">
  <div class="tag-row">
    <span class="chip"><span class="dot"></span>Question</span>
  </div>
  <div class="content prompt">{{Front}}</div>
  <div class="divider"></div>
  <div class="tag-row" style="margin-bottom:14px;">
    <span class="chip chip--accent"><span class="dot"></span>Answer</span>
  </div>
  <div class="content answer-block">{{Back}}</div>
</div>
"""

TWOWAY_CARD1_FRONT = """
<div class="stage">
  <div class="tag-row">
    <span class="chip"><span class="dot"></span>Concept</span>
  </div>
  <div class="content prompt">{{Front}}</div>
</div>
"""

TWOWAY_CARD1_BACK = """
<div class="stage">
  <div class="tag-row">
    <span class="chip"><span class="dot"></span>Concept</span>
  </div>
  <div class="content prompt">{{Front}}</div>
  <div class="divider"></div>
  <div class="tag-row" style="margin-bottom:14px;">
    <span class="chip chip--accent"><span class="dot"></span>Overview</span>
  </div>
  <div class="content answer-block">{{Back}}</div>
</div>
"""

TWOWAY_CARD2_FRONT = """
<div class="stage">
  <div class="tag-row">
    <span class="chip chip--accent"><span class="dot"></span>Overview</span>
  </div>
  <div class="content prompt">{{Back}}</div>
</div>
"""

TWOWAY_CARD2_BACK = """
<div class="stage">
  <div class="tag-row">
    <span class="chip chip--accent"><span class="dot"></span>Overview</span>
  </div>
  <div class="content prompt">{{Back}}</div>
  <div class="divider"></div>
  <div class="tag-row" style="margin-bottom:14px;">
    <span class="chip"><span class="dot"></span>Concept</span>
  </div>
  <div class="content answer-block">{{Front}}</div>
</div>
"""

CLOZE_FRONT = """
<div class="stage">
  <div class="tag-row">
    <span class="chip"><span class="dot"></span>Fill in the blank</span>
  </div>
  <div class="content prompt">{{cloze:Text}}</div>
</div>
"""

CLOZE_BACK = """
<div class="stage">
  <div class="tag-row">
    <span class="chip"><span class="dot"></span>Fill in the blank</span>
  </div>
  <div class="content prompt">{{cloze:Text}}</div>
  {{#Extra}}
  <div class="divider"></div>
  <div class="extra">
    <span class="mark">i</span>
    <div class="content">{{Extra}}</div>
  </div>
  {{/Extra}}
</div>
"""

# --------------------------------------------------------------------------
# MODELS
# --------------------------------------------------------------------------

basic_model = genanki.Model(
    MODEL_ID_BASIC,
    "Studio — Basic",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Sequence"}],
    templates=[
        {
            "name": "Carte 1",
            "qfmt": BASIC_FRONT,
            "afmt": BASIC_BACK,
        }
    ],
    css=CSS,
)

twoway_model = genanki.Model(
    MODEL_ID_TWOWAY,
    "Studio — Two-Way (Overview)",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Sequence"}],
    templates=[
        {
            "name": "Concept → Overview",
            "qfmt": TWOWAY_CARD1_FRONT,
            "afmt": TWOWAY_CARD1_BACK,
        },
        {
            "name": "Overview → Concept",
            "qfmt": TWOWAY_CARD2_FRONT,
            "afmt": TWOWAY_CARD2_BACK,
        },
    ],
    css=CSS,
)

cloze_model = genanki.Model(
    MODEL_ID_CLOZE,
    "Studio — Cloze",
    fields=[{"name": "Text"}, {"name": "Extra"}, {"name": "Sequence"}],
    templates=[
        {
            "name": "Cloze",
            "qfmt": CLOZE_FRONT,
            "afmt": CLOZE_BACK,
        }
    ],
    css=CSS,
    model_type=genanki.Model.CLOZE,
)

# --------------------------------------------------------------------------
# DECK
# --------------------------------------------------------------------------

deck = genanki.Deck(DECK_ID, "Studio — Mathématiques & Fondamentaux")

notes = [
    genanki.Note(
        model=basic_model,
        fields=[
            r"Quelle est la definition de la derivee d'une fonction \(f\) en un point \(a\) ?",
            r"\[f'(a) = \lim_{h \to 0} \frac{f(a+h) - f(a)}{h}\]<br>C'est la limite du taux d'accroissement quand \(h\) tend vers 0.",
            "1",
        ],
        guid=genanki.guid_for("unique_theme_name", "1"),
    ),
    genanki.Note(
        model=basic_model,
        fields=[
            "En Python, quelle est la complexite temporelle moyenne d'une recherche dans un dictionnaire (<code>dict</code>) ?",
            "<code>O(1)</code> en moyenne, grace au hachage.<br><br><pre><code>d = {\"a\": 1, \"b\": 2}\nprint(d[\"a\"])  # O(1)</code></pre>",
            "2",
        ],
        guid=genanki.guid_for("unique_theme_name", "2"),
    ),
    genanki.Note(
        model=basic_model,
        fields=[
            "Que represente ce graphe ?<br><img src=\"img-0.png\">",
            "La fonction \\(y = \\sin(x)\\), une oscillation periodique de periode \\(2\\pi\\) et d'amplitude 1.",
            "3",
        ],
        guid=genanki.guid_for("unique_theme_name", "3"),
    ),
    genanki.Note(
        model=twoway_model,
        fields=[
            "Loi de Newton (2e loi)",
            r"\[\vec{F} = m\,\vec{a}\] La somme des forces appliquees a un corps est egale au produit de sa masse par son acceleration.",
            "4",
        ],
        guid=genanki.guid_for("unique_theme_name", "4"),
    ),
    genanki.Note(
        model=cloze_model,
        fields=[
            "Les trois etats classiques de la matiere sont {{c1::solide}}, {{c2::liquide}} et {{c3::gazeux}}.",
            "Le passage d'un etat a l'autre (fusion, vaporisation, etc.) s'appelle un changement d'etat.",
            "5",
        ],
        guid=genanki.guid_for("unique_theme_name", "5"),
    ),
    genanki.Note(
        model=basic_model,
        fields=[
            "Definir la mesure de comptage \\(\\mu\\) sur \\((X, \\mathcal{P}(X))\\).",
            r"\[\mu(A) = \begin{cases} \text{le nombre d'elements de } A & \text{si } A \text{ est fini,} \\ +\infty & \text{si } A \text{ est infini,} \end{cases} \quad \text{pour tout } A \in \mathcal{P}(X).\]<br>Cette equation est volontairement large pour tester le defilement horizontal.",
            "6",
        ],
        guid=genanki.guid_for("unique_theme_name", "6"),
    ),
    genanki.Note(
        model=basic_model,
        fields=[
            "Cette carte teste une equation INLINE tres longue, integree au milieu d'une phrase.",
            "Le developpement en serie \\(\\pi = 4 \\left( 1 - \\frac{1}{3} + \\frac{1}{5} - \\frac{1}{7} + \\frac{1}{9} - \\frac{1}{11} + \\frac{1}{13} - \\frac{1}{15} + \\frac{1}{17} - \\frac{1}{19} + \\ldots \\right)\\) reste sur sa ligne, sans la casser, meme s'il faut faire defiler juste ce morceau.",
            "7",
        ],
        guid=genanki.guid_for("unique_theme_name", "7"),
    ),
]

for note in notes:
    deck.add_note(note)

# --------------------------------------------------------------------------
# PACKAGE — attach media (fonts + graph image)
# --------------------------------------------------------------------------

package = genanki.Package(deck)
package.media_files = [
    os.path.join(ASSET_DIR, "_SpaceGrotesk.ttf"),
    os.path.join(ASSET_DIR, "_SourceSerif4.ttf"),
    os.path.join(ASSET_DIR, "_SourceSerif4Italic.ttf"),
    os.path.join(ASSET_DIR, "_JetBrainsMono.ttf"),
    os.path.join(ASSET_DIR, "img-0.png"),
]
# Files are named with an underscore prefix so their basenames match the
# @font-face references in CSS exactly, and so they're unlikely to collide
# with other decks' media in the user's collection. genanki stores every
# media file under its basename regardless of source folder.

OUTPUT = "Studio_Deck.apkg"
package.write_to_file(OUTPUT)
print(f"Wrote {OUTPUT}")