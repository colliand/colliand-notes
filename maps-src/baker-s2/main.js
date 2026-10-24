// Mount Baker bright ice, computed in the browser: Sentinel-2 red / shortwave-infrared (B04 / B11) above a threshold,
// the method whatcom.land uses for its 2025 glacier estimate. Bands stream as Cloud-Optimized GeoTIFFs straight from
// the public Sentinel-2 archive on AWS (Element 84, Collection 1); the ratio and threshold run on the GPU
// (deck.gl-raster), so the slider is instant. Only the two bands the test uses are fetched; the background is the red
// band in grey (blue and green for natural colour would double the download).
import { Deck, MapView } from "@deck.gl/core";
import { GeoJsonLayer } from "@deck.gl/layers";
import { MultiCOGLayer } from "@developmentseed/deck.gl-geotiff";
import { parseWkt } from "@developmentseed/proj";

const SUMMIT = [-121.8144, 48.7768];
// Area of bright ice within 10 km of the summit at threshold 2, measured by whatcom.land on the same dates
// (methods/glacier-outlines.md; Planetary Computer's processing of these scenes). 2021 was not measured for Mount
// Baker alone. 2015 (the baseline): 39.8 km².
const MEASURED = { "2023-09-14": 34.8, "2025-09-23": 34.4 };

const el = (id) => document.getElementById(id);
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));

// GPU step after the bands are composited: r, g, b = red, green, blue and a = SWIR, each a uint16 digital number
// normalized to 0–1 (DN / 65535). Removes the scene's offset, takes red / SWIR, paints bright ice, dims the rest.
const GlacierRatio = {
  name: "glacierRatio",
  fs: `\
uniform glacierRatioUniforms {
  float threshold;
  float offset;
  float showIce;
  vec3 iceColor;
} glacierRatio;
`,
  inject: {
    "fs:DECKGL_FILTER_COLOR": /* glsl */ `
  if (color.r == 0.0 && color.a == 0.0) discard;
  float off = glacierRatio.offset;
  vec3 refl = max(color.rgb - off, 0.0);
  float swir = max(color.a - off, 1.0 / 65535.0);
  float ratio = refl.r / swir;
  vec3 natural = clamp(refl / (5000.0 / 65535.0), 0.0, 1.0);
  natural = pow(natural, vec3(0.8));
  if (glacierRatio.showIce > 0.5 && ratio > glacierRatio.threshold) {
    color = vec4(glacierRatio.iceColor, 1.0);
  } else {
    color = vec4(natural * (glacierRatio.showIce > 0.5 ? 0.72 : 1.0), 1.0);
  }
`,
  },
  uniformTypes: { threshold: "f32", offset: "f32", showIce: "f32", iceColor: "vec3<f32>" },
  getUniforms: (p) => ({
    threshold: p.threshold ?? 2,
    offset: p.offset ?? 0,
    showIce: p.showIce ?? 1,
    iceColor: p.iceColor ?? [0.95, 0.94, 0.97],
  }),
};

// index: the year asked for; shown: the year whose image is on screen. Every year keeps its own layer (and tile cache),
// and the old year stays on top until the new one has drawn, so switching never blanks the map. Once the first year
// has drawn, the others load in the background, so later switches are instant.
const state = { scenes: [], index: 0, shown: null, preload: false, drawn: new Set(), threshold: 2, showIce: true, show2015: true, show2025: false };
let outlines = null;
let utm10 = null;

const deck = new Deck({
  parent: el("map"),
  views: new MapView({ repeat: false }),
  controller: { dragRotate: false, touchRotate: false },
  initialViewState: { longitude: SUMMIT[0], latitude: SUMMIT[1], zoom: window.innerWidth < 640 ? 10.6 : 11.4, minZoom: 9, maxZoom: 15 },
  getCursor: ({ isDragging }) => (isDragging ? "grabbing" : "grab"),
  onError: (e) => showError(e),
});

function showError(e) {
  el("status").textContent = "The images did not load. Reload the page to try again.";
  el("status").hidden = false;
  console.error(e);
}

function sceneLayer(i, iceColor) {
  const s = state.scenes[i];
  // Keep one sources object per scene: a new object makes the layer reopen every file and drop its tiles
  s.sources ??= Object.fromEntries(Object.entries(s.bands).filter(([k]) => k === "red" || k === "swir").map(([k, href]) => [k, { url: href }]));
  return new MultiCOGLayer({
    id: `s2-${s.date}`,
    sources: s.sources,
    composite: { r: "red", g: "red", b: "red", a: "swir" },  // grey from red; SWIR rides in alpha
    epsgResolver: async () => utm10,
    renderPipeline: [{
      module: GlacierRatio,
      props: { threshold: state.threshold, offset: s.offset / 65535, showIce: state.showIce ? 1 : 0, iceColor },
    }],
    onViewportLoad: () => {
      state.drawn.add(i);
      if (i !== state.index) return;
      el("status").hidden = true;
      if (state.shown !== i || !state.preload) {
        state.shown = i;
        state.preload = true;
        render().catch(showError);
      }
    },
  });
}

async function render() {
  const s = state.scenes[state.index];
  const iceColor = rgb(css("--snow-amount-0") || "#f2f0f7").map((v) => v / 255);
  // Drawn bottom to top: years loading in the background, the year asked for, and (until that one has drawn) the year
  // still on screen.
  const order = state.scenes.map((_, i) => i)
    .filter((i) => i !== state.index && i !== state.shown && state.preload);
  order.push(state.index);
  if (state.shown !== null && state.shown !== state.index) order.push(state.shown);
  const layers = [
    ...order.map((i) => sceneLayer(i, iceColor)),
    new GeoJsonLayer({
      id: "outlines",
      data: outlines.features.filter((f) => (f.properties.set === "2015" ? state.show2015 : state.show2025)),
      filled: false,
      stroked: true,
      getLineColor: (f) => rgb(f.properties.set === "2015" ? css("--snow-then") : css("--snow-est")),
      getLineWidth: (f) => (f.properties.set === "2015" ? 1.6 : 2),
      lineWidthUnits: "pixels",
    }),
  ];
  deck.setProps({ layers });
  const m = MEASURED[s.date];
  el("readout").textContent = state.threshold === 2 && m
    ? `whatcom.land measured ${m} km² of bright ice within 10 km of the summit on this date (39.8 km² in 2015).` : "";
  el("thr-value").textContent = state.threshold.toFixed(1);
  el("scene-note").textContent = s.note;
  document.querySelectorAll("#years button").forEach((b, i) => b.setAttribute("aria-pressed", i === state.index));
}

async function start() {
  const [scenes, geo, projjson] = await Promise.all([
    fetch("data/baker_s2_scenes.json").then((r) => r.json()),
    fetch("data/baker_outlines.geojson").then((r) => r.json()),
    fetch("data/epsg32610.projjson").then((r) => r.json()),
  ]);
  state.scenes = scenes;
  state.index = scenes.length - 1;
  outlines = geo;
  utm10 = parseWkt(projjson);
  const years = el("years");
  scenes.forEach((s, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = s.date.slice(0, 4);
    b.title = s.date;
    b.addEventListener("click", () => {
      state.index = i;
      if (state.drawn.has(i)) state.shown = i;  // already drawn once: its tiles are cached, swap now
      if (state.shown !== i) {
        el("status").textContent = `Loading ${s.date.slice(0, 4)}…`;
        el("status").hidden = false;
      }
      render().catch(showError);
    });
    years.append(b);
  });
  el("thr").addEventListener("input", (e) => { state.threshold = Number(e.target.value); render().catch(showError); });
  el("ice").addEventListener("change", (e) => { state.showIce = e.target.checked; render().catch(showError); });
  el("o2015").addEventListener("change", (e) => { state.show2015 = e.target.checked; render().catch(showError); });
  el("o2025").addEventListener("change", (e) => { state.show2025 = e.target.checked; render().catch(showError); });
  if (window.self !== window.top) document.body.classList.add("embedded");
  await render();
}

start().catch(showError);
