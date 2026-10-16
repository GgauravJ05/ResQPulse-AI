from functools import lru_cache
from typing import Tuple, Optional
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

geolocator = Nominatim(user_agent="resqpulse_api_v1")

DEMO_FALLBACKS = {
    "mumbai-pune expressway near lonavala exit": (18.7546, 73.4062),
    "fc road": (18.5204, 73.8466),
    "petrol pump on fc road": (18.5204, 73.8466),
    "connaught place, delhi": (28.6315, 77.2167)
}

@lru_cache(maxsize=256)
def geocode_location(location_text: Optional[str]) -> Tuple[Optional[float], Optional[float], bool]:
    if not location_text or not location_text.strip():
        return None, None, False

    clean = location_text.lower().strip()
    for key, (lat, lon) in DEMO_FALLBACKS.items():
        if key in clean:
            return lat, lon, True

    try:
        loc = geolocator.geocode(f"{location_text}, India", country_codes="IN", timeout=5)
        if loc:
            return loc.latitude, loc.longitude, True
    except (GeocoderTimedOut, GeocoderServiceError):
        pass

    return None, None, False