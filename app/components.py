"""
ResQPulse AI — Reusable UI Components
Provides styled components for Alert Cards, Attention Heatmaps, Incident Maps,
Queue Rows, Severity Badges, and Metrics tables with enterprise mission-control aesthetics.
"""

import html
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import streamlit as st
import folium
from streamlit_folium import st_folium

from app.styles import (
    SEVERITY_COLORS,
    INCIDENT_TYPE_META,
    SDG_META,
    RESPONDER_ICONS,
    get_severity_style,
    get_incident_type_meta,
)


def render_header():
    """Renders the master command-center header with live status beacon."""
    st.markdown(
        """
        <div class="app-header">
            <div class="header-top-row">
                <div>
                    <h1 class="app-title">🚨 ResQPulse AI</h1>
                    <p class="app-tagline">Transforming emergency reports into structured, actionable alerts.</p>
                </div>
                <div class="system-beacon">
                    <span class="pulse-dot"></span>
                    <span>112 ERSS • TRIAGE ENGINE ACTIVE</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_severity_pill(severity_label: str, severity_score: Optional[float] = None) -> str:
    """Return HTML for a styled severity pill with crisp typography."""
    clean_label = str(severity_label).upper().strip() if severity_label else "LOW"
    style = get_severity_style(clean_label)
    score_text = f" • {severity_score:.1f}" if severity_score is not None else ""
    return (
        f'<span class="rq-badge" style="background-color: {style["badge_bg"]}; color: {style["badge_text"]};">'
        f'{clean_label}{score_text}</span>'
    )


def render_empty_state(title: str, description: str, icon: str = "📋"):
    """Render a clean, friendly empty state container."""
    st.markdown(
        f"""
        <div class="rq-empty-state">
            <div class="rq-empty-icon">{icon}</div>
            <div class="rq-empty-title">{html.escape(title)}</div>
            <div class="rq-empty-desc">{html.escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_non_emergency_card(alert: Dict[str, Any]):
    """Render calm, neutral card for NON_EMERGENCY alerts."""
    summary = alert.get("summary") or "No emergency situation detected in this report."
    confidence = alert.get("type_confidence")
    conf_str = f"{confidence * 100:.1f}%" if isinstance(confidence, (int, float)) else "N/A"
    latency = alert.get("latency_ms", "N/A")

    st.markdown(
        f"""
        <div class="rq-card-neutral">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.85rem;">
                <div style="display: flex; align-items: center; gap: 0.65rem;">
                    <span style="font-size: 1.6rem;">ℹ️</span>
                    <span style="font-size: 1.4rem; font-weight: 800; color: #1E293B;">No emergency detected</span>
                </div>
                <span class="rq-badge" style="background-color: #64748B; color: #FFFFFF;">NON-EMERGENCY</span>
            </div>
            <p style="font-size: 1.1rem; color: #334155; margin: 0.5rem 0 1.25rem 0; line-height: 1.6;">
                {html.escape(summary)}
            </p>
            <div style="display: flex; flex-wrap: wrap; gap: 1.5rem; font-size: 0.9rem; color: #475569; border-top: 1px solid #CBD5E1; padding-top: 0.9rem;">
                <span><strong>Classification Confidence:</strong> {conf_str}</span>
                <span><strong>Severity:</strong> 1.0 (Non-urgent Inquiry / Non-emergency)</span>
                <span><strong>Status:</strong> DISMISSED (Filtered out of priority queue)</span>
                <span><strong>Inference Latency:</strong> {latency} ms</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Download JSON button
    st.download_button(
        label="📥 Download Alert JSON",
        data=json.dumps(alert, indent=2),
        file_name=f"{alert.get('alert_id', 'alert')}.json",
        mime="application/json",
        key=f"dl_non_emerg_{alert.get('alert_id', 'none')}",
    )


def render_alert_card(alert: Dict[str, Any]):
    """
    Renders structured alert card with all documented schema fields:
    incident_type, severity bar, location, people affected, injuries, hazards,
    summary, responders, SDG badges, confidence, and latency.
    """
    if not alert:
        render_empty_state("No alert generated yet", "Submit a report or choose a demo sample to view the structured alert.")
        return

    # Check for NON_EMERGENCY
    incident_type = alert.get("incident_type", "UNKNOWN")
    is_emergency = alert.get("is_emergency", True)
    if incident_type == "NON_EMERGENCY" or not is_emergency:
        render_non_emergency_card(alert)
        return

    severity_label = alert.get("severity_label", "LOW")
    severity = alert.get("severity", 1.0)
    type_meta = get_incident_type_meta(incident_type)
    sev_style = get_severity_style(severity_label)

    # Location handling
    loc_data = alert.get("location")
    if isinstance(loc_data, dict):
        loc_text = loc_data.get("text") or "Location unavailable"
        lat = loc_data.get("lat")
        lon = loc_data.get("lon")
        geocoded = loc_data.get("geocoded", False)
    elif isinstance(loc_data, str) and loc_data.strip():
        loc_text = loc_data.strip()
        lat, lon, geocoded = None, None, False
    else:
        loc_text = "Location unavailable"
        lat, lon, geocoded = None, None, False

    coords_badge = (
        f'<span class="rq-chip rq-chip-responder" style="font-size: 0.75rem; font-family: monospace;">📍 {lat:.4f}, {lon:.4f}</span>'
        if (geocoded and lat is not None and lon is not None)
        else '<span class="rq-chip" style="background:#F1F5F9; color:#64748B; font-size:0.75rem;">Ungeocoded</span>'
    )

    people_affected = alert.get("people_affected")
    people_str = str(people_affected) if people_affected is not None else "Unknown"

    injuries = alert.get("injuries") or []
    hazards = alert.get("hazards") or []
    responders = alert.get("responders") or []
    sdg_targets = alert.get("sdg_targets") or []
    summary = alert.get("summary") or "No summary provided."
    confidence = alert.get("type_confidence")
    conf_str = f"{confidence * 100:.1f}%" if isinstance(confidence, (int, float)) else "N/A"
    latency = alert.get("latency_ms", "N/A")
    alert_id = alert.get("alert_id", "RQP-000000")

    # Progress percentage for severity (1.0 to 5.0 scale -> 0% to 100%)
    sev_num = float(severity) if isinstance(severity, (int, float)) else 1.0
    sev_pct = max(0, min(100, int(((sev_num - 1.0) / 4.0) * 100)))

    # Main Card Container with custom border color according to severity
    card_border_class = f"rq-card-{severity_label.lower()}"
    st.markdown(
        f"""
        <div class="rq-card {card_border_class}" style="background: {sev_style.get('gradient', sev_style['bg'])};">
            <!-- Top bar: Alert ID, Type, and Severity -->
            <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; margin-bottom: 1rem; gap: 0.6rem;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <span style="font-size: 2.2rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));">{type_meta['icon']}</span>
                    <div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #0F172A; letter-spacing: -0.02em;">{type_meta['name']}</div>
                        <div style="font-size: 0.85rem; color: #475569; font-family: 'JetBrains Mono', monospace; font-weight: 600;">INCIDENT ID: {alert_id}</div>
                    </div>
                </div>
                <div>
                    <span class="rq-badge" style="background-color: {sev_style['badge_bg']}; color: {sev_style['badge_text']}; font-size: 1rem; padding: 0.45rem 1.1rem; box-shadow: 0 4px 10px {sev_style.get('glow', 'rgba(0,0,0,0.1)')};">
                        {severity_label} • {sev_num:.1f} / 5.0
                    </span>
                </div>
            </div>

            <!-- Severity visual bar -->
            <div style="margin-bottom: 1.4rem;">
                <div style="display: flex; justify-content: space-between; font-size: 0.82rem; color: #475569; font-weight: 700; margin-bottom: 0.35rem; text-transform: uppercase; letter-spacing: 0.04em;">
                    <span>Continuous Severity Gauge (1.0 — 5.0)</span>
                    <span>Level {sev_num:.1f} ({severity_label})</span>
                </div>
                <div style="background-color: rgba(203, 213, 225, 0.6); border-radius: 9999px; height: 12px; overflow: hidden; box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);">
                    <div style="background: {sev_style['bar_color']}; height: 100%; width: {sev_pct}%; transition: width 0.4s ease; border-radius: 9999px;"></div>
                </div>
            </div>

            <!-- Summary block -->
            <div style="background: #FFFFFF; border: 1px solid rgba(226, 232, 240, 0.9); border-radius: 10px; padding: 1.15rem; margin-bottom: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size: 0.78rem; font-weight: 800; text-transform: uppercase; color: #64748B; margin-bottom: 0.4rem; letter-spacing: 0.06em;">Triage Incident Summary</div>
                <div style="font-size: 1.15rem; font-weight: 600; color: #1E293B; line-height: 1.6;">{html.escape(summary)}</div>
            </div>

            <!-- Stat Boxes Grid -->
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 1rem; margin-bottom: 1rem;">
                <!-- Location -->
                <div class="rq-stat-box">
                    <div class="rq-stat-label">📍 Incident Location</div>
                    <div style="font-size: 1.02rem; font-weight: 700; color: #0F172A; margin: 0.2rem 0 0.4rem 0;">{html.escape(loc_text)}</div>
                    <div>{coords_badge}</div>
                </div>

                <!-- People Affected -->
                <div class="rq-stat-box">
                    <div class="rq-stat-label">👥 Casualties / At Risk</div>
                    <div class="rq-stat-val" style="color: {'#DC2626' if (isinstance(people_affected, int) and people_affected > 0) else '#0F172A'};">
                        {people_str}
                    </div>
                </div>

                <!-- Confidence -->
                <div class="rq-stat-box">
                    <div class="rq-stat-label">🎯 Model Confidence</div>
                    <div class="rq-stat-val">{conf_str}</div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.2rem;">DistilBERT Multi-task</div>
                </div>

                <!-- Latency -->
                <div class="rq-stat-box">
                    <div class="rq-stat-label">⚡ Inference Latency</div>
                    <div class="rq-stat-val">{latency} <span style="font-size: 0.9rem; font-weight: 600; color: #64748B;">ms</span></div>
                    <div style="font-size: 0.78rem; color: #64748B; margin-top: 0.2rem;">Flan-T5 + DistilBERT</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Detailed Chips and Badges in two columns
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🚑 Recommended Responders")
        if responders:
            resp_html = "".join(
                [f'<span class="rq-chip rq-chip-responder">{RESPONDER_ICONS.get(r, html.escape(r))}</span>' for r in responders]
            )
            st.markdown(resp_html, unsafe_allow_html=True)
        else:
            st.info("No emergency responders assigned.")

        st.markdown("#### 🎯 UN SDG Target Alignment")
        if sdg_targets:
            sdg_html = "".join(
                [
                    f'<span class="rq-chip rq-chip-sdg" title="{SDG_META.get(str(t), {}).get("desc", "")}">'
                    f'🌱 <strong>{SDG_META.get(str(t), {}).get("label", f"SDG {t}")}</strong>: {SDG_META.get(str(t), {}).get("title", "")}'
                    f'</span>'
                    for t in sdg_targets
                ]
            )
            st.markdown(sdg_html, unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#64748B; font-size:0.9rem;">None specified</span>', unsafe_allow_html=True)

    with c2:
        st.markdown("#### 🩹 Extracted Injuries / Medical Needs")
        if injuries:
            inj_html = "".join(
                [f'<span class="rq-chip rq-chip-injury">⚠️ {html.escape(str(i))}</span>' for i in injuries]
            )
            st.markdown(inj_html, unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#64748B; font-size:0.95rem;">None reported in call transcript</span>', unsafe_allow_html=True)

        st.markdown("#### ⚠️ Environmental / Situational Hazards")
        if hazards:
            haz_html = "".join(
                [f'<span class="rq-chip rq-chip-hazard">🔥 {html.escape(str(h))}</span>' for h in hazards]
            )
            st.markdown(haz_html, unsafe_allow_html=True)
        else:
            st.markdown('<span style="color:#64748B; font-size:0.95rem;">None reported in call transcript</span>', unsafe_allow_html=True)

    st.markdown("---")

    # JSON Download Button
    st.download_button(
        label="📥 Download Structured Alert JSON",
        data=json.dumps(alert, indent=2),
        file_name=f"{alert_id}.json",
        mime="application/json",
        key=f"dl_alert_{alert_id}",
    )


def render_attention_heatmap(alert: Dict[str, Any]):
    """
    Renders the report text with attention heatmap highlights.
    Attention format: alert.explanation.attention = [[word, score], ...]
    Clamps scores to 0.0 - 1.0, escapes HTML, preserves word order.
    Displays required disclaimer note.
    """
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

    st.markdown("### 🔍 Model Interpretability & Attention Weights")
    st.caption("Inspect token-level attention rollout from DistilBERT multi-task self-attention layers.")

    # Attention Legend
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem; font-size: 0.85rem; color: #475569;">
            <span><strong>Attention Intensity:</strong></span>
            <span style="display: inline-flex; align-items: center; gap: 0.25rem;">
                <span style="display: inline-block; width: 14px; height: 14px; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(220, 38, 38, 0.3); border-radius: 3px;"></span>
                <span>Low (0.0 - 0.4)</span>
            </span>
            <span style="display: inline-flex; align-items: center; gap: 0.25rem;">
                <span style="display: inline-block; width: 14px; height: 14px; background: rgba(239, 68, 68, 0.55); border: 1px solid rgba(220, 38, 38, 0.6); border-radius: 3px;"></span>
                <span>Moderate (0.4 - 0.7)</span>
            </span>
            <span style="display: inline-flex; align-items: center; gap: 0.25rem;">
                <span style="display: inline-block; width: 14px; height: 14px; background: rgba(220, 38, 38, 0.95); border: 1px solid #B91C1C; border-radius: 3px;"></span>
                <span>High Focus (0.7 - 1.0)</span>
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    spans = []
    for item in attention:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        word, score = item[0], item[1]
        try:
            val = float(score)
        except (ValueError, TypeError):
            val = 0.0

        # Clamp score between 0.0 and 1.0
        clamped_score = max(0.0, min(1.0, val))

        # Color: vivid red / coral highlight with opacity proportional to score
        alpha = max(0.08, min(0.96, clamped_score * 0.95))
        # Ensure high contrast text
        text_color = "#FFFFFF" if alpha > 0.58 else "#0F172A"
        border_color = f"rgba(220, 38, 38, {max(0.2, alpha)})"
        bg_color = f"rgba(239, 68, 68, {alpha:.2f})"

        escaped_word = html.escape(str(word))
        span_html = (
            f'<span class="heatmap-token" '
            f'style="background-color: {bg_color}; color: {text_color}; border: 1px solid {border_color};" '
            f'title="Token: \'{escaped_word}\' • Attention Weight: {clamped_score:.3f}">{escaped_word}</span>'
        )
        spans.append(span_html)

    if not spans:
        st.info("No tokens were available for attention visualization.")
        return

    # Render HTML in container
    heatmap_html = f'<div class="heatmap-container">{" ".join(spans)}</div>'
    st.markdown(heatmap_html, unsafe_allow_html=True)

    # EXACT MANDATORY EXPLANATORY NOTE
    st.markdown(
        '<div class="heatmap-note"><span>ℹ️</span> <span>Highlighted words are what the model focused on. This is an indicator, not proof.</span></div>',
        unsafe_allow_html=True,
    )

    # Display type probability distribution if present
    probs = alert.get("type_probs")
    if isinstance(probs, dict) and probs:
        st.markdown("#### Incident-Type Class Probabilities")
        sorted_probs = sorted(probs.items(), key=lambda x: x[1], reverse=True)
        prob_cols = st.columns(min(len(sorted_probs), 4))
        for idx, (t, p) in enumerate(sorted_probs[:4]):
            with prob_cols[idx % len(prob_cols)]:
                meta = get_incident_type_meta(t)
                st.metric(label=f"{meta['icon']} {t}", value=f"{p * 100:.1f}%")


def render_incident_map(alerts: List[Dict[str, Any]]):
    """
    Renders Folium incident map for all geocoded alerts.
    Skips alerts with geocoded: false, missing coords, invalid/out-of-range coords.
    """
    mappable_alerts = []
    for a in alerts:
        loc = a.get("location")
        if not isinstance(loc, dict):
            continue
        if loc.get("geocoded") is False:
            continue
        lat = loc.get("lat")
        lon = loc.get("lon")
        if lat is None or lon is None:
            continue
        try:
            flat = float(lat)
            flon = float(lon)
        except (ValueError, TypeError):
            continue
        # Coordinate bounds check
        if not (-90.0 <= flat <= 90.0 and -180.0 <= flon <= 180.0):
            continue
        mappable_alerts.append((a, flat, flon))

    if not mappable_alerts:
        render_empty_state("No mappable incidents", "None of the active alerts have valid geocoded coordinates to display on the map.", icon="🗺️")
        return

    # Calculate map center (average of coordinates or default to first)
    avg_lat = sum(flat for _, flat, _ in mappable_alerts) / len(mappable_alerts)
    avg_lon = sum(flon for _, _, flon in mappable_alerts) / len(mappable_alerts)

    # Create Folium Map with OpenStreetMap
    m = folium.Map(
        location=[avg_lat, avg_lon],
        zoom_start=7 if len(mappable_alerts) > 1 else 10,
        tiles="OpenStreetMap",
    )

    for alert, flat, flon in mappable_alerts:
        sev_label = alert.get("severity_label", "LOW")
        sev_val = alert.get("severity", 1.0)
        inc_type = alert.get("incident_type", "INCIDENT")
        summary = alert.get("summary", "Emergency incident")
        alert_id = alert.get("alert_id", "RQP")
        status = alert.get("status", "NEW")
        style = get_severity_style(sev_label)
        meta = get_incident_type_meta(inc_type)

        # Popup HTML
        popup_html = f"""
        <div style="font-family: 'Plus Jakarta Sans', sans-serif; min-width: 220px;">
            <div style="font-weight: 800; font-size: 14px; margin-bottom: 4px; color: #0F172A;">
                {meta['icon']} {inc_type} <span style="font-family: monospace; font-size: 11px; color: #64748B;">[{alert_id}]</span>
            </div>
            <div style="margin-bottom: 6px;">
                <span style="background-color: {style['badge_bg']}; color: white; padding: 2px 7px; border-radius: 9999px; font-size: 11px; font-weight: bold;">
                    {sev_label} • {sev_val:.1f}
                </span>
                <span style="background-color: #E2E8F0; color: #334155; padding: 2px 7px; border-radius: 9999px; font-size: 11px; margin-left: 4px; font-weight: 600;">
                    {status}
                </span>
            </div>
            <div style="font-size: 12px; color: #334155; margin-top: 6px; line-height: 1.4;">{html.escape(summary)}</div>
        </div>
        """

        folium.Marker(
            location=[flat, flon],
            popup=folium.Popup(popup_html, max_width=320),
            tooltip=f"{meta['icon']} {inc_type} ({sev_label}) - {alert_id}",
            icon=folium.Icon(color=style["map_color"], icon="info-sign"),
        ).add_to(m)

    st_folium(m, width="100%", height=460)
