"""
ResQPulse AI — Streamlit Frontend Application
Entry point for ResQPulse AI: AI-powered emergency report processing system.
Five Screens:
1. REPORT INPUT (text, voice, demo samples, transcript verification)
2. ALERT CARD (structured alert, severity, location, responders, SDG badges, JSON download)
3. EXPLAIN (attention heatmap visualization with required indicator note)
4. DISPATCHER DASHBOARD (live severity-sorted alert queue and Folium incident map)
5. METRICS PAGE (baseline vs DistilBERT, severity regression, Flan-T5 extraction, confusion matrices)
"""

import html
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd
import streamlit as st

# Local modules
from app.api_client import (
    API_URL,
    DEFAULT_API_URL,
    BackendNotReachableError,
    APIResponseError,
    ResQPulseAPIError,
    check_health,
    get_alert,
    get_alerts,
    update_alert,
    transcribe_audio,
    get_metrics,
    _load_json_file,
    DEMO_SAMPLES_PATH,
    MOCK_ALERT_PATH,
)
from app.styles import (
    CUSTOM_CSS,
    SEVERITY_COLORS,
    INCIDENT_TYPE_META,
    get_severity_style,
    get_incident_type_meta,
)
from app.components import (
    render_header,
    render_rail_brand,
    render_page_title,
    render_alert_card,
    render_attention_heatmap,
    render_incident_map,
    render_empty_state,
    render_queue_row,
)

# -----------------------------------------------------------------------------
# Streamlit App Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ResQPulse AI · Dispatch console",
    page_icon=str(Path(__file__).resolve().parent / "static" / "favicon.png"),
    layout="wide",
    initial_sidebar_state="auto",
)

# Inject custom CSS
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Session State Initialization
# -----------------------------------------------------------------------------
if "mock_mode" not in st.session_state:
    # Start in Live mode when the backend answers (the real demo); fall back to Mock so the page still works without it.
    try:
        check_health(base_url=API_URL, timeout=2)
        st.session_state.mock_mode = False
    except Exception:
        st.session_state.mock_mode = True

if "api_url" not in st.session_state:
    st.session_state.api_url = API_URL

if "current_report_text" not in st.session_state:
    st.session_state.current_report_text = ""

if "current_alert" not in st.session_state:
    # Initialize with default mock alert from Section 6 of SCHEMA.md
    default_mock = _load_json_file(MOCK_ALERT_PATH)
    st.session_state.current_alert = default_mock

if "voice_transcript" not in st.session_state:
    st.session_state.voice_transcript = ""

if "voice_low_confidence" not in st.session_state:
    st.session_state.voice_low_confidence = False

if "voice_confidence" not in st.session_state:
    st.session_state.voice_confidence = None

if "report_source" not in st.session_state:
    st.session_state.report_source = "text"

if "queue_filter_status" not in st.session_state:
    st.session_state.queue_filter_status = "ALL"

# -----------------------------------------------------------------------------
# Sidebar Navigation and Global Controls
# -----------------------------------------------------------------------------
with st.sidebar:
    render_rail_brand()
    screen = st.radio(
        "Navigation Screens",
        options=[
            "Report Input",
            "Alert Card",
            "Attention Heatmap",
            "Dispatcher Dashboard",
            "Model Metrics",
        ],
        index=0,
        key="nav_screen_selection",
    )

    st.markdown("---")
    with st.expander("Backend settings", expanded=False):
        mock_choice = st.radio(
            "Data source",
            options=["Mock Mode (Offline Demo)", "Live Backend API"],
            index=0 if st.session_state.mock_mode else 1,
            help="Mock mode uses a stored sample alert and the demo reports, with no FastAPI server.",
        )
        st.session_state.mock_mode = (mock_choice == "Mock Mode (Offline Demo)")

        api_url_input = st.text_input(
            "Backend URL",
            value=st.session_state.api_url,
            help="FastAPI base URL. Default: http://localhost:8000",
        )
        st.session_state.api_url = api_url_input.rstrip("/")

        if st.button("Test connection", use_container_width=True):
            try:
                check_health(base_url=st.session_state.api_url)
                st.success("Backend online, models ready")
            except BackendNotReachableError as e:
                st.error(f"backend not reachable: {e}")
            except Exception as e:
                st.error(f"Connection error: {e}")

    st.markdown(
        '<div class="rail-foot">ResQPulse AI v1.0<br>GenHack · PS 15 EmergencyScribe</div>',
        unsafe_allow_html=True,
    )


# Render Global Header
render_header(mock_mode=st.session_state.mock_mode, screen=screen)


# =============================================================================
# SCREEN 1: REPORT INPUT
# =============================================================================
if screen == "Report Input":
    render_page_title(
        "Report an emergency",
        "Type a report, record a call or upload audio. ResQPulse returns a structured, prioritised alert in a few seconds.",
    )

    # Demo Samples Section
    demo_samples = _load_json_file(DEMO_SAMPLES_PATH) or []
    if demo_samples:
        st.markdown("### Try a sample report")
        st.caption("Each sample fills the report box below. Expected type and severity are shown on hover.")

        # Group samples into neat rows of buttons
        for i, sample in enumerate(demo_samples):
            if i % 3 == 0:
                cols = st.columns(3)               # one row of three at a time, so phones stack them in reading order
            col = cols[i % 3]
            sample_label = sample.get("label", f"Sample {i+1}")
            exp_type = sample.get("expected_type", "")
            exp_sev = sample.get("expected_severity", "")
            if col.button(sample_label, key=f"btn_sample_{i}", use_container_width=True,
                          help=f"Expected: {exp_type}, severity {exp_sev}"):
                st.session_state.current_report_text = sample.get("text", "")
                st.session_state.main_report_text_area = sample.get("text", "")
                st.session_state.report_source = "text"
                st.session_state.voice_transcript = ""
                st.session_state.voice_low_confidence = False
                st.session_state.voice_confidence = None
                st.rerun()

    # A transcript from the voice section below arrives on the next run; apply it before the text box is drawn
    if "pending_report_text" in st.session_state:
        pending = st.session_state.pop("pending_report_text")
        st.session_state.current_report_text = pending
        st.session_state.main_report_text_area = pending

    # Main Text Area
    st.markdown("### Report text")
    if st.session_state.voice_low_confidence:
        st.markdown(
            '<div class="warn"><b>Check the transcript.</b> Speech recognition was not confident on this audio. Fix any misheard words before analysing.</div>',
            unsafe_allow_html=True,
        )
    report_input = st.text_area(
        label="Type, paste or correct the transcript",
        value=st.session_state.current_report_text,
        height=140,
        max_chars=2200,
        help="Max 2,000 characters allowed per API schema.",
        key="main_report_text_area",
    )
    st.session_state.current_report_text = report_input

    # Character count and validation indicator
    char_count = len(report_input)
    if char_count > 2000:
        st.error(f"Input exceeds maximum limit of 2,000 characters (Current: {char_count}). Please shorten report.")
    elif char_count > 0:
        st.caption(f"{char_count} / 2,000 characters · source: {st.session_state.report_source}")

    # Analyze Button
    c_btn, c_info = st.columns([1, 3])
    with c_btn:
        analyze_clicked = st.button("Analyze Report", type="primary", use_container_width=True)

    if analyze_clicked:
        cleaned_text = report_input.strip()
        if not cleaned_text:
            st.warning("Report text cannot be empty. Please enter or record an emergency report.")
        elif len(cleaned_text) > 2000:
            st.error("Cannot analyze: Report text exceeds 2,000 characters.")
        else:
            with st.spinner("Analyzing emergency report with DistilBERT and Flan-T5..."):
                try:
                    alert = get_alert(
                        cleaned_text,
                        source=st.session_state.report_source,
                        transcript_confidence=st.session_state.voice_confidence,
                        mock_mode=st.session_state.mock_mode,
                        base_url=st.session_state.api_url,
                    )
                    st.session_state.current_alert = alert
                    st.success("Alert generated. Open Alert Card for the full breakdown.")
                    
                    # Quick Summary Preview below
                    
                    render_alert_card(alert)
                except BackendNotReachableError:
                    st.error("backend not reachable")
                except APIResponseError as e:
                    st.error(f"API Error: {e.message}")
                except Exception as e:
                    st.error(f"Analysis failed: {e}")


    # Audio Input Section
    st.markdown("### Or report by voice")
    audio_col1, audio_col2 = st.columns(2)

    with audio_col1:
        recorded_audio = st.audio_input("Record a call", key="mic_audio_input")

    with audio_col2:
        uploaded_audio = st.file_uploader(
            "Or upload a recording",
            type=["wav", "mp3", "m4a", "webm", "ogg", "oga", "opus", "mpeg", "mpga", "flac", "aac"],
            key="file_audio_input",
        )

    # Process Audio if captured
    active_audio_bytes = None
    audio_filename = "recorded_audio.wav"

    if recorded_audio is not None:
        active_audio_bytes = recorded_audio.read()
        audio_filename = "microphone.wav"
    elif uploaded_audio is not None:
        active_audio_bytes = uploaded_audio.read()
        audio_filename = uploaded_audio.name

    if active_audio_bytes:
        if st.button("Transcribe Audio Now", key="btn_transcribe_audio", type="secondary"):
            with st.spinner("Transcribing audio via Whisper ASR..."):
                try:
                    asr_res = transcribe_audio(
                        active_audio_bytes,
                        filename=audio_filename,
                        mock_mode=st.session_state.mock_mode,
                        base_url=st.session_state.api_url,
                    )
                    st.session_state.voice_transcript = asr_res.get("transcript", "")
                    st.session_state.voice_confidence = asr_res.get("confidence")
                    st.session_state.voice_low_confidence = asr_res.get("low_confidence", False)
                    st.session_state.pending_report_text = st.session_state.voice_transcript
                    st.session_state.report_source = "voice"
                    st.success(
                        f"Audio transcribed successfully ({asr_res.get('duration_s', 0):.1f}s, "
                        f"confidence: {asr_res.get('confidence', 0)*100:.1f}%)"
                    )
                    st.rerun()
                except BackendNotReachableError:
                    st.error("backend not reachable")
                except Exception as e:
                    st.error(f"Audio transcription failed: {e}")



# =============================================================================
# SCREEN 2: ALERT CARD
# =============================================================================
elif screen == "Alert Card":
    render_page_title("Alert", "The structured alert for the current report, with the evidence beside each field.")

    if not st.session_state.current_alert:
        render_empty_state(
            title="No alert available",
            description="Submit an emergency report on Report Input to generate and inspect the structured alert.",
        )
    else:
        render_alert_card(st.session_state.current_alert)


# =============================================================================
# SCREEN 3: EXPLAIN — ATTENTION HEATMAP
# =============================================================================
elif screen == "Attention Heatmap":
    render_page_title(
        "Why the model decided this",
        "Attention rollout from DistilBERT: the words that drove the incident type and severity, shaded by weight.",
    )

    if not st.session_state.current_alert:
        render_empty_state(
            title="No alert to explain",
            description="Submit an emergency report on Report Input to inspect its attention score breakdown.",
        )
    else:
        render_attention_heatmap(st.session_state.current_alert)


# =============================================================================
# SCREEN 4: DISPATCHER DASHBOARD
# =============================================================================
elif screen == "Dispatcher Dashboard":
    render_page_title(
        "Dispatcher queue",
        "Every open alert, most severe first, with its place on the map. Confirm, dispatch or dismiss each one.",
    )

    # Top Controls: Refresh and Status Filter
    ctrl_col1, ctrl_col2, _ = st.columns([1, 2, 2], vertical_alignment="bottom")
    with ctrl_col1:
        manual_refresh = st.button("Refresh", use_container_width=True)

    with ctrl_col2:
        status_filter = st.selectbox(
            "Status",
            options=["ALL", "NEW", "CONFIRMED", "DISPATCHED", "DISMISSED"],
            index=["ALL", "NEW", "CONFIRMED", "DISPATCHED", "DISMISSED"].index(st.session_state.queue_filter_status),
        )
        st.session_state.queue_filter_status = status_filter


    # Fetch alerts
    filter_arg = None if status_filter == "ALL" else status_filter
    alerts_data: List[Dict[str, Any]] = []
    fetch_error = False

    try:
        res = get_alerts(
            status=filter_arg,
            mock_mode=st.session_state.mock_mode,
            base_url=st.session_state.api_url,
        )
        alerts_data = res.get("alerts", [])
    except BackendNotReachableError:
        st.error("backend not reachable")
        fetch_error = True
    except Exception as e:
        st.error(f"Failed to fetch alerts: {e}")
        fetch_error = True

    if not fetch_error:
        # Command Center KPI Overview Ribbon
        n_total = len(alerts_data)
        n_critical = sum(1 for a in alerts_data if str(a.get("severity_label", "")).upper() == "CRITICAL")
        n_dispatched = sum(1 for a in alerts_data if a.get("status") == "DISPATCHED")
        n_geocoded = sum(
            1 for a in alerts_data
            if isinstance(a.get("location"), dict)
            and a.get("location", {}).get("geocoded")
            and a.get("location", {}).get("lat") is not None
        )

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(label="Alerts in queue", value=str(n_total))
        k2.metric(label="Critical", value=str(n_critical))
        k3.metric(label="Dispatched", value=str(n_dispatched))
        k4.metric(label="On the map", value=f"{n_geocoded} / {n_total}")

        st.markdown("### Incident map")
        render_incident_map(alerts_data)

        st.markdown(f"### Queue · {len(alerts_data)} alert{'s' if len(alerts_data) != 1 else ''}")

        if not alerts_data:
            render_empty_state(
                title="Queue is empty",
                description=f"No emergency alerts currently found with status filter: {status_filter}.",
            )
        else:
            # Render each alert in queue
            for alert in alerts_data:
                alert_id = alert.get("alert_id", "RQP-000")
                status = alert.get("status", "NEW")

                with st.container():
                    render_queue_row(alert)

                    # Status Update Action Controls
                    actions = st.container(horizontal=True, gap="small")
                    if actions.button("Confirm", key=f"btn_conf_{alert_id}", disabled=(status == "CONFIRMED")):
                        try:
                            update_alert(alert_id, status="CONFIRMED", mock_mode=st.session_state.mock_mode, base_url=st.session_state.api_url)
                            st.success(f"{alert_id} status updated to CONFIRMED")
                            st.rerun()
                        except BackendNotReachableError:
                            st.error("backend not reachable")
                        except Exception as e:
                            st.error(f"Update failed: {e}")

                    if actions.button("Dispatch", key=f"btn_disp_{alert_id}", type="primary", disabled=(status == "DISPATCHED")):
                        try:
                            update_alert(alert_id, status="DISPATCHED", mock_mode=st.session_state.mock_mode, base_url=st.session_state.api_url)
                            st.success(f"{alert_id} status updated to DISPATCHED")
                            st.rerun()
                        except BackendNotReachableError:
                            st.error("backend not reachable")
                        except Exception as e:
                            st.error(f"Update failed: {e}")

                    if actions.button("Dismiss", key=f"btn_dism_{alert_id}", disabled=(status == "DISMISSED")):
                        try:
                            update_alert(alert_id, status="DISMISSED", mock_mode=st.session_state.mock_mode, base_url=st.session_state.api_url)
                            st.info(f"{alert_id} dismissed")
                            st.rerun()
                        except BackendNotReachableError:
                            st.error("backend not reachable")
                        except Exception as e:
                            st.error(f"Update failed: {e}")

                    if actions.button("Open alert", key=f"btn_view_{alert_id}"):
                        st.session_state.current_alert = alert
                        st.session_state.nav_screen_selection = "Alert Card"
                        st.rerun()


# =============================================================================
# SCREEN 5: METRICS PAGE
# =============================================================================
elif screen == "Model Metrics":
    render_page_title(
        "Model metrics",
        "Scores from one evaluation script on held-out data. Baseline is TF-IDF with logistic regression; ours is DistilBERT plus Flan-T5.",
    )

    metrics_data = None
    try:
        metrics_data = get_metrics(
            mock_mode=st.session_state.mock_mode,
            base_url=st.session_state.api_url,
        )
    except BackendNotReachableError:
        st.error("backend not reachable")
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")

    if not metrics_data:
        st.info("Results appear after evaluation")
    else:
        # 1. Incident-Type Classification Comparison Table
        st.markdown("### Incident type: baseline vs DistilBERT")
        
        clf_data = metrics_data.get("classification", {})
        baseline_res = clf_data.get("baseline_tfidf_lr", {})
        distilbert_res = clf_data.get("distilbert", {})

        eval_sets = ["gold", "test_synth", "test_public"]
        comparison_rows = []

        for es in eval_sets:
            b_set = baseline_res.get(es, {})
            d_set = distilbert_res.get(es, {})

            if b_set or d_set:
                comparison_rows.append({
                    "Evaluation Set": es.upper(),
                    "Baseline Accuracy": f"{b_set.get('accuracy', 0.0):.3f}" if b_set.get('accuracy') is not None else "N/A",
                    "DistilBERT Accuracy": f"{d_set.get('accuracy', 0.0):.3f}" if d_set.get('accuracy') is not None else "N/A",
                    "Baseline Macro F1": f"{b_set.get('macro_f1', 0.0):.3f}" if b_set.get('macro_f1') is not None else "N/A",
                    "DistilBERT Macro F1": f"{d_set.get('macro_f1', 0.0):.3f}" if d_set.get('macro_f1') is not None else "N/A",
                    "Baseline Precision": f"{b_set.get('macro_precision', 0.0):.3f}" if b_set.get('macro_precision') is not None else "N/A",
                    "DistilBERT Precision": f"{d_set.get('macro_precision', 0.0):.3f}" if d_set.get('macro_precision') is not None else "N/A",
                    "Baseline Recall": f"{b_set.get('macro_recall', 0.0):.3f}" if b_set.get('macro_recall') is not None else "N/A",
                    "DistilBERT Recall": f"{d_set.get('macro_recall', 0.0):.3f}" if d_set.get('macro_recall') is not None else "N/A",
                    "Baseline Emergency Recall": f"{b_set.get('emergency_recall', 0.0):.3f}" if b_set.get('emergency_recall') is not None else "N/A",
                    "DistilBERT Emergency Recall": f"{d_set.get('emergency_recall', 0.0):.3f}" if d_set.get('emergency_recall') is not None else "N/A",
                })

        if comparison_rows:
            df_comp = pd.DataFrame(comparison_rows)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)
        else:
            st.info("Classification evaluation results not available.")

        # Key Safety Metrics highlight
        gold_d = distilbert_res.get("gold", {})
        gold_b = baseline_res.get("gold", {})
        if gold_d:
            st.markdown("#### Safety on the gold set (144 real reports)")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric(
                label="Emergencies caught",
                value=f"{gold_d.get('emergency_recall', 0)*100:.1f}%",
                delta=f"+{(gold_d.get('emergency_recall', 0) - gold_b.get('emergency_recall', 0))*100:.1f}% vs baseline",
            )
            m2.metric(
                label="Severe reports kept",
                value=f"{gold_d.get('critical_recall', 0)*100:.1f}%",
                delta=f"+{(gold_d.get('critical_recall', 0) - gold_b.get('critical_recall', 0.75))*100:.1f}% vs baseline",
            )
            m3.metric(
                label="Macro F1",
                value=f"{gold_d.get('macro_f1', 0):.3f}",
                delta=f"+{gold_d.get('macro_f1', 0) - gold_b.get('macro_f1', 0):.3f} vs baseline",
            )
            m4.metric(
                label="False alarms",
                value=f"{gold_d.get('false_alarm_rate', 0)*100:.1f}%",
                delta=f"{(gold_d.get('false_alarm_rate', 0) - gold_b.get('false_alarm_rate', 0))*100:.1f}%",
                delta_color="inverse",
            )

        st.markdown("---")

        # 2. Severity Regression Metrics
        st.markdown("### Severity, 1 to 5 (DistilBERT)")
        sev_data = metrics_data.get("severity", {}).get("distilbert", {})
        sev_rows = []
        for s_set_name, s_vals in sev_data.items():
            if isinstance(s_vals, dict):
                sev_rows.append({
                    "Test Set": s_set_name.upper(),
                    "RMSE": f"{s_vals.get('rmse', 0.0):.3f}",
                    "MSE": f"{s_vals.get('mse', 0.0):.3f}",
                    "MAE": f"{s_vals.get('mae', 0.0):.3f}",
                    "Bucket Accuracy": f"{s_vals.get('bucket_accuracy', 0.0)*100:.1f}%",
                    "Within ±1.0 Point": f"{s_vals.get('within_one', 0.0)*100:.1f}%",
                })
        if sev_rows:
            st.dataframe(pd.DataFrame(sev_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Severity metrics not available.")

        st.markdown("---")

        # 3. Field-Extraction Evaluation Table (Flan-T5)
        st.markdown("### Field extraction (Flan-T5)")
        extract_data = metrics_data.get("extraction", {}).get("flan_t5", {})
        ext_rows = []
        for e_set_name, e_vals in extract_data.items():
            if isinstance(e_vals, dict):
                inj = e_vals.get("injuries", {})
                haz = e_vals.get("hazards", {})
                ext_rows.append({
                    "Test Set": e_set_name.upper(),
                    "Parse Rate": f"{e_vals.get('parse_rate', 0.0)*100:.1f}%",
                    "Location Token F1": f"{e_vals.get('location_token_f1', 0.0):.3f}",
                    "People Exact Match": f"{e_vals.get('people_exact_match', 0.0)*100:.1f}%",
                    "Injuries F1 (Strict)": f"{inj.get('f1', 0.0):.3f}",
                    "Hazards F1 (Strict)": f"{haz.get('f1', 0.0):.3f}",
                    "Summary ROUGE-L": f"{e_vals.get('summary_rougeL', 0.0):.3f}",
                })
        if ext_rows:
            st.dataframe(pd.DataFrame(ext_rows), use_container_width=True, hide_index=True)
        else:
            st.info("Field extraction metrics not available.")

        st.markdown("---")

        # 4. Confusion Matrix PNGs
        st.markdown("### Confusion matrices, gold set")
        cm_col1, cm_col2 = st.columns(2)

        reports_dir = Path(__file__).resolve().parent.parent / "reports"
        cm_gold_ml2 = reports_dir / "confusion_matrix_gold_ml2.png"
        cm_gold_base = reports_dir / "confusion_matrix_gold_baseline.png"

        with cm_col1:
            st.markdown("**DistilBERT**")
            if cm_gold_ml2.exists():
                st.image(str(cm_gold_ml2), caption="DistilBERT Confusion Matrix — Gold Test Set", use_container_width=True)
            else:
                st.info("Confusion matrix for DistilBERT not generated yet.")

        with cm_col2:
            st.markdown("**TF-IDF + logistic regression baseline**")
            if cm_gold_base.exists():
                st.image(str(cm_gold_base), caption="Baseline Confusion Matrix — Gold Test Set", use_container_width=True)
            else:
                st.info("Confusion matrix for Baseline not generated yet.")
