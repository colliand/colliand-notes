# notes.colliand.com. `make new T=glaciers/baker-flipbook`, then write; drop `draft: true` to list it.
.PHONY: build start new binder

build:
	uv run npm run build

start:
	uv run npm start

new:
	@test -n "$(T)" || { echo "usage: make new T=<topic>/<slug>"; exit 1; }
	@test ! -e "$(T).md" || { echo "$(T).md exists"; exit 1; }
	@mkdir -p "$(dir $(T))"
	@sed -e "s/^title: TITLE/title: $(notdir $(T))/" -e "s/^date: DATE/date: $$(date +%F)/" templates/note.md > "$(T).md"
	@echo "wrote $(T).md (draft: true, so it builds but is not on the landing page yet)"

# Binder pins: the direct dependencies, at the versions in uv.lock, plus jupytext so .md notes open as notebooks
binder:
	@{ echo "# Binder (mybinder.org) environment for the notes that run code."; \
	  echo "# Versions match uv.lock; regenerate with: make binder"; \
	  uv export --frozen --no-hashes --no-dev --format requirements-txt --no-header --no-annotate \
	    | grep -E '^(pandas|geopandas|matplotlib|pyogrio|pyproj|shapely|numpy|rasterio)=='; \
	  echo "jupytext==1.19.5"; } > binder/requirements.txt
