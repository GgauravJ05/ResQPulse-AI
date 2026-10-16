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
        "border": "#DC2626",      # Vivid red border
        "badge_bg": "#DC2626",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "red",
        "bar_color": "linear-gradient(90deg, #EF4444 0%, #B91C1C 100%)",
        "gradient": "linear-gradient(135deg, #FEF2F2 0%, #FEE2E2 100%)",
        "glow": "rgba(220, 38, 38, 0.25)",
    },
    "HIGH": {
        "text": "#9A3412",        # Deep formal orange
        "bg": "#FFF7ED",          # Soft light orange tint
        "border": "#EA580C",      # Vivid orange border
        "badge_bg": "#EA580C",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "orange",
        "bar_color": "linear-gradient(90deg, #F97316 0%, #C2410C 100%)",
        "gradient": "linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%)",
        "glow": "rgba(234, 88, 12, 0.25)",
    },
    "MEDIUM": {
        "text": "#92400E",        # Deep formal amber
        "bg": "#FFFBEB",          # Soft light amber tint
        "border": "#D97706",      # Vivid amber border
        "badge_bg": "#D97706",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "beige",
        "bar_color": "linear-gradient(90deg, #F59E0B 0%, #B45309 100%)",
        "gradient": "linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%)",
        "glow": "rgba(217, 119, 6, 0.25)",
    },
    "LOW": {
        "text": "#166534",        # Deep formal green
        "bg": "#F0FDF4",          # Soft light green tint
        "border": "#16A34A",      # Vivid green border
        "badge_bg": "#16A34A",    # Solid badge fill
        "badge_text": "#FFFFFF",
        "map_color": "green",
        "bar_color": "linear-gradient(90deg, #22C55E 0%, #15803D 100%)",
        "gradient": "linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%)",
        "glow": "rgba(22, 163, 74, 0.25)",
    },
    "NON_EMERGENCY": {
        "text": "#334155",        # Formal neutral slate
        "bg": "#F8FAFC",          # Soft slate tint
        "border": "#64748B",      # Slate border
        "badge_bg": "#64748B",    # Neutral badge fill
        "badge_text": "#FFFFFF",
        "map_color": "gray",
        "bar_color": "linear-gradient(90deg, #94A3B8 0%, #475569 100%)",
        "gradient": "linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)",
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
        "default_color": "#EA580C",
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

# Formal Enterprise Command Center CSS
CUSTOM_CSS = """
<style>
/* Modern Enterprise Typography */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    letter-spacing: -0.01em;
}

code, pre, .mono {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Master Command-Center Header */
.app-header {
    background: linear-gradient(135deg, #090D16 0%, #111827 55%, #1A2234 100%);
    color: #FFFFFF;
    padding: 1.6rem 2.2rem;
    border-radius: 14px;
    margin-bottom: 1.75rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.08);
    position: relative;
    overflow: hidden;
    border-left: 6px solid #EF4444;
}

.app-header::after {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 320px;
    height: 100%;
    background: radial-gradient(circle at right, rgba(239, 68, 68, 0.12) 0%, transparent 70%);
    pointer-events: none;
}

.header-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1rem;
}

.app-title {
    font-size: 2.3rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    margin: 0;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}

.app-tagline {
    font-size: 1.05rem;
    font-weight: 400;
    color: #94A3B8;
    margin-top: 0.4rem;
    margin-bottom: 0;
}

/* Pulse Beacon */
.system-beacon {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.12);
    padding: 0.4rem 0.9rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #E2E8F0;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    backdrop-filter: blur(8px);
}

.pulse-dot {
    width: 9px;
    height: 9px;
    background-color: #10B981;
    border-radius: 50%;
    box-shadow: 0 0 0 rgba(16, 185, 129, 0.6);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
    }
    70% {
        box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
    }
}

/* Formal Enterprise Cards */
.rq-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05), 0 2px 6px -1px rgba(15, 23, 42, 0.02);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.rq-card-neutral {
    background: #F8FAFC;
    border: 1px solid #CBD5E1;
    border-left: 6px solid #64748B;
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.03);
}

/* Severity Accent Borders */
.rq-card-critical {
    border-left: 6px solid #DC2626 !important;
}

.rq-card-high {
    border-left: 6px solid #EA580C !important;
}

.rq-card-medium {
    border-left: 6px solid #D97706 !important;
}

.rq-card-low {
    border-left: 6px solid #16A34A !important;
}

/* Capsule Badges */
.rq-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.85rem;
    border-radius: 9999px;
    font-weight: 700;
    font-size: 0.85rem;
    letter-spacing: 0.03em;
    margin-right: 0.4rem;
    margin-bottom: 0.4rem;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

/* Formal Micro-Chips */
.rq-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0.35rem 0.75rem;
    border-radius: 7px;
    font-size: 0.85rem;
    font-weight: 600;
    margin: 0.25rem 0.35rem 0.25rem 0;
    letter-spacing: -0.01em;
}

.rq-chip-injury {
    background-color: #FEF2F2;
    color: #991B1B;
    border: 1px solid #FECACA;
}

.rq-chip-hazard {
    background-color: #FFFBEB;
    color: #92400E;
    border: 1px solid #FDE68A;
}

.rq-chip-responder {
    background-color: #EEF2FF;
    color: #3730A3;
    border: 1px solid #C7D2FE;
}

.rq-chip-sdg {
    background-color: #F0FDF4;
    color: #166534;
    border: 1px solid #BBF7D0;
    transition: all 0.2s ease;
}

.rq-chip-sdg:hover {
    border-color: #4ADE80;
    transform: translateY(-1px);
}

/* Attention Heatmap Command Display */
.heatmap-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.8rem;
    line-height: 2.5;
    font-size: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: inset 0 2px 4px rgba(15, 23, 42, 0.02);
}

.heatmap-token {
    display: inline-block;
    padding: 0.25rem 0.55rem;
    margin: 0.2rem 0.25rem;
    border-radius: 6px;
    font-weight: 600;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: default;
}

.heatmap-token:hover {
    transform: scale(1.08) translateY(-1px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.12);
}

.heatmap-note {
    font-size: 0.95rem;
    font-weight: 500;
    color: #334155;
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-left: 4px solid #475569;
    padding: 0.9rem 1.2rem;
    border-radius: 8px;
    margin-top: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Queue Card in Dashboard */
.queue-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    transition: all 0.2s ease;
}

.queue-card:hover {
    box-shadow: 0 8px 16px -2px rgba(15, 23, 42, 0.08);
    transform: translateY(-2px);
    border-color: #CBD5E1;
}

/* Empty State */
.rq-empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: #F8FAFC;
    border: 2px dashed #CBD5E1;
    border-radius: 14px;
    margin: 1.5rem 0;
}

.rq-empty-icon {
    font-size: 3.2rem;
    margin-bottom: 0.85rem;
}

.rq-empty-title {
    font-size: 1.35rem;
    font-weight: 700;
    color: #1E293B;
    margin-bottom: 0.5rem;
}

.rq-empty-desc {
    color: #64748B;
    font-size: 1rem;
    max-width: 520px;
    margin: 0 auto;
    line-height: 1.5;
}

/* Verification warning box */
.rq-warning-box {
    background-color: #FFFBEB;
    border: 1px solid #FCD34D;
    border-left: 6px solid #D97706;
    padding: 1rem 1.35rem;
    border-radius: 10px;
    color: #92400E;
    font-weight: 600;
    margin-bottom: 1.2rem;
    font-size: 0.95rem;
    box-shadow: 0 2px 4px rgba(217, 119, 6, 0.06);
}

/* KPI / Stat Mini Cards */
.rq-stat-box {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 1rem 1.1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}

.rq-stat-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.3rem;
}

.rq-stat-val {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0F172A;
}

/* Buttons Enhancement */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
}

.stButton > button:hover {
    transform: translateY(-1px);
}
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
