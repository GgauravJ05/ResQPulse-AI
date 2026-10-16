"""
ResQPulse AI — Frontend Styling and Formal Enterprise Design System
Defines consistent severity colors, badge styles, incident-type metadata,
and custom CSS for an enterprise mission-control emergency dispatch console.
"""

from typing import Dict, Any

# Primary Severity Color Mapping
# Consistent across all screens: CRITICAL (red), HIGH (orange), MEDIUM (yellow), LOW (green), NON_EMERGENCY (slate)
SEVERITY_COLORS: Dict[str, Dict[str, str]] = {
    "CRITICAL": {
        "text": "#991B1B",        # Deep formal red
        "bg": "#FEF2F2",          # Soft light crimson tint
        "border": "#B42318",      # Vivid red border
        "badge_bg": "#B42318",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "red",
        "bar_color": "#B91C1C",
        "gradient": None,
        "glow": "rgba(220, 38, 38, 0.25)",
    },
    "HIGH": {
        "text": "#9A3412",        # Deep formal orange
        "bg": "#FFF7ED",          # Soft light orange tint
        "border": "#C2570C",      # Vivid orange border
        "badge_bg": "#C2570C",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "orange",
        "bar_color": "#C2410C",
        "gradient": None,
        "glow": "rgba(234, 88, 12, 0.25)",
    },
    "MEDIUM": {
        "text": "#92400E",        # Deep formal amber
        "bg": "#FFFBEB",          # Soft light amber tint
        "border": "#B7791F",      # Vivid amber border
        "badge_bg": "#B7791F",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "beige",
        "bar_color": "#B45309",
        "gradient": None,
        "glow": "rgba(217, 119, 6, 0.25)",
    },
    "LOW": {
        "text": "#166534",        # Deep formal green
        "bg": "#F0FDF4",          # Soft light green tint
        "border": "#2F7D4F",      # Vivid green border
        "badge_bg": "#2F7D4F",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "green",
        "bar_color": "#15803D",
        "gradient": None,
        "glow": "rgba(22, 163, 74, 0.25)",
    },
    "NON_EMERGENCY": {
        "text": "#334155",        # Formal neutral slate
        "bg": "#F8FAFC",          # Soft slate tint
        "border": "#64748B",      # Slate border
        "badge_bg": "#64748B",    # Neutral badge fill
        "badge_text": "#FFFFFF",
        "map_color": "gray",
        "bar_color": "#475569",
        "gradient": None,
        "glow": "rgba(100, 116, 139, 0.2)",
    },
}

# Incident Type Metadata
INCIDENT_TYPE_META: Dict[str, Dict[str, str]] = {
    "FIRE": {
        "icon": "🔥",
        "name": "Fire / Explosion",
        "default_color": "#EF4444",
        "badge_bg": "#FEE2E2",
        "badge_text": "#991B1B",
    },
    "FLOOD": {
        "icon": "🌊",
        "name": "Flood / Waterlogging",
        "default_color": "#0284C7",
        "badge_bg": "#E0F2FE",
        "badge_text": "#075985",
    },
    "STORM_CYCLONE": {
        "icon": "🌀",
        "name": "Storm / Cyclone",
        "default_color": "#0D9488",
        "badge_bg": "#CCFBF1",
        "badge_text": "#115E59",
    },
    "EARTHQUAKE_COLLAPSE": {
        "icon": "🏚️",
        "name": "Earthquake / Collapse",
        "default_color": "#B45309",
        "badge_bg": "#FEF3C7",
        "badge_text": "#92400E",
    },
    "TRANSPORT_ACCIDENT": {
        "icon": "🚗",
        "name": "Transport Accident",
        "default_color": "#C2570C",
        "badge_bg": "#FFEDD5",
        "badge_text": "#9A3412",
    },
    "MEDICAL": {
        "icon": "🚑",
        "name": "Medical Emergency",
        "default_color": "#E11D48",
        "badge_bg": "#FFE4E6",
        "badge_text": "#9F1239",
    },
    "VIOLENCE_CRIME": {
        "icon": "🛡️",
        "name": "Violence / Crime",
        "default_color": "#7C3AED",
        "badge_bg": "#EDE9FE",
        "badge_text": "#5B21B6",
    },
    "NON_EMERGENCY": {
        "icon": "ℹ️",
        "name": "Non-Emergency",
        "default_color": "#64748B",
        "badge_bg": "#F1F5F9",
        "badge_text": "#334155",
    },
}

# SDG Targets Metadata
SDG_META: Dict[str, Dict[str, str]] = {
    "3.6": {
        "label": "SDG 3.6",
        "title": "Road Safety",
        "desc": "Halve deaths and injuries from road traffic accidents",
        "color": "#4C9F38",
    },
    "3.d": {
        "label": "SDG 3.d",
        "title": "Health Risk Early Warning",
        "desc": "Strengthen early warning and risk reduction for health",
        "color": "#4C9F38",
    },
    "11.5": {
        "label": "SDG 11.5",
        "title": "Disaster Impact Reduction",
        "desc": "Reduce deaths and people affected by water-related disasters",
        "color": "#FD9D24",
    },
    "13.1": {
        "label": "SDG 13.1",
        "title": "Climate Resilience",
        "desc": "Strengthen resilience to climate-related hazards",
        "color": "#3F7E44",
    },
    "16.1": {
        "label": "SDG 16.1",
        "title": "Reduce Violence",
        "desc": "Significantly reduce all forms of violence and related deaths",
        "color": "#00689D",
    },
    "16.6": {
        "label": "SDG 16.6",
        "title": "Accountable Institutions",
        "desc": "Develop effective, accountable and transparent institutions",
        "color": "#00689D",
    },
}

# Responder Badges
RESPONDER_ICONS: Dict[str, str] = {
    "AMBULANCE": "🚑 Ambulance",
    "FIRE_BRIGADE": "🚒 Fire Brigade",
    "POLICE": "👮 Police",
    "TRAFFIC_POLICE": "🚦 Traffic Police",
    "DISASTER_RESPONSE": "🦺 Disaster Response (NDRF/SDRF)",
}

# Stylesheet. Direction: a calm dispatch console on warm paper. One display serif for titles and numbers, one grotesque for
# everything else, mono only for IDs and coordinates. Red is reserved for critical, so it still means something.
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=Hanken+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --paper: #F7F5F0;
    --surface: #FFFFFF;
    --ink: #171A21;
    --ink-2: #4A5160;
    --ink-3: #6B7280;
    --hair: #E5E1D6;
    --hair-2: #D8D3C5;
    --navy: #14213D;
    --crit: #B42318;
    --ease: cubic-bezier(0.22, 1, 0.36, 1);
}

html, body, [class*="css"], .stApp {
    font-family: 'Hanken Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
}
.stApp { background: var(--paper); }
code, pre, .mono { font-family: 'JetBrains Mono', monospace !important; }

/* page title and section headings */
.stApp h1, .stApp h2, .stApp h3 {
    font-family: 'Newsreader', Georgia, serif;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: var(--ink);
    text-wrap: balance;
}
.stApp h2 { font-size: 2rem; margin-top: 0.4rem; }
.stApp h3 { font-size: 1.35rem; margin-top: 1.6rem; }
.stApp h4 { font-family: 'Hanken Grotesk', sans-serif; font-weight: 700; font-size: 0.95rem; color: var(--ink-2); letter-spacing: 0; }
.stApp p, .stApp li, .stApp label { max-width: 75ch; }
.block-container { padding-top: 2.2rem; max-width: 1180px; }

/* browser chrome we do not use, and the parts we keep */
[data-testid="stToolbar"], [data-testid="stDecoration"], .stDeployButton { display: none; }
[data-testid="stHeader"] { background: transparent; }
::selection { background: rgba(180, 35, 24, 0.18); color: var(--ink); }
:focus-visible { outline: 2px solid var(--navy) !important; outline-offset: 2px; border-radius: 6px; }
::-webkit-scrollbar { width: 10px; height: 10px; }
::-webkit-scrollbar-thumb { background: var(--hair-2); border-radius: 9999px; border: 2px solid var(--paper); }
[data-testid="stCaptionContainer"] { color: var(--ink-3); }

/* sidebar: the navigation rail */
[data-testid="stSidebar"] { background: #EFECE4; border-right: 1px solid var(--hair); }
[data-testid="stSidebar"] h3 { font-size: 1.05rem; margin-top: 0.4rem; }
[data-testid="stSidebar"] hr { border-color: var(--hair-2); }
[data-testid="stSidebar"] [role="radiogroup"] label { padding: 0.3rem 0; }

/* masthead */
.app-header {
    background: var(--navy);
    color: #FFFFFF;
    padding: 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 12px 28px -16px rgba(20, 33, 61, 0.55), 0 2px 4px rgba(20, 33, 61, 0.12);
}
.header-top-row { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1.2rem; }
.brand { display: flex; align-items: center; gap: 1.1rem; }
.brand-mark { flex: none; width: 52px; height: 52px; border-radius: 14px; background: rgba(255,255,255,0.08);
    display: grid; place-items: center; box-shadow: inset 0 0 0 1px rgba(255,255,255,0.16); }
.brand-mark svg { width: 30px; height: 30px; }
.app-title { font-family: 'Newsreader', Georgia, serif !important; font-size: 2.1rem !important; font-weight: 600 !important;
    letter-spacing: -0.02em; margin: 0 !important; padding: 0 !important; color: #FFFFFF !important; line-height: 1.1; }
.app-title em { font-style: italic; font-weight: 500; color: #F3B7AE; }
.app-tagline { font-size: 0.98rem; color: #B8C2D9; margin: 0.35rem 0 0 0; max-width: 52ch; }
.system-beacon { display: inline-flex; align-items: center; gap: 0.55rem; padding: 0.45rem 0.95rem; border-radius: 9999px;
    font-size: 0.74rem; font-weight: 600; color: #DCE3F2; letter-spacing: 0.08em; text-transform: uppercase;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,0.18); }
.pulse-dot { width: 8px; height: 8px; background: #4ADE80; border-radius: 50%; animation: pulse 2.4s var(--ease) infinite; }
@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0.55); }
    70% { box-shadow: 0 0 0 9px rgba(74, 222, 128, 0); }
    100% { box-shadow: 0 0 0 0 rgba(74, 222, 128, 0); }
}

/* surfaces */
.rq-card, .queue-card, .heatmap-container, .rq-stat-box {
    background: var(--surface); border: 1px solid var(--hair); border-radius: 14px;
}
.rq-card { padding: 1.6rem; margin-bottom: 1.4rem; box-shadow: 0 1px 2px rgba(23,26,33,0.04), 0 14px 30px -22px rgba(23,26,33,0.35); }
.rq-card-neutral { background: var(--surface); border: 1px solid var(--hair); border-radius: 14px;
    padding: 1.6rem; margin-bottom: 1.4rem; box-shadow: 0 1px 2px rgba(23,26,33,0.04); }

.rq-badge { display: inline-flex; align-items: center; padding: 0.32rem 0.8rem; border-radius: 9999px; font-weight: 700;
    font-size: 0.78rem; letter-spacing: 0.05em; margin: 0 0.4rem 0.4rem 0; text-transform: uppercase; }
.rq-chip { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.3rem 0.7rem; border-radius: 8px; font-size: 0.85rem;
    font-weight: 600; margin: 0.25rem 0.35rem 0.25rem 0; }
.rq-chip-injury { background: #FBECEA; color: #8E1B12; }
.rq-chip-hazard { background: #FBF1DC; color: #7A4B0B; }
.rq-chip-responder { background: #E8ECF6; color: #1E2F5C; }
.rq-chip-sdg { background: #E6F1EA; color: #1F5C39; }

.rq-stat-box { padding: 1rem 1.1rem; }
.rq-stat-label { font-size: 0.72rem; font-weight: 700; color: var(--ink-3); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.35rem; }
.rq-stat-val { font-family: 'Newsreader', Georgia, serif; font-size: 1.7rem; font-weight: 600; color: var(--ink); font-variant-numeric: tabular-nums; }

/* attention heatmap */
.heatmap-container { padding: 1.6rem; line-height: 2.6; font-size: 1.15rem; margin-bottom: 1rem; }
.heatmap-token { display: inline-block; padding: 0.15rem 0.5rem; margin: 0.15rem 0.2rem; border-radius: 6px; font-weight: 600; cursor: default; }
.heatmap-note { font-size: 0.92rem; color: var(--ink-2); background: #EFECE4; border-radius: 10px; padding: 0.85rem 1.1rem;
    margin-top: 1rem; display: flex; align-items: center; gap: 0.5rem; }

/* dispatcher queue */
.queue-card { padding: 1.15rem 1.3rem; margin-bottom: 0.9rem; transition: box-shadow 0.25s var(--ease), border-color 0.25s var(--ease); }
.queue-card:hover { border-color: var(--hair-2); box-shadow: 0 14px 28px -20px rgba(23,26,33,0.45); }

.rq-empty-state { text-align: center; padding: 3rem 2rem; background: transparent; border: 1px dashed var(--hair-2); border-radius: 14px; margin: 1.5rem 0; }
.rq-empty-icon { display: none; }
.rq-empty-title { font-family: 'Newsreader', Georgia, serif; font-size: 1.4rem; font-weight: 600; color: var(--ink); margin-bottom: 0.5rem; }
.rq-empty-desc { color: var(--ink-3); font-size: 1rem; max-width: 52ch; margin: 0 auto; line-height: 1.55; }

.rq-warning-box { background: #FBF1DC; color: #6B4208; border-radius: 10px; padding: 0.95rem 1.2rem; font-weight: 600; margin-bottom: 1.1rem; font-size: 0.95rem; }

/* native controls */
.stButton > button { border-radius: 10px !important; font-weight: 600 !important; border: 1px solid var(--hair-2) !important;
    background: var(--surface) !important; color: var(--ink) !important; transition: border-color 0.2s var(--ease), background 0.2s var(--ease) !important; }
.stButton > button:hover { border-color: var(--navy) !important; background: #FBFAF6 !important; }
.stButton > button[kind="primary"] { background: var(--navy) !important; color: #FFFFFF !important; border-color: var(--navy) !important; }
.stButton > button[kind="primary"]:hover { background: #1C2E55 !important; }
[data-testid="stMetricValue"] { font-family: 'Newsreader', Georgia, serif; font-weight: 600; font-variant-numeric: tabular-nums; }
[data-testid="stMetricLabel"] { color: var(--ink-3); }
[data-testid="stTextArea"] textarea { border-radius: 12px; background: var(--surface); }
[data-testid="stDataFrame"] { border: 1px solid var(--hair); border-radius: 12px; overflow: hidden; }
hr { border-color: var(--hair) !important; }

@media (max-width: 640px) {
    .app-header { padding: 1.2rem 1.2rem; }
    .app-title { font-size: 1.7rem !important; }
    .block-container { padding-left: 1rem; padding-right: 1rem; }
}
@media (prefers-reduced-motion: reduce) { .pulse-dot { animation: none; } }
</style>
"""


def get_severity_style(severity_label: str) -> Dict[str, str]:
    """Return styling tokens for a given severity label with safe fallback."""
    clean_label = str(severity_label).upper().strip() if severity_label else "LOW"
    return SEVERITY_COLORS.get(clean_label, SEVERITY_COLORS["LOW"])


def get_incident_type_meta(incident_type: str) -> Dict[str, str]:
    """Return icon and human-readable name for an incident type."""
    clean_type = str(incident_type).upper().strip() if incident_type else "NON_EMERGENCY"
    return INCIDENT_TYPE_META.get(
        clean_type,
        {"icon": "⚠️", "name": clean_type.replace("_", " ").title(), "default_color": "#64748B"}
    )
