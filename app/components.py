"""
ResQPulse AI — UI components: top bar, alert card, severity ruler, attention heatmap, queue rows, incident map.
All user text is HTML-escaped. Multi-line HTML goes through _flat() so Markdown never turns it into a code block.
"""

import html
import json
import re
from typing import Any, Dict, List, Optional

import folium
import streamlit as st
from streamlit_folium import st_folium

from app.styles import (
    RESPONDER_ICONS,
    SDG_META,
    get_incident_type_meta,
    get_severity_style,
)

BRAND_MARK = (
    '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true">'
    '<rect width="32" height="32" rx="9" fill="#141414"/>'
    '<path d="M5 17h5l2.6-7 4.4 14 3.4-9.5 1.8 2.5H27" stroke="#FFCC00" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>'
    "</svg>"
)


def _flat(markup: str) -> str:
    """Collapse an HTML snippet to lines with no indentation, blank lines or comments.
    Markdown ends an HTML block at a blank line and turns 4-space-indented lines into a code block,
    which is how the alert card used to show its own source code."""
    markup = re.sub(r"<!--.*?-->", "", markup, flags=re.S)
    return "\n".join(line.strip() for line in markup.splitlines() if line.strip())


def _md(markup: str) -> None:
    st.markdown(_flat(markup), unsafe_allow_html=True)


# ---------------------------------------------------------------- chrome
def render_rail_brand() -> None:
    _md(f'<div class="rail-brand">{BRAND_MARK}<b>ResQPulse AI</b></div>')


def render_header(mock_mode: bool = False, screen: str = "") -> None:
    """Slim top bar: where you are, and whether the real models are answering."""
    pill = ('<span class="status-pill"><span class="status-dot"></span>Mock data</span>' if mock_mode
            else '<span class="status-pill live"><span class="status-dot"></span>Live · real models</span>')
    crumb = f"Dispatch console <span>/</span> <b>{html.escape(screen)}</b>" if screen else "Dispatch console"
    _md(f'<div class="topbar"><div class="topbar-crumb">{crumb}</div>{pill}</div>')


def render_page_title(title: str, lede: str) -> None:
    st.markdown(f"## {title}")
    _md(f'<p class="page-lede">{html.escape(lede)}</p>')


# ---------------------------------------------------------------- small pieces
def render_severity_pill(severity_label: str, severity_score: Optional[float] = None) -> str:
    """HTML for a severity pill."""
    clean_label = str(severity_label).upper().strip() if severity_label else "LOW"
    style = get_severity_style(clean_label)
    score_text = f" {severity_score:.1f}" if isinstance(severity_score, (int, float)) else ""
    return (f'<span class="sev-pill" style="background:{style["badge_bg"]};color:{style["badge_text"]};">'
            f'{html.escape(clean_label.replace("_", " "))}{score_text}</span>')


def render_severity_ruler(severity: Any, severity_label: str, mini: bool = False) -> str:
    """The signature: five cells for severity 1 to 5, filled up to the score."""
    try:
        sev = max(1.0, min(5.0, float(severity)))
    except (TypeError, ValueError):
        sev = 1.0
    colour = get_severity_style(severity_label)["bar_color"]
    cells = []
    for i in range(5):                                   # cell i covers severity i+1 (a score of 3.4 fills 3 cells and 40% of the 4th)
        fill = max(0.0, min(1.0, sev - i))
        cells.append(f'<span class="ruler-cell"><i style="width:{fill * 100:.0f}%;background:{colour};"></i></span>')
    return (f'<div class="ruler{" mini" if mini else ""}" role="img" aria-label="Severity {sev:.1f} of 5">'
            f'<div class="ruler-cells">{"".join(cells)}</div>'
            f'<div class="ruler-val">{sev:.1f}<span> / 5</span></div></div>')


def render_empty_state(title: str, description: str, icon: Optional[str] = None) -> None:
    """Empty state. `icon` is accepted for compatibility and ignored."""
    _md(f'<div class="empty"><div class="empty-title">{html.escape(title)}</div>'
        f'<div class="empty-desc">{html.escape(description)}</div></div>')


def _tags(items: List[str], kind: str) -> str:
    return "".join(f'<span class="tag {kind}"><i></i>{html.escape(str(x))}</span>' for x in items)


# ---------------------------------------------------------------- alert card
def render_non_emergency_card(alert: Dict[str, Any]) -> None:
    """Calm, neutral card for NON_EMERGENCY alerts."""
    summary = alert.get("summary") or "No emergency situation detected in this report."
    confidence = alert.get("type_confidence")
    conf_str = f"{confidence * 100:.1f}%" if isinstance(confidence, (int, float)) else "N/A"
    latency = alert.get("latency_ms", "N/A")
    _md(f"""
    <div class="panel">
      <div class="calm-head">
        <div class="calm-title">No emergency detected</div>
        {render_severity_pill("NON_EMERGENCY")}
      </div>
      <p class="alert-summary" style="margin:0.9rem 0 0;">{html.escape(summary)}</p>
      <div class="calm-facts">
        <div class="meta-row"><div class="field-label">Confidence</div><div class="meta-val">{conf_str}</div></div>
        <div class="meta-row"><div class="field-label">Severity</div><div class="meta-val">1.0, not urgent</div></div>
        <div class="meta-row"><div class="field-label">Status</div><div class="meta-val">Dismissed, kept out of the queue</div></div>
        <div class="meta-row"><div class="field-label">Response time</div><div class="meta-val">{html.escape(str(latency))} ms</div></div>
      </div>
    </div>
    """)
    st.download_button(
        label="Download alert JSON",
        data=json.dumps(alert, indent=2),
        file_name=f"{alert.get('alert_id', 'alert')}.json",
        mime="application/json",
        key=f"dl_non_emerg_{alert.get('alert_id', 'none')}",
    )


def render_alert_card(alert: Dict[str, Any]) -> None:
    """Structured alert in a Kaggle-style layout: main column (summary, severity, injuries, hazards) and a meta column."""
    if not alert:
        render_empty_state("No alert generated yet", "Submit a report or choose a demo sample to view the structured alert.")
        return

    incident_type = alert.get("incident_type", "UNKNOWN")
    if incident_type == "NON_EMERGENCY" or not alert.get("is_emergency", True):
        render_non_emergency_card(alert)
        return

    severity_label = str(alert.get("severity_label", "LOW"))
    severity = alert.get("severity", 1.0)
    type_name = get_incident_type_meta(incident_type)["name"]

    loc_data = alert.get("location")
    lat = lon = None
    geocoded = False
    if isinstance(loc_data, dict):
        loc_text = loc_data.get("text") or "Location unavailable"
        lat, lon, geocoded = loc_data.get("lat"), loc_data.get("lon"), loc_data.get("geocoded", False)
    elif isinstance(loc_data, str) and loc_data.strip():
        loc_text = loc_data.strip()
    else:
        loc_text = "Location unavailable"
    coords = (f'<div class="coords">{lat:.4f}, {lon:.4f}</div>'
              if geocoded and isinstance(lat, (int, float)) and isinstance(lon, (int, float))
              else '<div class="coords">Not on the map</div>')

    people = alert.get("people_affected")
    people_str = str(people) if people is not None else "Unknown"
    injuries = alert.get("injuries") or []
    hazards = alert.get("hazards") or []
    responders = alert.get("responders") or []
    sdg_targets = alert.get("sdg_targets") or []
    summary = alert.get("summary") or "No summary provided."
    confidence = alert.get("type_confidence")
    conf_str = f"{confidence * 100:.1f}" if isinstance(confidence, (int, float)) else "N/A"
    latency = alert.get("latency_ms", "N/A")
    alert_id = str(alert.get("alert_id", "RQP-000000"))
    status = str(alert.get("status", "NEW"))
    source = str((alert.get("input") or {}).get("source", "text")) if isinstance(alert.get("input"), dict) else "text"

    dup_of = alert.get("duplicate_of")
    dup = (f'<div class="dup-flag">Possible duplicate of <b>{html.escape(str(dup_of))}</b>. Merge or dismiss.</div>'
           if dup_of else "")
    inj = _tags(injuries, "injury") if injuries else '<span class="muted">None reported</span>'
    haz = _tags(hazards, "hazard") if hazards else '<span class="muted">None reported</span>'
    resp = ("".join(f'<span class="tag responder">{html.escape(RESPONDER_ICONS.get(r, str(r)))}</span>' for r in responders)
            if responders else '<span class="muted">None assigned</span>')
    sdg = ("".join(
        f'<span class="tag sdg" title="{html.escape(SDG_META.get(str(t), {}).get("desc", ""))}">'
        f'<b>{html.escape(str(t))}</b>{html.escape(SDG_META.get(str(t), {}).get("title", ""))}</span>'
        for t in sdg_targets) if sdg_targets else '<span class="muted">None</span>')

    _md(f"""
    <div class="panel">
      <div class="alert-head">
        <div>
          <div class="alert-title">{html.escape(type_name)}</div>
          <div class="alert-sub">{html.escape(alert_id)} · {html.escape(source)} report</div>
        </div>
        <div class="q-right">{render_severity_pill(severity_label, severity if isinstance(severity, (int, float)) else None)}<span class="status-tag">{html.escape(status)}</span></div>
      </div>
      <div class="alert-grid">
        <div>
          {dup}
          <p class="alert-summary">{html.escape(summary)}</p>
          <div class="field-label">Severity</div>
          {render_severity_ruler(severity, severity_label)}
          <div class="section-gap"><div class="field-label">Injuries and medical needs</div>{inj}</div>
          <div class="section-gap"><div class="field-label">Hazards</div>{haz}</div>
          <div class="section-gap"><div class="field-label">Recommended responders</div>{resp}</div>
        </div>
        <aside>
          <div class="meta-row"><div class="field-label">Location</div><div class="meta-val">{html.escape(loc_text)}</div>{coords}</div>
          <div class="meta-row"><div class="field-label">People affected</div><div class="meta-num">{html.escape(people_str)}</div></div>
          <div class="meta-row"><div class="field-label">Type confidence</div><div class="meta-num">{conf_str}<small>%</small></div></div>
          <div class="meta-row"><div class="field-label">Response time</div><div class="meta-num">{html.escape(str(latency))}<small> ms</small></div></div>
          <div class="meta-row"><div class="field-label">UN SDG targets</div>{sdg}</div>
        </aside>
      </div>
    </div>
    """)
    st.download_button(
        label="Download alert JSON",
        data=json.dumps(alert, indent=2),
        file_name=f"{alert_id}.json",
        mime="application/json",
        key=f"dl_alert_{alert_id}",
    )


# ---------------------------------------------------------------- explainability
def render_attention_heatmap(alert: Dict[str, Any]) -> None:
    """The report with each word shaded by attention (stretched within the report), plus the class probabilities."""
    if not alert:
        render_empty_state("No alert to explain", "Run an analysis on a report first to inspect model attention.")
        return
    explanation = alert.get("explanation")
    if not isinstance(explanation, dict):
        st.info("Attention explanation is not available for this alert.")
        return
    attention = explanation.get("attention")
    if not attention or not isinstance(attention, list):
        st.info("No attention token scores found for this alert.")
        return

    parsed = []
    for item in attention:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        try:
            val = float(item[1])
        except (ValueError, TypeError):
            val = 0.0
        parsed.append((item[0], max(0.0, min(1.0, val))))
    if not parsed:
        st.info("No tokens were available for attention visualization.")
        return

    # Attention-rollout scores sit close together (about 0.5 to 1.0), so colouring them directly makes every word dark.
    # Stretch them over the full range within this report; the tooltip still shows the raw weight.
    scores = [s for _, s in parsed]
    lo, hi = min(scores), max(scores)
    spans = []
    for word, score in parsed:
        shown = ((score - lo) / (hi - lo)) ** 1.5 if hi > lo else score
        alpha = max(0.06, min(1.0, shown))
        w = html.escape(str(word))
        spans.append(f'<span class="heat-tok" style="background-color: rgba(255, 204, 0, {alpha:.2f});" '
                     f'title="{w}: attention {score:.3f}">{w}</span>')

    _md('<div class="heat-legend">Less focus <span class="heat-ramp"></span> More focus</div>')
    st.markdown(f'<div class="heat">{" ".join(spans)}</div>', unsafe_allow_html=True)
    _md('<div class="heat-note">Highlighted words are what the model focused on. This is an indicator, not proof. '
        'Shading is relative within this report; hover a word for its raw attention weight.</div>')

    probs = alert.get("type_probs")
    if isinstance(probs, dict) and probs:
        st.markdown("### Incident type probabilities")
        rows = []
        for t, p in sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]:
            try:
                pv = float(p)
            except (TypeError, ValueError):
                continue
            rows.append(f'<div class="prob-row"><div class="prob-name">{html.escape(get_incident_type_meta(t)["name"])}</div>'
                        f'<div class="prob-bar"><i style="width:{pv * 100:.1f}%"></i></div>'
                        f'<div class="prob-val">{pv * 100:.1f}%</div></div>')
        _md(f'<div class="panel" style="padding:0.6rem 1.4rem;">{"".join(rows)}</div>')


# ---------------------------------------------------------------- queue
def render_queue_row(alert: Dict[str, Any]) -> None:
    """One alert in the dispatcher queue: type, ID, location, severity ruler, status, summary."""
    loc = alert.get("location")
    loc_text = (loc.get("text") if isinstance(loc, dict) else loc) or "Location unavailable"
    sev_label = str(alert.get("severity_label", "LOW"))
    severity = alert.get("severity", 1.0)
    dup_of = alert.get("duplicate_of")
    dup = (f'<span class="status-tag" style="color:#141414;border-color:#141414;">'
           f'Duplicate of {html.escape(str(dup_of))}</span>' if dup_of else "")
    _md(f"""
    <div class="q-row">
      <div class="q-top">
        <div>
          <span class="q-title">{html.escape(get_incident_type_meta(alert.get("incident_type", ""))["name"])}</span><span class="q-id">{html.escape(str(alert.get("alert_id", "")))}</span>
          <div class="q-loc">{html.escape(str(loc_text))}</div>
        </div>
        <div class="q-right">{render_severity_ruler(severity, sev_label, mini=True)}{render_severity_pill(sev_label)}<span class="status-tag">{html.escape(str(alert.get("status", "NEW")))}</span>{dup}</div>
      </div>
      <div class="q-sum">{html.escape(str(alert.get("summary") or "No summary provided."))}</div>
    </div>
    """)


def render_incident_map(alerts: List[Dict[str, Any]]) -> None:
    """Light map with one severity-coloured dot per geocoded alert. Skips alerts without valid coordinates."""
    mappable = []
    for a in alerts:
        loc = a.get("location")
        if not isinstance(loc, dict) or loc.get("geocoded") is False:
            continue
        try:
            flat, flon = float(loc.get("lat")), float(loc.get("lon"))
        except (TypeError, ValueError):
            continue
        if -90.0 <= flat <= 90.0 and -180.0 <= flon <= 180.0:
            mappable.append((a, flat, flon))

    if not mappable:
        render_empty_state("No incidents on the map yet", "Alerts appear here once their location has been geocoded.")
        return

    avg_lat = sum(p[1] for p in mappable) / len(mappable)
    avg_lon = sum(p[2] for p in mappable) / len(mappable)
    m = folium.Map(location=[avg_lat, avg_lon], zoom_start=7 if len(mappable) > 1 else 10, tiles="Esri.WorldGrayCanvas")
    for alert, flat, flon in mappable:
        sev_label = str(alert.get("severity_label", "LOW"))
        style = get_severity_style(sev_label)
        name = get_incident_type_meta(alert.get("incident_type", ""))["name"]
        alert_id = html.escape(str(alert.get("alert_id", "")))
        try:
            sev_num = float(alert.get("severity", 1.0))
        except (TypeError, ValueError):
            sev_num = 1.0
        popup = (f'<div style="font-family:Figtree,-apple-system,sans-serif;min-width:220px;">'
                 f'<div style="font-weight:600;font-size:14px;color:#141414;">{html.escape(name)}</div>'
                 f'<div style="font-family:monospace;font-size:11px;color:#6B6B68;margin:2px 0 6px;">{alert_id} · {html.escape(sev_label)} '
                 f'{sev_num:.1f} · {html.escape(str(alert.get("status", "NEW")))}</div>'
                 f'<div style="font-size:12px;color:#4D4D4D;line-height:1.4;">{html.escape(str(alert.get("summary", "")))}</div></div>')
        folium.CircleMarker(
            location=[flat, flon], radius=9, color="#FFFFFF", weight=2, fill=True,
            fill_color=style["badge_bg"], fill_opacity=0.95,
            popup=folium.Popup(popup, max_width=320), tooltip=f"{name} · {sev_label} · {alert_id}",
        ).add_to(m)
    st_folium(m, width="100%", height=440)
