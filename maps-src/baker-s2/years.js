// Mount Baker, one late summer a year since 1984, played like a film. Each frame is a Landsat scene's red and SWIR
// 1.6 µm bands, cut to a 16 km square as small Cloud-Optimized GeoTIFFs on R2 (scripts/baker_years_cogs.py and
// baker_years_upload.py; streaming whole scenes from Planetary Computer was too slow to play), and the bright-ice test
// (red / SWIR > threshold, on surface reflectance) runs on the GPU, so the threshold works while it plays. Frames load in
// the background a few at a time; the film plays as far as they have arrived.
import { Deck, MapView } from "@deck.gl/core";
import { GeoJsonLayer } from "@deck.gl/layers";
import { MultiCOGLayer } from "@developmentseed/deck.gl-geotiff";
import { parseWkt } from "@developmentseed/proj";

const SUMMIT = [-121.8144, 48.7768];
const LOADING_AT_ONCE = 4;
const FRAME_MS = 450;

const el = (id) => document.getElementById(id);
const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const rgb = (hex) => [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16));

// r = red, a = SWIR, each a uint16 digital number normalized to 0–1 (DN / 65535). Landsat Collection 2 surface
// reflectance = DN × 0.0000275 − 0.2, i.e. v × 1.8022 − 0.2. Background: red reflectance 0–0.8 with gamma 1.6, the
// flipbook's stretch.
const IceRatio = {
  name: "iceRatio",
  fs: `\
uniform iceRatioUniforms {
  float threshold;
  float showIce;
  vec3 iceColor;
} iceRatio;
`,
  inject: {
    "fs:DECKGL_FILTER_COLOR": /* glsl */ `
  if (color.r == 0.0) discard;
  float iceR = color.r * 1.8022 - 0.2;
  float iceS = max(color.a * 1.8022 - 0.2, 0.001);
  float iceGrey = pow(clamp(iceR / 0.8, 0.0, 1.0), 1.0 / 1.6);
  if (iceRatio.showIce > 0.5 && iceR / iceS > iceRatio.threshold) {
    color = vec4(iceRatio.iceColor, 1.0);
  } else {
    color = vec4(vec3(iceGrey) * (iceRatio.showIce > 0.5 ? 0.72 : 1.0), 1.0);
  }
`,
  },
  uniformTypes: { threshold: "f32", showIce: "f32", iceColor: "vec3<f32>" },
  getUniforms: (p) => ({ threshold: p.threshold ?? 2, showIce: p.showIce ?? 1, iceColor: p.iceColor ?? [0.95, 0.94, 0.97] }),
};

const state = { frames: [], index: 0, shown: null, playing: false, threshold: 2, showIce: true, show2015: true,
  drawn: new Set(), mounted: new Set() };
let outlines = null;
let utm10 = null;
let timer = null;

const deck = new Deck({
  parent: el("map"),
  views: new MapView({ repeat: false }),
  controller: { dragRotate: false, touchRotate: false },
  initialViewState: { longitude: SUMMIT[0], latitude: SUMMIT[1], zoom: window.innerWidth < 640 ? 11.2 : 11.9, minZoom: 10, maxZoom: 14 },
  getCursor: ({ isDragging }) => (isDragging ? "grabbing" : "grab"),
  onError: (e) => showError(e),
});

function showError(e) {
  el("status").textContent = "The images did not load. Reload the page to try again.";
  el("status").hidden = false;
  console.error(e);
}

// Mount more frames while fewer than LOADING_AT_ONCE are still loading: the chosen year first, then onwards in time.
function mountMore() {
  const n = state.frames.length;
  const loading = [...state.mounted].filter((i) => !state.drawn.has(i)).length;
  let room = LOADING_AT_ONCE - loading;
  for (let k = 0; k < n && room > 0; k++) {
    const i = (state.index + k) % n;
    if (!state.mounted.has(i)) { state.mounted.add(i); room--; }
  }
}

function frameLayer(i, iceColor) {
  const f = state.frames[i];
  const abs = (u) => new URL(u, document.baseURI).href;  // the COG reader needs absolute URLs
  f.sources ??= { red: { url: abs(f.red) }, swir: { url: abs(f.swir) } };
  return new MultiCOGLayer({
    id: `ls-${f.year}`,
    sources: f.sources,
    composite: { r: "red", g: "red", b: "red", a: "swir" },
    epsgResolver: async () => utm10,
    renderPipeline: [{ module: IceRatio, props: { threshold: state.threshold, showIce: state.showIce ? 1 : 0, iceColor } }],
    onViewportLoad: () => {
      const first = !state.drawn.has(i);
      state.drawn.add(i);
      if (i === state.index && state.shown !== i) state.shown = i;
      // deck.gl drops setProps made during its own update, which is when this fires: redraw just after
      if (first) { mountMore(); setTimeout(render, 0); }
    },
  });
}

function render() {
  const iceColor = rgb(css("--snow-amount-0") || "#f2f0f7").map((v) => v / 255);
  // Every mounted frame is drawn (a hidden layer stops loading); the one on screen goes last, on top.
  const order = [...state.mounted].filter((i) => i !== state.shown);
  if (state.shown !== null) order.push(state.shown);
  const layers = order.map((i) => frameLayer(i, iceColor));
  layers.push(new GeoJsonLayer({
    id: "outlines",
    data: state.show2015 ? outlines.features.filter((f) => f.properties.set === "2015") : [],
    filled: false, stroked: true,
    getLineColor: rgb(css("--snow-then") || "#6a51a3"), getLineWidth: 1.4, lineWidthUnits: "pixels",
  }));
  deck.setProps({ layers });
  const f = state.frames[state.index];
  // The label follows the year asked for at once (a finger on the strip); the image follows when it has arrived
  el("year").textContent = f.year;
  el("caption").textContent = state.drawn.has(state.index)
    ? `${new Date(f.date + "T12:00").toLocaleDateString("en-US", { month: "long", day: "numeric" })}, ${f.satellite}`
      + (f.partly_cloudy ? " · partly cloudy" : "")
    : "loading this summer…";
  const tl = el("timeline");
  [...tl.children].forEach((tick, i) => {
    tick.classList.toggle("loaded", state.drawn.has(i));
    tick.classList.toggle("now", i === state.index);
  });
  tl.setAttribute("aria-valuenow", f.year);
  tl.setAttribute("aria-valuetext", `${f.year}`);
  el("thr-value").textContent = state.threshold.toFixed(1);
  const waiting = state.shown !== state.index;
  el("status").textContent = waiting ? `Loading ${f.year}…` : `${state.drawn.size} of ${state.frames.length} summers loaded`;
  el("status").hidden = !waiting && state.drawn.size === state.frames.length;
  el("play").textContent = state.playing ? "❚❚ Pause" : "▶ Play";
}

function go(i) {
  if (i === state.index && state.mounted.size) return;
  state.index = i;
  if (state.drawn.has(i)) state.shown = i;
  mountMore();
  render();
}

function tick() {
  if (state.shown !== state.index) return;  // wait for the current frame to arrive
  const next = (state.index + 1) % state.frames.length;
  if (next === 0 && state.drawn.size < state.frames.length) return;  // hold on the last loaded year
  go(next);
}

function setPlaying(on) {
  state.playing = on;
  clearInterval(timer);
  if (on) {
    if (state.index === state.frames.length - 1) go(0);
    timer = setInterval(tick, FRAME_MS);
  }
  render();
}

// The year strip: touch or drag anywhere to scrub (pointer events cover mouse, pen and touch), scroll or swipe over it
// to step, arrow keys for the keyboard. Any of these pauses playback.
function timeline() {
  const tl = el("timeline");
  const n = state.frames.length;
  tl.replaceChildren(...state.frames.map((f) => Object.assign(document.createElement("i"), { title: f.year })));
  const at = (x) => {
    const r = tl.getBoundingClientRect();
    return Math.max(0, Math.min(n - 1, Math.floor(((x - r.left) / r.width) * n)));
  };
  const scrub = (i) => { if (state.playing) setPlaying(false); go(i); };
  tl.addEventListener("pointerdown", (e) => { tl.setPointerCapture(e.pointerId); scrub(at(e.clientX)); });
  tl.addEventListener("pointermove", (e) => { if (tl.hasPointerCapture(e.pointerId)) scrub(at(e.clientX)); });
  let wheel = 0;
  tl.addEventListener("wheel", (e) => {
    e.preventDefault();
    wheel += Math.abs(e.deltaX) > Math.abs(e.deltaY) ? e.deltaX : e.deltaY;
    const steps = Math.trunc(wheel / 30);
    if (steps) { wheel -= steps * 30; scrub(Math.max(0, Math.min(n - 1, state.index + steps))); }
  }, { passive: false });
  tl.addEventListener("keydown", (e) => {
    const k = { ArrowLeft: -1, ArrowDown: -1, ArrowRight: 1, ArrowUp: 1 }[e.key];
    if (k) scrub(Math.max(0, Math.min(n - 1, state.index + k)));
    else if (e.key === "Home") scrub(0);
    else if (e.key === "End") scrub(n - 1);
    else return;
    e.preventDefault();
  });
}

async function start() {
  const [data, geo, projjson] = await Promise.all([
    fetch("data/baker_years.json").then((r) => r.json()),
    fetch("data/baker_outlines.geojson").then((r) => r.json()),
    fetch("data/epsg32610.projjson").then((r) => r.json()),
  ]);
  state.frames = data.frames;
  outlines = geo;
  utm10 = parseWkt(projjson);
  timeline();
  el("play").addEventListener("click", () => setPlaying(!state.playing));
  el("thr").addEventListener("input", (e) => { state.threshold = Number(e.target.value); render(); });
  el("ice").addEventListener("change", (e) => { state.showIce = e.target.checked; render(); });
  el("o2015").addEventListener("change", (e) => { state.show2015 = e.target.checked; render(); });
  if (window.self !== window.top) document.body.classList.add("embedded");
  go(0);
}

start().catch(showError);

