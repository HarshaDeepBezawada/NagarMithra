"""
NagarMithra — Mangalagiri Service Boundary Engine
==================================================
Strict geographic validation ensuring the platform exclusively accepts
civic complaints within the defined Mangalagiri service area,
Andhra Pradesh, India.

Enforces boundary checks via Ray-Casting Point-in-Polygon (PIP) algorithm
both on backend API endpoints and in frontend Leaflet maps.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GEOJSON_PATH = os.path.join(BASE_DIR, "mangalagiri_boundary.geojson")

# Default boundary polygon vertices [(lat, lon), ...]
# (Loaded from GeoJSON or fallback constants)
DEFAULT_MANGALAGIRI_POLYGON = [
    (16.4750, 80.5300),
    (16.4780, 80.5500),
    (16.4720, 80.5700),
    (16.4550, 80.5880),
    (16.4380, 80.5950),
    (16.4220, 80.5900),
    (16.4080, 80.5800),
    (16.3980, 80.5650),
    (16.3980, 80.5450),
    (16.4050, 80.5280),
    (16.4200, 80.5150),
    (16.4450, 80.5150),
    (16.4650, 80.5200),
    (16.4750, 80.5300)
]

# Verified Mangalagiri Localities & Landmarks
MANGALAGIRI_LOCALITIES = {
    "Panakala Temple Area": {
        "name": "Sri Panakala Lakshmi Narasimha Swamy Temple",
        "description": "Ancient historic hill shrine of Lord Narasimha, famous for panakam offerings and the 153-foot Raja Gopuram.",
        "lat": 16.438500,
        "lon": 80.562000,
        "landmark_type": "Heritage & Spiritual"
    },
    "Weavers Colony": {
        "name": "Mangalagiri Handloom Weavers Colony",
        "description": "Traditional artisan weaving quarter producing the famous GI-tagged Mangalagiri cotton sarees and fabrics with Nizam borders.",
        "lat": 16.431000,
        "lon": 80.561500,
        "landmark_type": "Handloom & Craft Heritage"
    },
    "AIIMS Mangalagiri": {
        "name": "AIIMS Mangalagiri Campus",
        "description": "Premier national apex healthcare institute and hospital campus established under PMSSY.",
        "lat": 16.446800,
        "lon": 80.528500,
        "landmark_type": "Healthcare & Education"
    },
    "ACA Stadium": {
        "name": "ACA International Cricket Stadium",
        "description": "State-of-the-art international cricket facility of the Andhra Cricket Association.",
        "lat": 16.441200,
        "lon": 80.551000,
        "landmark_type": "Sports Infrastructure"
    },
    "Railway Station / Kothapet": {
        "name": "Mangalagiri Railway Station & Old Town",
        "description": "Central municipal transit corridor connecting Vijayawada-Guntur railway lines and local markets.",
        "lat": 16.433500,
        "lon": 80.557000,
        "landmark_type": "Transit & Commercial"
    },
    "Chinakakani / NRI Hospital": {
        "name": "Chinakakani & NRI General Hospital",
        "description": "Major healthcare, academic, and residential junction along NH-16.",
        "lat": 16.405500,
        "lon": 80.548000,
        "landmark_type": "Healthcare & Residential"
    },
    "Navuluru / Atmakur": {
        "name": "Navuluru & Atmakur Residential Zones",
        "description": "Rapidly growing civic neighborhoods with residential colonies and local schools.",
        "lat": 16.425000,
        "lon": 80.535000,
        "landmark_type": "Residential"
    },
    "Yerrabalem / Amaravati Bypass": {
        "name": "Yerrabalem Corridor",
        "description": "Northern arterial gateway linking Mangalagiri to the Amaravati capital region.",
        "lat": 16.462000,
        "lon": 80.543000,
        "landmark_type": "Transit Arterial"
    },
    "Eco-Park / Reserve Forest": {
        "name": "Mangalagiri Eco-Park & Reserve Forest",
        "description": "Protected green lung and biodiversity trail at the foothills of Mangalagiri.",
        "lat": 16.429000,
        "lon": 80.575000,
        "landmark_type": "Ecological & Recreation"
    }
}


def load_boundary_polygon() -> list[tuple[float, float]]:
    """
    Load polygon coordinates from GeoJSON file if present,
    otherwise fallback to verified polygon constants.
    Returns list of (latitude, longitude) tuples.
    """
    if os.path.exists(GEOJSON_PATH):
        try:
            with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                features = data.get("features", [])
                if features:
                    coords = features[0]["geometry"]["coordinates"][0]
                    # GeoJSON is [lon, lat], convert to (lat, lon)
                    return [(pt[1], pt[0]) for pt in coords]
        except Exception:
            pass
    return DEFAULT_MANGALAGIRI_POLYGON


# Pre-cached polygon
MANGALAGIRI_POLYGON = load_boundary_polygon()

# Bounding box for fast-path rejection
MIN_LAT = min(p[0] for p in MANGALAGIRI_POLYGON)
MAX_LAT = max(p[0] for p in MANGALAGIRI_POLYGON)
MIN_LON = min(p[1] for p in MANGALAGIRI_POLYGON)
MAX_LON = max(p[1] for p in MANGALAGIRI_POLYGON)


def is_inside_mangalagiri(lat: float, lon: float) -> bool:
    """
    Ray-Casting Point-in-Polygon (PIP) Algorithm:
    Determines if coordinate (lat, lon) lies inside the Mangalagiri boundary.

    1. Fast-path bounding box check.
    2. Ray-casting: cast horizontal ray to infinity and count edge intersections.
    Returns True if inside, False otherwise.
    """
    # 1. Bounding box fast-path rejection
    if lat < MIN_LAT or lat > MAX_LAT or lon < MIN_LON or lon > MAX_LON:
        return False

    # 2. Ray-casting algorithm
    inside = False
    n = len(MANGALAGIRI_POLYGON)
    p1_lat, p1_lon = MANGALAGIRI_POLYGON[0]

    for i in range(1, n + 1):
        p2_lat, p2_lon = MANGALAGIRI_POLYGON[i % n]
        if min(p1_lat, p2_lat) < lat <= max(p1_lat, p2_lat):
            if lon <= max(p1_lon, p2_lon):
                if p1_lat != p2_lat:
                    lon_intersect = (lat - p1_lat) * (p2_lon - p1_lon) / (p2_lat - p1_lat) + p1_lon
                    if p1_lon == p2_lon or lon <= lon_intersect:
                        inside = not inside
        p1_lat, p1_lon = p2_lat, p2_lon

    return inside


def validate_mangalagiri_coordinates(lat: float, lon: float) -> tuple[bool, str]:
    """
    Validates submitted coordinates.
    Returns (is_valid, user_friendly_message).
    """
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (ValueError, TypeError):
        return False, "Invalid coordinate format."

    if is_inside_mangalagiri(lat_f, lon_f):
        return True, "Location verified within the Mangalagiri service area."
    else:
        return False, (
            "Location Outside Mangalagiri: This platform currently accepts civic complaints "
            "only within the designated Mangalagiri service area, Andhra Pradesh. "
            "The location you selected does not fall within our supported area. "
            "Please select a location inside Mangalagiri to continue."
        )


def get_boundary_geojson_dict() -> dict:
    """Return the raw GeoJSON dict for frontend Leaflet rendering."""
    if os.path.exists(GEOJSON_PATH):
        try:
            with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    # Fallback GeoJSON
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Mangalagiri Service Boundary"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[p[1], p[0]] for p in DEFAULT_MANGALAGIRI_POLYGON]]
                }
            }
        ]
    }
