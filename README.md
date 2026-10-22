# colliand-notes

Source of [notes.colliand.com](https://notes.colliand.com): quick experiments and first results, written as MyST
notebooks. Polished work is shared elsewhere; this is the workbench, and the landing cards and search are how to find
things again.

Pages read only small published outputs (CSV, GeoJSON, images) from analysis repos such as
[colliand/glacier-change](https://github.com/colliand/glacier-change), pinned to a commit. Builds never fetch
satellite imagery.

```sh
uv sync && npm install
uv run npm run build        # executes the notebooks → _build/html
uv run npm start            # live preview
GLACIER_CHANGE=../glacier-change uv run npm start   # use local glacier-change outputs instead of GitHub
make new T=glaciers/baker-flipbook                  # start a note from templates/note.md (draft: true)
```

## Adding a note

A note is `<topic>/<slug>.md`; the folder is the topic. `scripts/build_index.py` (run by every build) writes the
landing cards in `index.md` and the toc in `myst.yml` from each note's frontmatter (`title`, `subtitle`, `date`,
`thumbnail`, `tags`), newest first. Do not edit between the BEGIN/END markers by hand. `draft: true` keeps a note off
the landing cards; preview and local builds list it in the toc under "Drafts" so it has a link, and production
(`main`) leaves it out entirely. Set `description` too: it is the text under link
previews and search results, and `scripts/fix_meta.py` adds the share tags MyST leaves out (absolute `og:image`, etc.).

Notes with code cells get MyST's power button, which runs them in the page on mybinder.org. Binder installs
`binder/requirements.txt` (direct dependencies at the uv.lock versions, plus jupytext) on Python 3.13
(`binder/runtime.txt`). After changing dependencies, run `make binder`.

## Deploy

Same flow as whatcom.land. Cloudflare Pages project `notes-colliand` is connected to this repo and builds it itself
(`pip install uv==0.12.4 && uv sync --frozen && npm ci && uv run npm run build`, output `_build/html`). Push a branch
for a preview at `https://<branch>.notes-colliand.pages.dev`; merging to `main` publishes notes.colliand.com.
The old direct-upload project `colliand-notes` is retired once the domain has moved.

`maps/` holds standalone pages copied into the build as-is (MyST does not copy their relative files). `maps/hood-3d.html`
uses whatcom.land's MapLibre build and `theme.js` (copied from colliand/whatcom-land) so the colours match.
Its per-glacier card reads `maps/data/hood_glaciers.json`; rebuild that with `uv run python scripts/hood_map_data.py`
(same `GLACIER_CHANGE` override as the notebooks). The page embeds the map in an iframe; `custom.css` makes it taller.
