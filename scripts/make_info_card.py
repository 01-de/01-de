import json
import os

def load_live_stats():
    """Reads data/contributions.json (written by fetch_contributions.py).
    Falls back to placeholder text if the file isn't there yet."""
    path = "data/contributions.json"
    if not os.path.exists(path):
        return "N/A", "N/A"
    with open(path) as f:
        data = json.load(f)
    stats = data.get("stats", {})
    total = stats.get("total_contributions")
    streak = stats.get("current_streak")
    contribs_str = f"{total:,} this year" if total is not None else "N/A"
    streak_str = f"{streak} days" if streak is not None else "N/A"
    return contribs_str, streak_str

FONT_SIZE = 20
LINE_H = 30
PAD_X = 24
PAD_Y = 28
LABEL_COLOR = "#00ff00"
VALUE_COLOR = "#c9c9c9"
DIM_COLOR = "#4a4a4a"

# --- EDIT THESE (static fields) ---
USER = "01-de@github"
CONTRIBS_VALUE, STREAK_VALUE = load_live_stats()
FIELDS = [
    ("Languages",   "Java, Python, TypeScript, JavaScript"),
    ("Backend",     "Spring Boot, FastAPI, PostgreSQL"),
    ("Frontend",    "React, Vue, TypeScript, HTML, CSS"),
    ("Editor",      "IntelliJ, Vim, VS Code"),
    ("Status",      "Open to collaborate on interesting projects"),
    ("Currently",   "Digital Banking Platform"),
    ("Contribs",    CONTRIBS_VALUE),   # <- live, from data/contributions.json
    ("Streak",      STREAK_VALUE),     # <- live, from data/contributions.json
]
# -------------------

title_line = f"{USER}"
sep_line = "-" * len(title_line)

n_lines = 3 + len(FIELDS)  # title + sep + blank-ish spacing handled by loop
canvas_w = 700
canvas_h = PAD_Y * 2 + LINE_H * (len(FIELDS) + 2)

STAGGER = 0.15
DUR = 0.4

style_rules = []
style_rules.append("""
    @keyframes lineFade {
      from { opacity: 0; transform: translateX(-8px); }
      to   { opacity: 1; transform: translateX(0); }
    }""")
total_lines = len(FIELDS) + 2
for i in range(total_lines):
    delay = round(i * STAGGER, 3)
    style_rules.append(
        f".card-line-{i} {{ opacity: 0; "
        f"animation: lineFade {DUR}s ease-out {delay}s forwards; }}"
    )

svg = []
svg.append('<?xml version="1.0" encoding="UTF-8"?>')
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">')
svg.append('  <style>')
svg.append("    text { font-family: 'Share Tech Mono', 'Courier New', monospace; font-size: %dpx; }" % FONT_SIZE)
svg.append('    ' + '\n    '.join(style_rules))
svg.append('  </style>')
svg.append('  <rect width="100%" height="100%" fill="#000000"/>')
svg.append('  <g>')

def esc(s):
    return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

y = PAD_Y
line_idx = 0

# title
svg.append(f'    <g class="card-line-{line_idx}"><text x="{PAD_X}" y="{y}" fill="{LABEL_COLOR}">{esc(title_line)}</text></g>')
line_idx += 1
y += LINE_H

# separator
svg.append(f'    <g class="card-line-{line_idx}"><text x="{PAD_X}" y="{y}" fill="{DIM_COLOR}">{esc(sep_line)}</text></g>')
line_idx += 1
y += LINE_H

# fields
LABEL_W = 130
for label, value in FIELDS:
    svg.append(f'    <g class="card-line-{line_idx}">')
    svg.append(f'      <text x="{PAD_X}" y="{y}" fill="{LABEL_COLOR}">{esc(label)}</text>')
    svg.append(f'      <text x="{PAD_X + LABEL_W}" y="{y}" fill="{VALUE_COLOR}">{esc(value)}</text>')
    svg.append('    </g>')
    line_idx += 1
    y += LINE_H

svg.append('  </g>')
svg.append('</svg>')

result = '\n'.join(svg)
with open('info-card.svg', 'w') as f:
    f.write(result)
print("canvas:", canvas_w, "x", canvas_h)
print("total anim time:", round(total_lines*STAGGER + DUR, 2), "s")
