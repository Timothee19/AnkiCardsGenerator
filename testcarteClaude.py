import random

import genanki

CSS = r"""
:root{
  --bg:#faf6ef;
  --card-bg:#fffbf3;
  --dot:rgba(79,125,92,.22);
  --ink:#2e2a24;
  --ink-soft:#7a7266;
  --accent:#4f7d5c;
  --accent-light:#71a481;
  --accent-dark:#3c6047;
  --accent-soft:rgba(79,125,92,.14);
  --accent2:#c1694f;
  --accent2-light:#d78a6c;
  --accent2-dark:#9f4f39;
  --accent2-soft:rgba(193,105,79,.14);
  --line:#e6ddcf;
  --code-bg:#efe7d8;
  --code-ink:#4a4235;
  --code-dark-bg:#2e2a24;
  --code-dark-bg2:#3c3527;
  --code-dark-ink:#f4ede0;
}

html, body{
  margin:0;
  background-color:var(--bg);
  background-image:radial-gradient(circle, var(--dot) 1.5px, transparent 1.5px);
  background-size:22px 22px;
}

.card{
  font-family:"Source Sans 3","Segoe UI",-apple-system,BlinkMacSystemFont,Arial,sans-serif;
  font-size:20px;
  line-height:1.65;
  color:var(--ink);
  text-align:justify;
  max-width:640px;
  margin:0 auto;
  padding:32px 36px;
  background:linear-gradient(165deg, #ffffff 0%, var(--card-bg) 100%);
  border-radius:22px;
  box-shadow:0 22px 46px rgba(46,42,36,.20), 0 2px 6px rgba(46,42,36,.10), inset 0 1px 0 rgba(255,255,255,.9);
}

/* separateur Question / Reponse : barre droite + bulle en relief */
.divider{
  display:flex;
  align-items:center;
  gap:14px;
  margin:26px 0 22px;
}
.divider::before, .divider::after{
  content:"";
  flex:1;
  height:1px;
  background:var(--line);
}
.divider span{
  font-size:12px;
  font-weight:700;
  letter-spacing:.06em;
  text-transform:uppercase;
  color:var(--accent-dark);
  background:linear-gradient(160deg, #ffffff 0%, var(--accent-soft) 100%);
  padding:4px 12px;
  border-radius:999px;
  box-shadow:0 4px 10px rgba(79,125,92,.28), inset 0 1px 0 rgba(255,255,255,.9), inset 0 -2px 3px rgba(60,96,71,.10);
  white-space:nowrap;
}

/* cloze : relief marque, forme V1 conservee */
.cloze{
  font-weight:600;
  color:var(--accent2-dark);
  background:linear-gradient(160deg, #ffffff 0%, var(--accent2-soft) 100%);
  padding:1px 7px;
  border-radius:5px;
  box-shadow:0 3px 7px rgba(193,105,79,.25), inset 0 1px 0 rgba(255,255,255,.9);
}

/* images */
img{
  max-width:100%;
  height:auto;
  display:block;
  margin:16px auto;
  border-radius:26px 8px 26px 8px;
  box-shadow:0 16px 32px rgba(46,42,36,.22);
}

/* code */
code{
  font-family:"JetBrains Mono","Fira Code",Consolas,monospace;
  font-size:.85em;
  background:linear-gradient(160deg, #ffffff 0%, var(--code-bg) 100%);
  color:var(--code-ink);
  padding:2px 7px;
  border-radius:8px 3px 8px 3px;
  box-shadow:0 2px 5px rgba(46,42,36,.12), inset 0 1px 0 rgba(255,255,255,.8);
}
pre{
  font-family:"JetBrains Mono","Fira Code",Consolas,monospace;
  background:linear-gradient(160deg, var(--code-dark-bg2) 0%, var(--code-dark-bg) 100%);
  color:var(--code-dark-ink);
  padding:16px 18px;
  border-radius:20px 6px 20px 6px;
  overflow-x:auto;
  line-height:1.55;
  font-size:.85em;
  box-shadow:0 16px 34px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.08);
}
pre code{ background:none; padding:0; color:inherit; box-shadow:none; }

/* tableaux */
table{
  border-collapse:separate;
  border-spacing:0;
  width:100%;
  margin:18px 0;
  font-size:.92em;
  border:1px solid var(--line);
  border-radius:16px;
  overflow:hidden;
  box-shadow:0 10px 22px rgba(46,42,36,.14);
}
th, td{ padding:10px 13px; text-align:left; border-bottom:1px solid var(--line); }
tr:last-child td{ border-bottom:none; }
th{ background:linear-gradient(160deg, #ffffff 0%, var(--accent-soft) 100%); color:var(--accent-dark); font-weight:700; box-shadow:inset 0 -1px 0 rgba(46,42,36,.06); }

/* mode nuit (desktop + AnkiDroid) */
.night_mode body, body.night_mode, .nightMode body, body.nightMode{
  background-color:#211d18;
  background-image:radial-gradient(circle, rgba(143,195,158,.22) 1.5px, transparent 1.5px);
  background-size:22px 22px;
}
.night_mode .card, .card.night_mode, .nightMode .card, .card.nightMode{
  --ink:#f0e9db;
  --ink-soft:#bcb2a0;
  --accent:#8fc39e;
  --accent-light:#a8d4b3;
  --accent-dark:#c7e6cd;
  --accent-soft:rgba(143,195,158,.18);
  --accent2:#e08e6f;
  --accent2-light:#eaab90;
  --accent2-dark:#f2c6b3;
  --accent2-soft:rgba(224,142,111,.18);
  --line:#3b352c;
  --code-bg:#332e26;
  --code-ink:#e9dfcb;
  --code-dark-bg:#171410;
  --code-dark-bg2:#211d17;
  --code-dark-ink:#f0e9db;
  background:linear-gradient(165deg, #332e24 0%, #2a251d 100%);
  box-shadow:0 22px 46px rgba(0,0,0,.45), 0 2px 6px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.06);
}
.night_mode .divider span, .nightMode .divider span{ background:linear-gradient(160deg, #3a352c 0%, var(--accent-soft) 100%); box-shadow:0 4px 10px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.10), inset 0 -2px 3px rgba(0,0,0,.25); }
.night_mode .cloze, .nightMode .cloze{ background:linear-gradient(160deg, #3a352c 0%, var(--accent2-soft) 100%); box-shadow:0 3px 7px rgba(0,0,0,.45), inset 0 1px 0 rgba(255,255,255,.10); }
.night_mode code, .nightMode code{ background:linear-gradient(160deg, #3a352c 0%, var(--code-bg) 100%); box-shadow:0 2px 5px rgba(0,0,0,.35), inset 0 1px 0 rgba(255,255,255,.08); }
.night_mode th, .nightMode th{ background:linear-gradient(160deg, #3a352c 0%, var(--accent-soft) 100%); box-shadow:inset 0 -1px 0 rgba(0,0,0,.2); }
"""

MODEL_BASIC_ID = 1875392046
model_basic = genanki.Model(
    MODEL_BASIC_ID,
    "Basique (Claude)",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Sequence"}],
    sort_field_index=2,
    templates=[
        {
            "name": "Card 1",
            "qfmt": '<div class="note">{{Front}}</div>',
            "afmt": '<div class="note">{{Front}}</div>'
            '<div class="divider"><span>Reponse</span></div>'
            '<div class="note answer">{{Back}}</div>',
        },
    ],
    css=CSS,
)

MODEL_GENERALITES_ID = 1875392091
model_generalites = genanki.Model(
    MODEL_GENERALITES_ID,
    "Generalites deux sens (Claude)",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Sequence"}],
    sort_field_index=2,
    templates=[
        {
            "name": "Sens 1",
            "qfmt": '<div class="note">{{Front}}</div>',
            "afmt": '<div class="note">{{Front}}</div>'
            '<div class="divider"><span>Reponse</span></div>'
            '<div class="note answer">{{Back}}</div>',
        },
        {
            "name": "Sens 2",
            "qfmt": '<div class="note">{{Back}}</div>',
            "afmt": '<div class="note">{{Back}}</div>'
            '<div class="divider"><span>Reponse</span></div>'
            '<div class="note answer">{{Front}}</div>',
        },
    ],
    css=CSS,
)

MODEL_CLOZE_ID = 1875392177
model_cloze = genanki.Model(
    MODEL_CLOZE_ID,
    "Cloze (Claude)",
    model_type=genanki.Model.CLOZE,
    fields=[{"name": "Text"}, {"name": "Extra"}, {"name": "Sequence"}],
    sort_field_index=2,
    templates=[
        {
            "name": "Cloze",
            "qfmt": '<div class="note">{{cloze:Text}}</div>',
            "afmt": '<div class="note">{{cloze:Text}}</div>'
            '{{#Extra}}<div class="divider"><span>Info</span></div>'
            '<div class="note answer">{{Extra}}</div>{{/Extra}}',
        },
    ],
    css=CSS,
)

deck = genanki.Deck(2059400111, "Demo - Nouveau design (Sciences)")

note1 = genanki.Note(
    model=model_basic,
    fields=[
        r"Quelle est la definition de la derivee d'une fonction \(f\) en un point \(a\) ?",
        r"\[f'(a) = \lim_{h \to 0} \frac{f(a+h) - f(a)}{h}\]"
        r"<br>C'est la limite du taux d'accroissement quand \(h\) tend vers 0.",
        "1",
    ],
)

note2 = genanki.Note(
    model=model_basic,
    fields=[
        "En Python, quelle est la complexite temporelle moyenne d'une recherche "
        "dans un dictionnaire (<code>dict</code>) ?",
        "<code>O(1)</code> en moyenne, grace au hachage.<br><br>"
        '<pre><code>d = {"a": 1, "b": 2}\nprint(d["a"])  # O(1)</code></pre>',
        "2",
    ],
)

note3 = genanki.Note(
    model=model_basic,
    fields=[
        'Que represente ce graphe ?<br><img src="sinusoide.png">',
        "La fonction \\(y = \\sin(x)\\), une oscillation periodique de periode "
        "\\(2\\pi\\) et d'amplitude 1.",
        "3",
    ],
)

note4 = genanki.Note(
    model=model_generalites,
    fields=[
        "Loi de Newton (2e loi)",
        r"\[\vec{F} = m\,\vec{a}\] La somme des forces appliquees a un corps "
        "est egale au produit de sa masse par son acceleration.",
        "4",
    ],
)

note5 = genanki.Note(
    model=model_cloze,
    fields=[
        "Les trois etats classiques de la matiere sont {{c1::solide}}, "
        "{{c2::liquide}} et {{c3::gazeux}}.",
        "Le passage d'un etat a l'autre (fusion, vaporisation, etc.) "
        "s'appelle un changement d'etat.",
        "5",
    ],
)

for n in (note1, note2, note3, note4, note5):
    deck.add_note(n)

pkg = genanki.Package(deck)
# pkg.media_files = ['sinusoide.png']
pkg.write_to_file("Demo_Nouveau_Design.apkg")
print("apkg cree")
