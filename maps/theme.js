// whatcom.land · THEME: every color on the site, in one place (Phase 3 design system).
// Load in <head>, before style.css is applied and before any page script. It also publishes each color as a CSS
// custom property (--family-key, --family-key-0…n for ramps), so style.css never repeats a hex value.
// One visual language: each kind of thing keeps its own color family on every tab, and age or amount runs
// light → dark. A hex value belongs to exactly one family (tools/check_theme.py enforces this).
// The block between the THEME-JSON markers must stay plain JSON: the Python pipeline and the check read it.
const THEME = /*THEME-JSON*/{
  "neutral": {
    "ink": "#1f2a24", "muted": "#5b6760", "paper": "#fbfaf6", "card": "#ffffff", "line": "#e2e0d8",
    "accent": "#2f6b4f", "county": "#333333", "outline": "#222222", "strong": "#111111", "black": "#000000",
    "ref": "#555555", "axis": "#c9c5b9", "nodata": "#cfcfcf", "me": "#ffd400",
    "flag_ink": "#5a3e00", "flag_bg": "#fbf1dc"
  },
  "harvest": {
    "year": ["#f6e8c3", "#dfc27d", "#bf812d", "#8c510a", "#543005"],
    "owner": { "small": "#fdae6b", "large_private": "#e6550d", "state": "#8c2d04", "unlisted": "#9a9a9a" },
    "when": ["#01665e", "#35978f", "#80cdc1", "#c7eae5"],
    "kind": { "salvage": "#e0a458", "uneven": "#8d99ae", "even": "#3d405b", "other": "#9a9a9a" },
    "longterm": "#8a8f98",
    "cut": { "cleared": "#7a0177", "partly": "#dd3497", "standing": "#fcc5c0", "unknown": "#9a9a9a" },
    "outline": "#3b2a12"
  },
  "fire": {
    "year": ["#fee5d9", "#fcae91", "#fb6a4a", "#de2d26", "#a50f15"],
    "outline": "#3b0008",
    "slider": "#b2301f",
    "severity": { "low": "#fcae91", "moderate": "#fb6a4a", "high": "#a50f15" }
  },
  "conserved": {
    "gap": ["#00441b", "#2a924a", "#7bc87c", "#d9f0d3"],
    "owner": { "nps": "#24693d", "usfs": "#6fa96a", "fed": "#b5d6a7", "dnr": "#a67c2e", "state": "#dcc27a",
               "local": "#5b86a8", "ngo": "#c2571a", "other": "#a3a19a" },
    "worked": "#b58b2a",
    "holder": { "ngo": "#c2571a", "fed": "#7a4a9e", "state": "#dcc27a", "local": "#5b86a8", "other": "#a3a19a" },
    "line": "#1d6b36",
    "outline": "#0b2e17"
  },
  "flood": {
    "level": ["#deebf7", "#9ecae1", "#6baed6", "#2171b5", "#08306b"],
    "zone": { "floodway": "#08306b", "high": "#2171b5", "coastal": "#4a6fa5", "moderate": "#9ecae1" },
    "levee": "#d94801"
  },
  "farm": {
    "group": { "berries": "#a3195b", "corn": "#e8b10c", "hay": "#b9ad5a", "vegetables": "#5e7d1e", "grains": "#c96a34",
               "trees": "#8a5a2b", "fallow": "#bdb4a3" },
    "line": ["#7b6a4e", "#3e3426"],
    "outline": "#2b2418"
  },
  "snow": {
    "amount": ["#f2f0f7", "#cbc9e2", "#9e9ac8", "#756bb1", "#54278f", "#3f007d"],
    "then": "#6a51a3",
    "est": "#0e8a9e"
  }
}/*THEME-JSON*/;

(function publishCssVars() {
  const root = document.documentElement.style;
  const put = (name, v) => {
    if (typeof v === "string") root.setProperty(`--${name}`, v);
    else if (Array.isArray(v)) v.forEach((x, i) => put(`${name}-${i}`, x));
    else Object.entries(v).forEach(([k, x]) => put(`${name}-${k.replace(/_/g, "-")}`, x));
  };
  Object.entries(THEME).forEach(([fam, v]) => put(fam, v));
})();
