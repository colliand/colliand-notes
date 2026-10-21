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
