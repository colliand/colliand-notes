// Loads MapLibre GL JS 6 (ES modules only) and exposes it as the global `maplibregl` the page scripts use.
// Pages load this as <script type="module"> BEFORE their classic scripts, which carry `defer`: module and deferred
// scripts run in document order, so maplibregl is defined by the time common.js and the page script run.
// The worker file is found next to maplibre-gl.mjs (import.meta.url), so no setWorkerUrl is needed.
import * as maplibregl from "./maplibre-gl.mjs";
window.maplibregl = maplibregl;
