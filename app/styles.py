"""
ResQPulse AI — design tokens, incident metadata and the app stylesheet.

Direction (references chosen by the team: kaggle.com, motion.dev, impeccable.style): a light, flat console.
Light grey ground, white panels with hairlines, black pill buttons, one signal yellow for live state, active
navigation, focus and attention. Figtree for text; JetBrains Mono only for IDs, coordinates, scores and field labels.
Severity colours appear only where they mean severity. No emoji anywhere.
"""

from typing import Dict

# Severity palette. Keys are read across the app: badge_bg/badge_text for pills, text/bg for tinted rows,
# border for accents, map_color for Folium markers, bar_color for the severity ruler fill.
SEVERITY_COLORS: Dict[str, Dict[str, str]] = {
    "CRITICAL": {
        "text": "#A11A12",
        "bg": "#FDECEA",
        "border": "#D92D20",
        "badge_bg": "#D92D20",
        "badge_text": "#FFFFFF",
        "map_color": "red",
        "bar_color": "#D92D20",
    },
    "HIGH": {
        "text": "#9A2A0A",
        "bg": "#FFF0E6",
        "border": "#E8590C",
        "badge_bg": "#C4320A",
        "badge_text": "#FFFFFF",
        "map_color": "orange",
        "bar_color": "#E8590C",
    },
    "MEDIUM": {
        "text": "#6E4A00",
        "bg": "#FFF7DB",
        "border": "#E0A100",
        "badge_bg": "#F5B301",
        "badge_text": "#141414",
        "map_color": "beige",
        "bar_color": "#E0A100",
    },
    "LOW": {
        "text": "#1F5C39",
        "bg": "#E9F4EE",
        "border": "#2F7D4F",
        "badge_bg": "#2F7D4F",
        "badge_text": "#FFFFFF",
        "map_color": "green",
        "bar_color": "#2F7D4F",
    },
    "NON_EMERGENCY": {
        "text": "#4D4D4D",
        "bg": "#F0F0EE",
        "border": "#8A8A86",
        "badge_bg": "#5C5C59",
        "badge_text": "#FFFFFF",
        "map_color": "gray",
        "bar_color": "#8A8A86",
    },
}

# Incident types. "icon" is kept for compatibility and is empty: the interface uses words, not pictograms.
INCIDENT_TYPE_META: Dict[str, Dict[str, str]] = {
    "FIRE": {"icon": "", "name": "Fire / Explosion"},
    "FLOOD": {"icon": "", "name": "Flood / Waterlogging"},
    "STORM_CYCLONE": {"icon": "", "name": "Storm / Cyclone"},
    "EARTHQUAKE_COLLAPSE": {"icon": "", "name": "Earthquake / Collapse"},
    "TRANSPORT_ACCIDENT": {"icon": "", "name": "Transport Accident"},
    "MEDICAL": {"icon": "", "name": "Medical Emergency"},
    "VIOLENCE_CRIME": {"icon": "", "name": "Violence / Crime"},
    "NON_EMERGENCY": {"icon": "", "name": "Non-Emergency"},
}

# SDG Targets Metadata
SDG_META: Dict[str, Dict[str, str]] = {
    "3.6": {"label": "SDG 3.6", "title": "Road Safety",
            "desc": "Halve deaths and injuries from road traffic accidents"},
    "3.d": {"label": "SDG 3.d", "title": "Health Risk Early Warning",
            "desc": "Strengthen early warning and risk reduction for health"},
    "11.5": {"label": "SDG 11.5", "title": "Disaster Impact Reduction",
             "desc": "Reduce deaths and people affected by water-related disasters"},
    "13.1": {"label": "SDG 13.1", "title": "Climate Resilience",
             "desc": "Strengthen resilience to climate-related hazards"},
    "16.1": {"label": "SDG 16.1", "title": "Reduce Violence",
             "desc": "Significantly reduce all forms of violence and related deaths"},
    "16.6": {"label": "SDG 16.6", "title": "Accountable Institutions",
             "desc": "Develop effective, accountable and transparent institutions"},
}

# Responder names (the name is historical; there are no icons)
RESPONDER_ICONS: Dict[str, str] = {
    "AMBULANCE": "Ambulance",
    "FIRE_BRIGADE": "Fire brigade",
    "POLICE": "Police",
    "TRAFFIC_POLICE": "Traffic police",
    "DISASTER_RESPONSE": "Disaster response (NDRF/SDRF)",
}

CUSTOM_CSS = """
<style>
/* Fonts are served from app/static/fonts (Streamlit static serving), so the demo works with no internet. OFL licences sit beside them. */
@font-face { font-family: 'Figtree'; src: url('app/static/fonts/Figtree-Variable.ttf') format('truetype'); font-weight: 300 900; font-display: swap; }
@font-face { font-family: 'JetBrains Mono'; src: url('app/static/fonts/JetBrainsMono-Variable.ttf') format('truetype'); font-weight: 100 800; font-display: swap; }

:root {
    --ground: #F5F5F3;
    --surface: #FFFFFF;
    --ink: #141414;
    --ink-2: #4D4D4D;
    --ink-3: #6B6B68;
    --hair: #E4E4E1;
    --hair-2: #D4D4D0;
    --signal: #FFCC00;
    --signal-tint: #FFF4CC;
    --ease: cubic-bezier(0.22, 1, 0.36, 1);
    --sans: 'Figtree', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}

/* ---------- base ---------- */
html, body, .stApp, [class*="css"], button, input, textarea, select { font-family: var(--sans); }
.stApp { background: var(--ground); color: var(--ink); }
.block-container { padding-top: 1.4rem; padding-bottom: 4rem; max-width: 1200px; }
.stApp h1, .stApp h2, .stApp h3, .stApp h4 { font-family: var(--sans); color: var(--ink); letter-spacing: -0.02em; text-wrap: balance; }
.stApp h2 { font-size: 2.35rem; font-weight: 600; margin: 0.6rem 0 0.1rem; }
.stApp h3 { font-size: 1.15rem; font-weight: 600; margin-top: 1rem; padding-bottom: 0.2rem; }
.stApp h4 { font-size: 0.98rem; font-weight: 600; margin-top: 1.2rem; }
.stApp p, .stApp li { color: var(--ink-2); max-width: 72ch; }
.stApp strong { color: var(--ink); font-weight: 600; }
[data-testid="stMarkdownContainer"] p, [data-testid="stMarkdownContainer"] li, [data-testid="stCaptionContainer"] p,
[data-testid="stWidgetLabel"] p, button[data-testid^="stBaseButton"]:not([data-testid*="header"]) p, [data-testid="stSidebar"] p, [data-testid="stExpander"] summary p,
.topbar, .panel, .q-row, .empty, .warn, .heat, .tag { font-family: var(--sans) !important; }
code, pre, .mono { font-family: var(--mono) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, .stApp small { color: var(--ink-3) !important; opacity: 1 !important; }
hr { border: none !important; border-top: 1px solid var(--hair) !important; margin: 1rem 0 !important; }
::selection { background: var(--signal); color: var(--ink); }
:focus-visible { outline: 2px solid var(--ink) !important; outline-offset: 2px; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: var(--hair-2); border-radius: 999px; border: 2px solid var(--ground); }

/* chrome we do not use */
[data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton { display: none; }
[data-testid="stHeader"] { background: transparent; }

/* ---------- left rail (Kaggle) ---------- */
[data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--hair); }
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarContent"] { padding-top: 0.6rem; }
.rail-brand { display: flex; align-items: center; gap: 0.6rem; padding: 0.2rem 0.4rem 1.2rem; }
.rail-brand svg { width: 26px; height: 26px; flex: none; }
.rail-brand b { font-size: 1.12rem; font-weight: 700; letter-spacing: -0.02em; color: var(--ink); }
.st-key-nav_screen_selection [data-testid="stWidgetLabel"] { display: none; }
.st-key-nav_screen_selection [role="radiogroup"] { gap: 2px; }
.st-key-nav_screen_selection [role="radiogroup"] label {
    width: 100%; padding: 0.62rem 0.9rem; border-radius: 12px; margin: 0;
    transition: background 0.2s var(--ease); cursor: pointer;
}
.st-key-nav_screen_selection label[data-testid="stRadioOption"] > div { width: 100%; }
.st-key-nav_screen_selection label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display: none; }
.st-key-nav_screen_selection [role="radiogroup"] label p { font-size: 0.97rem; font-weight: 500; color: var(--ink-2); }
.st-key-nav_screen_selection [role="radiogroup"] label:hover { background: #F2F2F0; }
.st-key-nav_screen_selection [role="radiogroup"] { width: 100%; }
.st-key-nav_screen_selection [role="radiogroup"] label[data-selected="true"],
.st-key-nav_screen_selection [role="radiogroup"] label[data-selected="true"]:hover { background: var(--signal-tint); }
.st-key-nav_screen_selection label[data-selected="true"] p { color: var(--ink); font-weight: 600; }
[data-testid="stSidebar"] [data-testid="stExpander"] details { border: 1px solid var(--hair); border-radius: 12px; background: var(--surface); }
[data-testid="stSidebar"] [data-testid="stExpander"] summary p { font-weight: 600; color: var(--ink); }
.rail-foot { font-size: 0.8rem; color: var(--ink-3); padding: 0 0.4rem; line-height: 1.5; }

/* ---------- top bar ---------- */
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 0.2rem 0 1rem; border-bottom: 1px solid var(--hair); margin-bottom: 0.4rem; }
.topbar-crumb { font-size: 0.9rem; color: var(--ink-3); }
.topbar-crumb b { color: var(--ink); font-weight: 600; }
.status-pill { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.38rem 0.85rem; border-radius: 999px;
    background: var(--surface); border: 1px solid var(--hair-2); font-family: var(--mono); font-size: 0.72rem;
    letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink); white-space: nowrap; }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: #9A9A96; flex: none; }
.status-pill.live .status-dot { background: var(--signal); box-shadow: 0 0 0 0 rgba(255, 204, 0, 0.7); animation: live 2.2s var(--ease) infinite; }
@keyframes live { 0% { box-shadow: 0 0 0 0 rgba(255, 204, 0, 0.7); } 70% { box-shadow: 0 0 0 8px rgba(255, 204, 0, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 204, 0, 0); } }
.page-lede { font-size: 1.02rem; color: var(--ink-2); margin: 0.1rem 0 0.6rem; max-width: 72ch; }

/* ---------- panels ---------- */
.panel { background: var(--surface); border: 1px solid var(--hair); border-radius: 16px; padding: 1.5rem 1.6rem; margin-bottom: 1rem; }
.alert-head { display: flex; flex-wrap: wrap; align-items: flex-start; justify-content: space-between; gap: 0.8rem; margin-bottom: 1.2rem; }
.alert-title { font-size: 1.75rem; font-weight: 600; letter-spacing: -0.025em; color: var(--ink); line-height: 1.15; }
.alert-sub { font-family: var(--mono); font-size: 0.74rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--ink-3); margin-top: 0.35rem; }
.alert-grid { display: grid; grid-template-columns: minmax(0, 1fr) 300px; gap: 1.8rem; }
.alert-grid > aside { border-left: 1px solid var(--hair); padding-left: 1.6rem; }
.alert-summary { font-size: 1.22rem; line-height: 1.55; color: var(--ink); font-weight: 500; margin: 0 0 1.4rem; max-width: 60ch; }
.field-label { font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-3); margin-bottom: 0.35rem; }
.meta-row { padding: 0.75rem 0; border-bottom: 1px solid var(--hair); }
.meta-row:first-child { padding-top: 0; }
.meta-row:last-child { border-bottom: none; }
.meta-val { font-size: 1rem; color: var(--ink); font-weight: 500; line-height: 1.4; }
.meta-num { font-size: 1.45rem; font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
.meta-num small { font-size: 0.85rem; color: var(--ink-3); font-weight: 500; }
.coords { font-family: var(--mono); font-size: 0.78rem; color: var(--ink-3); margin-top: 0.25rem; }
.section-gap { margin-top: 1.3rem; }
.dup-flag { display: inline-flex; align-items: center; gap: 0.5rem; background: var(--surface); color: var(--ink);
    border: 1px solid var(--hair-2); border-radius: 10px; padding: 0.55rem 0.85rem; font-size: 0.92rem; margin-bottom: 1.1rem; }
.dup-flag b { font-family: var(--mono); font-weight: 600; font-size: 0.85rem; }

/* severity ruler: the signature. Five cells, filled to the score */
.ruler { display: flex; align-items: center; gap: 0.9rem; }
.ruler-cells { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; flex: 1; max-width: 420px; }
.ruler-cell { height: 12px; border-radius: 3px; background: #ECECE9; position: relative; overflow: hidden; }
.ruler-cell i { position: absolute; inset: 0 auto 0 0; display: block; }
.ruler-val { font-family: var(--mono); font-size: 0.9rem; font-weight: 600; color: var(--ink); white-space: nowrap; font-variant-numeric: tabular-nums; }
.ruler-val span { color: var(--ink-3); font-weight: 400; }
.ruler.mini { flex: none; gap: 0.55rem; }
.ruler.mini .ruler-cells { flex: 0 0 110px; width: 110px; max-width: 110px; gap: 3px; }
.ruler.mini .ruler-cell { height: 7px; border-radius: 2px; }
.ruler.mini .ruler-val { font-size: 0.78rem; }

/* pills and tags */
.sev-pill { display: inline-flex; align-items: center; gap: 0.45rem; border-radius: 999px; padding: 0.38rem 0.9rem;
    font-family: var(--mono); font-size: 0.74rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; white-space: nowrap; }
.status-tag { display: inline-flex; align-items: center; border-radius: 999px; padding: 0.32rem 0.75rem; border: 1px solid var(--hair-2);
    font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-2); background: var(--surface); }
.tag { display: inline-flex; align-items: center; gap: 0.4rem; border: 1px solid var(--hair-2); border-radius: 999px;
    padding: 0.32rem 0.8rem; font-size: 0.88rem; color: var(--ink); background: var(--surface); margin: 0 0.35rem 0.4rem 0; }
.tag i { width: 7px; height: 7px; border-radius: 50%; display: inline-block; flex: none; }
.tag.injury i { background: #D92D20; }
.tag.hazard i { background: #E0A100; }
.tag.responder { font-weight: 600; }
.tag.sdg b { font-family: var(--mono); font-size: 0.74rem; font-weight: 600; }
.muted { color: var(--ink-3); font-size: 0.92rem; }

/* non-emergency */
.calm-head { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.calm-title { font-size: 1.5rem; font-weight: 600; letter-spacing: -0.02em; color: var(--ink); }
.calm-facts { display: flex; flex-wrap: wrap; gap: 0 2rem; border-top: 1px solid var(--hair); margin-top: 1.1rem; padding-top: 1rem; }

/* attention heatmap */
.heat { background: var(--surface); border: 1px solid var(--hair); border-radius: 16px; padding: 1.6rem; line-height: 2.5; font-size: 1.2rem; margin: 0.4rem 0 1rem; }
.heat-tok { display: inline-block; padding: 0.05rem 0.42rem; margin: 0.12rem 0.08rem; border-radius: 6px; color: var(--ink); font-weight: 500; cursor: default; }
.heat-legend { display: flex; align-items: center; gap: 0.75rem; font-family: var(--mono); font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--ink-3); }
.heat-ramp { width: 160px; height: 10px; border-radius: 999px; background: linear-gradient(90deg, rgba(255, 204, 0, 0.08), rgba(255, 204, 0, 1)); border: 1px solid var(--hair); }
.heat-note { font-size: 0.95rem; color: var(--ink-2); margin: 0.8rem 0 0.4rem; max-width: 80ch; }
.prob-row { display: grid; grid-template-columns: 220px minmax(0, 1fr) 64px; align-items: center; gap: 1rem; padding: 0.55rem 0; border-bottom: 1px solid var(--hair); }
.prob-row:last-child { border-bottom: none; }
.prob-name { font-size: 0.95rem; color: var(--ink); }
.prob-bar { height: 8px; background: #ECECE9; border-radius: 999px; overflow: hidden; }
.prob-bar i { display: block; height: 100%; background: var(--ink); border-radius: 999px; }
.prob-val { font-family: var(--mono); font-size: 0.82rem; text-align: right; color: var(--ink); font-variant-numeric: tabular-nums; }

/* queue */
.q-row { background: var(--surface); border: 1px solid var(--hair); border-radius: 14px; padding: 1.05rem 1.25rem; margin: 0.9rem 0 0.4rem; transition: border-color 0.2s var(--ease); }
.q-row:hover { border-color: var(--hair-2); }
.q-top { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.q-title { font-size: 1.05rem; font-weight: 600; color: var(--ink); }
.q-id { font-family: var(--mono); font-size: 0.74rem; color: var(--ink-3); letter-spacing: 0.04em; margin-left: 0.6rem; }
.q-loc { font-size: 0.9rem; color: var(--ink-3); margin-top: 0.15rem; }
.q-sum { font-size: 0.97rem; color: var(--ink-2); margin-top: 0.6rem; }
.q-right { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }

/* empty and warning */
.empty { text-align: center; padding: 3rem 2rem; border: 1px dashed var(--hair-2); border-radius: 16px; margin: 1.2rem 0; background: transparent; }
.empty-title { font-size: 1.2rem; font-weight: 600; color: var(--ink); margin-bottom: 0.4rem; }
.empty-desc { color: var(--ink-3); font-size: 0.98rem; max-width: 52ch; margin: 0 auto; line-height: 1.55; }
.warn { background: var(--signal-tint); color: var(--ink); border-radius: 12px; padding: 0.85rem 1.1rem; font-size: 0.95rem; margin-bottom: 1rem; }

/* ---------- native controls ---------- */
button[data-testid^="stBaseButton"]:not([data-testid*="header"]) {
    border-radius: 999px !important; font-weight: 600 !important; padding: 0.5rem 1.15rem !important;
    border: 1px solid var(--hair-2) !important; background: var(--surface) !important; color: var(--ink) !important;
    transition: background 0.2s var(--ease), border-color 0.2s var(--ease) !important; box-shadow: none !important;
}
button[data-testid^="stBaseButton"]:not([data-testid*="header"]):hover, button[data-testid^="stBaseButton"]:not([data-testid*="header"]):hover { border-color: var(--ink) !important; }
button[data-testid^="stBaseButton"]:not([data-testid*="header"]):disabled { opacity: 1 !important; color: #A3A3A0 !important; border-color: var(--hair) !important; background: #FAFAF9 !important; }
button[data-testid="stBaseButton-primary"][kind="primary"]:disabled { background: #B8B8B4 !important; border-color: #B8B8B4 !important; color: #FFFFFF !important; }
button[data-testid="stBaseButton-primary"][kind="primary"] { background: var(--ink) !important; color: #FFFFFF !important; border-color: var(--ink) !important; }
button[data-testid="stBaseButton-primary"][kind="primary"]:hover { background: #2E2E2E !important; }
button[data-testid^="stBaseButton"]:not([data-testid*="header"]) p, button[data-testid^="stBaseButton"]:not([data-testid*="header"]) p { font-weight: 600; font-size: 0.93rem; }
button[data-testid^="stBaseButton"]:not([data-testid*="header"]) p, button[data-testid^="stBaseButton"]:not([data-testid*="header"]) p { color: var(--ink) !important; }
button[data-testid="stBaseButton-primary"][kind="primary"] p { color: #FFFFFF !important; }
button[data-testid^="stBaseButton"]:not([data-testid*="header"]):disabled p { color: #A3A3A0 !important; }
button[data-testid="stBaseButton-primary"][kind="primary"]:disabled p { color: #FFFFFF !important; }
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    background: var(--surface) !important; border-radius: 12px !important; font-size: 1rem; color: var(--ink);
}
[data-testid="stTextArea"] > div > div, [data-testid="stTextInput"] > div > div { border-radius: 12px !important; border-color: var(--hair-2) !important; background: var(--surface) !important; }
[data-testid="stTextArea"] > div > div:focus-within, [data-testid="stTextInput"] > div > div:focus-within { border-color: var(--ink) !important; }
[data-testid="stSelectbox"] > div > div { border-radius: 12px !important; background: var(--surface) !important; border-color: var(--hair-2) !important; }
[data-testid="stWidgetLabel"] p { font-size: 0.88rem; font-weight: 600; color: var(--ink); }
[data-testid="stMetric"] { background: var(--surface); border: 1px solid var(--hair); border-radius: 14px; padding: 1rem 1.15rem; }
[data-testid="stMetricLabel"] *, [data-testid="stMetricLabel"] p { white-space: normal !important; text-overflow: clip !important; overflow: visible !important; }
[data-testid="stMetricLabel"] p { font-family: var(--mono); font-size: 0.7rem !important; letter-spacing: 0.1em; text-transform: uppercase; color: var(--ink-3) !important; }
[data-testid="stMetricValue"] { font-weight: 600; letter-spacing: -0.02em; font-variant-numeric: tabular-nums; color: var(--ink); }
[data-testid="stDataFrame"] { border: 1px solid var(--hair); border-radius: 12px; overflow: hidden; }
[data-testid="stAudioInput"], [data-testid="stFileUploaderDropzone"] { border-radius: 14px !important; }
[data-testid="stFileUploaderDropzone"] { background: var(--surface) !important; border: 1px dashed var(--hair-2) !important; }
[data-testid="stAlert"] { border-radius: 12px; }
iframe { border-radius: 14px; border: 1px solid var(--hair) !important; }

@media (max-width: 900px) {
    .alert-grid { grid-template-columns: 1fr; }
    .alert-grid > aside { border-left: none; padding-left: 0; border-top: 1px solid var(--hair); padding-top: 1rem; }
    .prob-row { grid-template-columns: 1fr 64px; }
    .prob-bar { grid-column: 1 / -1; grid-row: 2; }
}
@media (prefers-reduced-motion: reduce) { .status-pill.live .status-dot { animation: none; } }
</style>
"""


def get_severity_style(severity_label: str) -> Dict[str, str]:
    """Return styling tokens for a given severity label with safe fallback."""
    clean_label = str(severity_label).upper().strip() if severity_label else "LOW"
    return SEVERITY_COLORS.get(clean_label, SEVERITY_COLORS["LOW"])


def get_incident_type_meta(incident_type: str) -> Dict[str, str]:
    """Return the human-readable name for an incident type (icon is always empty)."""
    clean_type = str(incident_type).upper().strip() if incident_type else "NON_EMERGENCY"
    return INCIDENT_TYPE_META.get(clean_type, {"icon": "", "name": clean_type.replace("_", " ").title()})
