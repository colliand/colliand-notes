// deck.gl-raster 0.8.1, AffineTilesetLevel.crsBoundsToTileRange floors the right and bottom edges, so a bound lying
// exactly on a block edge also takes the next column and row. Sentinel-2's red (20 m overview) and SWIR (20 m) share a
// grid, so every red tile fetched a 2 × 2 square of SWIR blocks and used one: the first view of the Baker map downloaded
// 35 SWIR blocks for 13 distinct ones. Treat the range as half-open, with slack for rounding.
// Run before every build (npm run build); fails loudly if the library changed. Worth reporting upstream:
// https://github.com/developmentseed/deck.gl-raster
import { readFileSync, writeFileSync } from "node:fs";

const f = "node_modules/@developmentseed/deck.gl-raster/dist/raster-tileset/affine-tileset-level.js";
const from = `        const maxCol = Math.min(maxColIdx, Math.floor(pixMaxX / tw));
        const minRow = Math.max(0, Math.floor(pixMinY / th));
        const maxRow = Math.min(maxRowIdx, Math.floor(pixMaxY / th));`;
const to = `        const maxCol = Math.min(maxColIdx, Math.ceil(pixMaxX / tw - 1e-6) - 1); // patched: half-open (patch-tile-range.mjs)
        const minRow = Math.max(0, Math.floor(pixMinY / th));
        const maxRow = Math.min(maxRowIdx, Math.ceil(pixMaxY / th - 1e-6) - 1);`;
const src = readFileSync(f, "utf8");
if (src.includes(to)) process.exit(0);
if (!src.includes(from)) throw new Error(`patch-tile-range: pattern not found in ${f}; check the new deck.gl-raster version`);
writeFileSync(f, src.replace(from, to));
console.log("patched", f);
