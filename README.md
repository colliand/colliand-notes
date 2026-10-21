# colliand-notes

Source of [notes.colliand.com](https://notes.colliand.com): working notes written as MyST notebooks.

Pages read only small published outputs (CSV, GeoJSON, images) from analysis repos such as
[colliand/glacier-change](https://github.com/colliand/glacier-change), pinned to a commit. Builds never fetch
satellite imagery.

```sh
uv sync && npm install
uv run npm run build        # executes the notebooks → _build/html
uv run npm start            # live preview
GLACIER_CHANGE=../glacier-change uv run npm start   # use local glacier-change outputs instead of GitHub
```

## Deploy

Cloudflare Pages project `colliand-notes` (direct upload, not git-connected), custom domain notes.colliand.com
(CNAME to colliand-notes.pages.dev, proxied). Build locally, then upload:

```sh
uv run npm run build
CLOUDFLARE_API_TOKEN=… CLOUDFLARE_ACCOUNT_ID=… WRANGLER_SEND_METRICS=false \
  npx wrangler@4.145.0 pages deploy _build/html --project-name colliand-notes --branch main
```

`maps/` holds standalone pages copied into the build as-is (MyST does not copy their relative files). `maps/hood-3d.html`
uses whatcom.land's MapLibre build and `theme.js` (copied from colliand/whatcom-land) so the colours match.
Its per-glacier card reads `maps/data/hood_glaciers.json`; rebuild that with `uv run python scripts/hood_map_data.py`
(same `GLACIER_CHANGE` override as the notebooks). The page embeds the map in an iframe; `custom.css` makes it taller.
