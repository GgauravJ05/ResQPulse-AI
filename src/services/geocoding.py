import os
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
    "bengaluru": (12.9716, 77.5946), "chennai": (13.0827, 80.2707)
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

    # 2. 0ms Fuzzy Match against Maharashtra Offline Database
    # This catches typos like "shvajinagar" or "bandra kurla"
    best_match = process.extractOne(clean_text, OFFLINE_GAZETTEER.keys(), scorer=fuzz.WRatio)
    if best_match and best_match[1] > 85: # 85% similarity threshold
        matched_key = best_match[0]
        return OFFLINE_GAZETTEER[matched_key][0], OFFLINE_GAZETTEER[matched_key][1], True

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