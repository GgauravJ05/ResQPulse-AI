import streamlit as st
import requests
import json
import os
from datetime import datetime

st.set_page_config(page_title="ResQPulse AI - Dispatcher", page_icon="🚨")
st.title("🚨 ResQPulse Dispatcher Input")

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

audio_bytes = st.audio_input("Record emergency report via Mic")

if audio_bytes is not None:
    with st.spinner("Processing Voice Report (Whisper -> DistilBERT -> Flan-T5)..."):
        try:
            # Step 1: Transcribe
            files = {"file": ("report.wav", audio_bytes, "audio/wav")}
            transcribe_res = requests.post("http://localhost:8000/transcribe", files=files)
            
            if transcribe_res.status_code == 200:
                transcribed_text = transcribe_res.json()["transcript"] # Updated to match new schema
                st.info(f"**Heard:** {transcribed_text}")
                
                # Step 2: Analyze
                analyze_payload = {"text": transcribed_text, "source": "voice"}
                analyze_res = requests.post("http://localhost:8000/analyze", json=analyze_payload)
                
                if analyze_res.status_code == 200:
                    alert_data = analyze_res.json()
                    
                    # Display the Alert Card
                    st.success("Alert Generated Successfully")
                    st.markdown(f"### {alert_data['incident_type']} - Priority: {alert_data['severity_label']} ({alert_data['severity']})")
                    st.write(f"**Location:** {alert_data['location']['text']}")
                    if alert_data['location']['lat']:
                        st.write(f"*(Lat/Lon: {alert_data['location']['lat']}, {alert_data['location']['lon']})*")
                    
                    st.write(f"**Summary:** {alert_data['summary']}")
                    st.write(f"**Send Responders:** {', '.join(alert_data['responders'])}")
                    
                    # Save JSON
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = os.path.join(OUTPUT_DIR, f"alert_{timestamp}.json")
                    with open(filename, "w") as f:
                        json.dump(alert_data, f, indent=4)
                        
                    with st.expander("View Raw JSON & Debug"):
                        st.json(alert_data)
                else:
                    st.error(f"Analyze Failed: {analyze_res.json()}")
            else:
                st.error(f"Transcribe Failed: {transcribe_res.json()}")
                
        except requests.exceptions.ConnectionError:
            st.error("Backend not reachable. Ensure `python -m uvicorn src.api.main:app --port 8000` is running in another terminal.")