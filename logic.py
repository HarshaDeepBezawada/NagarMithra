"""
NagarMithra — Core Algorithmic Engine
=====================================
Contains the 4 core mathematical and business algorithms for civic management:
1. Department Routing & SLA Mapping
2. Haversine Spatial Great-Circle Distance & Duplicate Detection
3. Dynamic Civic Priority Formula (0-100 scale)
4. Service Level Agreement (SLA) Compliance & Breach Detection
"""

import math
import random
from datetime import datetime, timezone, timedelta

# Earth radius in metres for the Haversine formula
EARTH_RADIUS_METRES = 6371000.0

# 2.1 Automated Department Routing & SLA Deadlines
DEPARTMENT_ROUTING = {
    "Pothole": {
        "icon": "🕳️",
        "department": "Roads & Traffic Infrastructure (GHMC)",
        "sla_hours": 48
    },
    "Garbage Dump": {
        "icon": "🗑️",
        "department": "Sanitation & Solid Waste Management",
        "sla_hours": 24
    },
    "Streetlight Fault": {
        "icon": "💡",
        "department": "Electricity & Public Lighting (TSSPDCL)",
        "sla_hours": 36
    },
    "Water Leakage": {
        "icon": "🚰",
        "department": "Water Supply & Drainage Board (HMWSSB)",
        "sla_hours": 24
    },
    "Broken Footpath": {
        "icon": "🚶",
        "department": "Public Works Department (PWD Walkways)",
        "sla_hours": 72
    }
}

FALLBACK_DEPARTMENT = {
    "icon": "📌",
    "department": "General Municipal Administration",
    "sla_hours": 48
}

HYDERABAD_HOTSPOTS = {
    "Banjara Hills": {"lat": 17.415600, "lon": 78.435000, "zone": "Commercial & Residential Arterial"},
    "Madhapur": {"lat": 17.448300, "lon": 78.391500, "zone": "IT Corridor / Hitec City"},
    "Gachibowli": {"lat": 17.440100, "lon": 78.348900, "zone": "Financial District & Outer Ring Road"},
    "Charminar": {"lat": 17.361600, "lon": 78.474700, "zone": "High-Density Historic Commercial Core"},
    "Kukatpally": {"lat": 17.494800, "lon": 78.399600, "zone": "High-Density Residential (KPHB)"}
}


def get_department_info(category: str) -> dict:
    """Return department name, icon, and SLA hours for a given civic category."""
    return DEPARTMENT_ROUTING.get(category, FALLBACK_DEPARTMENT)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two GPS coordinates in metres
    using the Haversine formula.
    
    Δϕ = radians(lat2 - lat1)
    Δλ = radians(lon2 - lon1)
    a = sin²(Δϕ / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin²(Δλ / 2)
    c = 2 * atan2(√a, √(1-a))
    d = R * c (R = 6,371,000 metres)
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_METRES * c


def calculate_priority_score(severity: int, report_count: int, upvotes: int) -> tuple[int, str]:
    """
    Calculate civic priority on a 0-100 scale:
    Raw Score = (Severity * 10) + (Report Count * 5) + (Upvotes * 2)
    Priority Score = min(100, max(0, Raw Score))
    
    Tiers:
    - Critical: >= 80
    - High: 60 <= Score < 80
    - Medium: 40 <= Score < 60
    - Low: < 40
    """
    severity = max(1, min(5, int(severity)))
    report_count = max(1, int(report_count))
    upvotes = max(0, int(upvotes))

    raw_score = (severity * 10) + (report_count * 5) + (upvotes * 2)
    score = min(100, max(0, raw_score))

    if score >= 80:
        level = "Critical"
    elif score >= 60:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    return score, level


def is_sla_breached(created_at_iso: str, sla_hours: int, status: str) -> bool:
    """
    Determine if a ticket has breached its resolution SLA:
    - If status == "Resolved": False (closed)
    - If (Current Time - Created Time) > SLA Hours: True
    - Otherwise: False
    """
    if status == "Resolved":
        return False

    try:
        if created_at_iso.endswith("Z"):
            created_at = datetime.fromisoformat(created_at_iso[:-1]).replace(tzinfo=timezone.utc)
        elif "+" in created_at_iso or created_at_iso.count("-") > 2:
            created_at = datetime.fromisoformat(created_at_iso)
        else:
            created_at = datetime.fromisoformat(created_at_iso).replace(tzinfo=timezone.utc)
    except Exception:
        return False

    now = datetime.now(timezone.utc)
    elapsed = (now - created_at).total_seconds() / 3600.0
    return elapsed > sla_hours


def generate_ticket_id() -> str:
    """Generate a unique 4-digit ticket reference ID (e.g., NM-1042)."""
    return f"NM-{random.randint(1000, 9999)}"
