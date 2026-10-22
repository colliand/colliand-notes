"""Share-preview tags MyST's static build leaves out: run after `myst build --html` (npm run build does).

MyST writes og:title and a relative og:image (a .webp). Link previews (iMessage, Slack, Facebook, Mastodon) need an
absolute image URL and a description, and some do not read webp. For each page this makes og:image absolute and
points it at the .jpg/.png copy MyST also writes, and adds description, og:description, og:url, og:type and
twitter:card from the note's frontmatter. The landing page borrows the newest note's thumbnail.

On a Cloudflare preview build the URLs use the preview's own address (CF_PAGES_URL), so a draft link previews too.
"""
import html
import os
import re
from pathlib import Path

from build_index import ROOT, frontmatter, notes

OUT = ROOT / "_build" / "html"
if os.environ.get("CF_PAGES_BRANCH", "main") != "main" and os.environ.get("CF_PAGES_URL"):
    SITE = os.environ["CF_PAGES_URL"].rstrip("/")
else:
    SITE = os.environ.get("SITE_URL", "https://notes.colliand.com")


def tags(page_html, fm, url):
    def meta(attr, key, value):
        return f'<meta {attr}="{key}" content="{html.escape(str(value), quote=True)}"/>'

    m = re.search(r'<meta property="og:image" content="([^"]+)"/>', page_html)
    image = None
    if m:
        img = m.group(1)
        stem = img.rsplit(".", 1)[0]
        raster = next((f"{stem}.{x}" for x in ("jpg", "jpeg", "png") if (OUT / f"{stem}.{x}".lstrip("/")).exists()), img)
        image = SITE + raster if raster.startswith("/") else raster
        page_html = page_html.replace(m.group(0), "")
        page_html = re.sub(r'<meta name="image" content="[^"]+"/>', "", page_html)
    add = [meta("property", "og:url", url), meta("property", "og:type", "article" if fm.get("date") else "website")]
    if fm.get("description"):
        if 'name="description"' not in page_html:  # MyST writes these on note pages, not on the index
            add.append(meta("name", "description", fm["description"]))
        if 'property="og:description"' not in page_html:
            add.append(meta("property", "og:description", fm["description"]))
    if image:
        add += [meta("property", "og:image", image), meta("name", "twitter:card", "summary_large_image")]
    if fm.get("tags"):
        page_html = re.sub(r'<meta name="keywords" content=""/>', meta("name", "keywords", ", ".join(fm["tags"])),
                           page_html)
    return page_html.replace("</head>", "".join(add) + "</head>", 1), image


if __name__ == "__main__":
    ns = notes()
    newest = None
    for n in sorted(ns, key=lambda n: str(n["date"]), reverse=True):
        f = OUT / Path(n["path"]).stem / "index.html"
        if not f.exists():
            print(f"fix_meta: no page for {n['path']}")
            continue
        s, image = tags(f.read_text(), n, f"{SITE}/{Path(n['path']).stem}")
        f.write_text(s)
        newest = newest or image
    index = OUT / "index.html"
    fm = frontmatter(ROOT / "index.md")
    s, _ = tags(index.read_text(), fm, SITE + "/")
    if newest and 'property="og:image"' not in s:
        s = s.replace("</head>", f'<meta property="og:image" content="{newest}"/>'
                                 '<meta name="twitter:card" content="summary_large_image"/></head>', 1)
    index.write_text(s)
    print(f"fix_meta: {len(ns)} notes + index, site {SITE}")
