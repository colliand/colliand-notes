"""Landing-page cards (index.md) and the table of contents (myst.yml) from each note's frontmatter.

    uv run python scripts/build_index.py

A note is any `<topic>/<slug>.md` with a `title` and `date`. The folder is the topic ("glaciers" → Glaciers).
Cards show the thumbnail, date, title, subtitle and tags, newest first within each topic; topics are ordered by
their newest note. Notes with `draft: true` are left out of both (they still build, so a preview link works).
Only the text between the BEGIN/END markers is rewritten, in index.md and in myst.yml.
"""
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"_build", "node_modules", "binder", "scripts", "templates", "maps"}


def frontmatter(path):
    m = re.match(r"---\n(.*?)\n---\n", path.read_text(), re.S)
    return yaml.safe_load(m.group(1)) if m else {}


def notes():
    out = []
    for p in sorted(ROOT.glob("*/*.md")):
        if p.parent.name in SKIP or p.parent.name.startswith("."):
            continue
        fm = frontmatter(p)
        if not fm.get("title") or not fm.get("date") or fm.get("draft"):
            continue
        out.append({"path": p.relative_to(ROOT).as_posix(), "topic": p.parent.name, **fm})
    return out


def topics(ns):
    by = {}
    for n in ns:
        by.setdefault(n["topic"], []).append(n)
    for t in by.values():
        t.sort(key=lambda n: str(n["date"]), reverse=True)
    return sorted(by.items(), key=lambda kv: str(kv[1][0]["date"]), reverse=True)


def title(topic):
    return topic.replace("-", " ").capitalize()


def card(n):
    lines = [f":::{{card}} {n['title']}", f":link: {n['path']}", f":header: {n['date']}"]
    if n.get("tags"):
        lines.append(":footer: " + " · ".join(n["tags"]))
    if n.get("thumbnail"):
        lines.append(f"![]({Path(n['topic'], n['thumbnail']).as_posix()})")
    if n.get("subtitle"):
        lines.append(n["subtitle"])
    return "\n".join(lines + [":::"])


def cards(ns):
    parts = []
    for topic, items in topics(ns):
        parts += [f"## {title(topic)}", "", "::::{grid} 1 2 2 3"]
        parts += [card(n) for n in items]
        parts += ["::::", ""]
    return "\n".join(parts).rstrip() + "\n"


def toc(ns):
    lines = ["    - file: index.md"]
    for topic, items in topics(ns):
        lines += [f"    - title: {title(topic)}", "      children:"]
        lines += [f"        - file: {n['path']}" for n in items]
    return "\n".join(lines) + "\n"


def splice(path, begin, end, body):
    s = path.read_text()
    a, b = s.index(begin) + len(begin), s.index(end)
    new = s[:a] + "\n" + body + s[b:]
    if new != s:
        path.write_text(new)
        print(f"updated {path.name}")


if __name__ == "__main__":
    ns = notes()
    splice(ROOT / "index.md", "<!-- BEGIN cards (scripts/build_index.py) -->", "<!-- END cards -->", cards(ns))
    splice(ROOT / "myst.yml", "  # BEGIN toc (scripts/build_index.py)", "  # END toc", toc(ns))
