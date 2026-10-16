import os
import re
import json
import time
from typing import Tuple, Optional
from geopy.geocoders import Nominatim
from rapidfuzz import process, fuzz

CACHE_FILE = "geocode_cache.json"
geolocator = Nominatim(user_agent="resqpulse_api_v1")

# High-density offline dictionary for Maharashtra + India Majors
# Add as many locations as you want here. Queries against this cost 0ms.
OFFLINE_GAZETTEER = {
    # Pune
    "pune": (18.5204, 73.8567), "fc road": (18.5204, 73.8466), "shivajinagar": (18.5314, 73.8446),
    "kothrud": (18.5074, 73.8077), "viman nagar": (18.5679, 73.9143), "hinjewadi": (18.5913, 73.7389),
    "mumbai-pune expressway": (18.7546, 73.4062), "lonavala": (18.7481, 73.4071),
    # Mumbai
    "mumbai": (19.0760, 72.8777), "bandra kurla complex": (19.0660, 72.8658), "andheri": (19.1136, 72.8697),
    "dadar": (19.0176, 72.8561), "colaba": (18.9067, 72.8147), "thane": (19.2183, 72.9781),
    # Rest of Maharashtra & India
    "nagpur": (21.1458, 79.0882), "nashik": (20.0110, 73.7903), "aurangabad": (19.8762, 75.3433),
    "delhi": (28.6139, 77.2090), "connaught place": (28.6315, 77.2167),
    "bengaluru": (12.9716, 77.5946), "chennai": (13.0827, 80.2707),
    # Other major cities that appear in the reports (city centres), so a map pin works with no internet
    "kolkata": (22.5726, 88.3639), "hyderabad": (17.3850, 78.4867), "ahmedabad": (23.0225, 72.5714),
    "jaipur": (26.9124, 75.7873), "lucknow": (26.8467, 80.9462), "guwahati": (26.1445, 91.7362),
    "kochi": (9.9312, 76.2673), "indore": (22.7196, 75.8577), "patna": (25.5941, 85.1376),
    "bhopal": (23.2599, 77.4126), "surat": (21.1702, 72.8311), "chandigarh": (30.7333, 76.7794),
    "kanpur": (26.4499, 80.3319), "varanasi": (25.3176, 82.9739), "bhubaneswar": (20.2961, 85.8245),
    "visakhapatnam": (17.6868, 83.2185), "coimbatore": (11.0168, 76.9558), "mysuru": (12.2958, 76.6394),
    "noida": (28.5355, 77.3910), "gurugram": (28.4595, 77.0266), "gurgaon": (28.4595, 77.0266),
    "ranchi": (23.3441, 85.3096), "dehradun": (30.3165, 78.0322), "goa": (15.4909, 73.8278),
    "kolhapur": (16.7050, 74.2433), "navi mumbai": (19.0330, 73.0297), "mira road": (19.2813, 72.8559),
    "pimpri chinchwad": (18.6298, 73.7997), "paud": (18.5042, 73.6200), "pune": (18.5204, 73.8567),
}

last_request_time = 0.0

def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return {}

geocode_cache = load_cache()

def get_coordinates(location_text: Optional[str]) -> Tuple[Optional[float], Optional[float], bool]:
    global last_request_time
    
    if not location_text or not location_text.strip():
        return None, None, False

    clean_text = location_text.lower().strip()

    # 1. 0ms Exact Cache Match
    if clean_text in geocode_cache:
        return geocode_cache[clean_text][0], geocode_cache[clean_text][1], True

    # 2a. 0ms: a known place name that actually appears in the text (longest name wins, so "kolhapur" beats "pune").
    # Matching on whole names only: a loose fuzzy match put "Barrackpore Kalyani expressway" (West Bengal) at Lonavala.
    named = [k for k in OFFLINE_GAZETTEER if re.search(rf"(?<![a-z]){re.escape(k)}(?![a-z])", clean_text)]
    if named:
        key = max(named, key=len)
        return OFFLINE_GAZETTEER[key][0], OFFLINE_GAZETTEER[key][1], True

    # 2b. 0ms: typo tolerance only ("shvajinagar"), by comparing the WHOLE text with a very strict ratio
    best_match = process.extractOne(clean_text, OFFLINE_GAZETTEER.keys(), scorer=fuzz.ratio)
    if best_match and best_match[1] >= 88:
        return OFFLINE_GAZETTEER[best_match[0]][0], OFFLINE_GAZETTEER[best_match[0]][1], True

    # 3. Slow Network API Fallback (Throttled to 1s)
    current_time = time.time()
    if current_time - last_request_time < 1.0:
        time.sleep(1.0 - (current_time - last_request_time))
        
    try:
        last_request_time = time.time()
        loc = geolocator.geocode(f"{clean_text}, India", country_codes="IN", timeout=3)
        if loc:
            # Save to cache so the next call is 0ms
            geocode_cache[clean_text] = (loc.latitude, loc.longitude)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(geocode_cache, f)
            return loc.latitude, loc.longitude, True
    except Exception as e:
        print(f"Network geocoding failed: {e}")

    return None, None, False

geocode_location = get_coordinates   # name used by src/api/main.py
