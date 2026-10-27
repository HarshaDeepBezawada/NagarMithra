"""
NagarMithra — Mangalagiri Demo Data Generator
==============================================
Seeds the SQLite database with 100 realistic civic grievance tickets
distributed strictly across Mangalagiri, Andhra Pradesh, with varied
categories, severities, statuses, upvotes, and SLA compliance dates.
"""

import os
import sys
import random
from datetime import datetime, timezone, timedelta

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import init_db, insert_issue, insert_suggestion, DB_PATH
from boundary import MANGALAGIRI_LOCALITIES, is_inside_mangalagiri

SAMPLE_TITLES = {
    "Pothole": [
        "Deep pothole near Panakala Temple Ghat road",
        "Multiple road depressions on Weavers Colony main street",
        "Sunken manhole on Old Town Market road",
        "Damaged asphalt near Mangalagiri Railway Station junction",
        "Road erosion on approach road to AIIMS Mangalagiri",
        "Crater-like pothole outside ACA Stadium entry gate",
        "Broken road surface on Chinakakani service lane",
        "Pothole cluster on Yerrabalem Amaravati bypass road"
    ],
    "Garbage Dump": [
        "Overflowing municipal bin near Panakala Temple steps",
        "Commercial packaging waste dumped near Handloom Silk Market",
        "Uncollected residential waste along Navuluru colony",
        "Food waste accumulation near Kothapet vegetable market",
        "Debris blocking footpath near AIIMS Mangalagiri outer gate",
        "Open trash heap near Chinakakani NRI Hospital junction",
        "Plastic and organic waste dumped in vacant plot at Atmakur",
        "Uncleared community garbage dumper near Eco-Park entrance"
    ],
    "Streetlight Fault": [
        "Complete dark stretch of 5 poles on Temple Hill road",
        "Flickering LED streetlight near Mangalagiri Bus Stand",
        "Exposed wiring on lighting pole in Weavers Colony",
        "Non-functional streetlights on AIIMS connector road",
        "Dark junction near ACA Stadium posing night safety hazard",
        "Streetlights staying ON during daylight at Navuluru",
        "Damaged high-mast lamp near Kothapet market circle",
        "Broken light fixtures on Chinakakani pedestrian overpass"
    ],
    "Water Leakage": [
        "Drinking water pipeline leak on Temple Car Street",
        "Burst freshwater pipe flooding Weavers Colony lane",
        "Sub-surface pipe fracture near Mangalagiri Railway gate",
        "Muddy municipal water supply reported in Navuluru",
        "Broken public drinking water tap leaking continuously at Kothapet",
        "Water pipeline damaged during road work near AIIMS Mangalagiri",
        "Water logging near Chinakakani residential apartments",
        "Overflow drain blocked near Yerrabalem bypass"
    ],
    "Broken Footpath": [
        "Missing paver blocks on Panakala Temple pilgrimage path",
        "Cracked concrete walkway slab near Handloom Weavers Bhavan",
        "Broken footpath tiles outside Mangalagiri Railway Station",
        "Displaced curb stones forcing pedestrians onto road near AIIMS",
        "Caved-in walkway section near ACA Stadium north gate",
        "Damaged pedestrian pathway near Chinakakani commercial hub",
        "Missing drain slab creating walking hazard in Navuluru",
        "Broken tactile pavers for visually impaired near Kothapet"
    ]
}

MANGALAGIRI_SUGGESTIONS = [
    ("Pilgrim Electric Shuttle Service for Panakala Swamy Temple", "Introduce battery-operated eco-shuttles between Mangalagiri Railway Station, Bus Stand, and the hilltop Panakala Temple to ease congestion.", "Sita Ramaiah"),
    ("Mangalagiri Handloom Heritage Corridor & Display Pavilions", "Create dedicated pedestrianized heritage walking zones with solar streetlights in Weavers Colony to promote Mangalagiri GI cotton textiles.", "Venkateswarlu (Weavers Society)"),
    ("Automated Solar Streetlighting for AIIMS Connector Roads", "Install smart sensor-based solar lighting along the connector roads between NH-16 and AIIMS Mangalagiri for patient night travel safety.", "Dr. K. Srinivas Rao"),
    ("Rainwater Harvesting & Recharge Shafts at Mangalagiri Foothills", "Construct contour recharge pits and percolation trenches along Mangalagiri hill reserve to boost groundwater levels across Kothapet and Navuluru.", "Anuradha Devi"),
    ("Underground Drainage Modernization in Old Town & Kothapet", "Upgrade legacy open drainage canals in Old Mangalagiri into covered RCC box drains to eliminate seasonal flooding and mosquito breeding.", "P. Satyanarayana")
]


def seed():
    """Seed 100 realistic Mangalagiri tickets and civic proposals."""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[CLEANUP] Removed existing database: {DB_PATH}")
        except Exception:
            pass

    init_db()
    print("[INIT] Initialized empty SQLite schema for Mangalagiri.")

    now = datetime.now(timezone.utc)
    categories = list(SAMPLE_TITLES.keys())
    localities = list(MANGALAGIRI_LOCALITIES.keys())
    statuses = ["Open", "In Progress", "Resolved"]
    status_weights = [0.5, 0.25, 0.25]

    count = 0
    while count < 100:
        ticket_id = f"NM-{1001 + count}"
        cat = random.choice(categories)
        title = random.choice(SAMPLE_TITLES[cat])
        loc_key = random.choice(localities)
        loc_data = MANGALAGIRI_LOCALITIES[loc_key]

        # Small GPS jitter (+/- 0.003 degrees, ~300m radius around landmark)
        lat = round(loc_data["lat"] + random.uniform(-0.003, 0.003), 6)
        lon = round(loc_data["lon"] + random.uniform(-0.003, 0.003), 6)

        # Strictly verify inside Mangalagiri boundary
        if not is_inside_mangalagiri(lat, lon):
            continue

        severity = random.randint(1, 5)
        status = random.choices(statuses, weights=status_weights)[0]
        report_count = random.choices([1, 2, 3, 4, 5, 7], weights=[0.55, 0.20, 0.12, 0.07, 0.04, 0.02])[0]
        upvotes = random.randint(0, 35)

        # Vary created_at timestamp: from 2 hours ago up to 5 days ago
        hours_ago = random.uniform(1.0, 120.0)
        created_at = (now - timedelta(hours=hours_ago)).isoformat()

        desc = (
            f"Civic grievance reported near {loc_key}, Mangalagiri, Andhra Pradesh. "
            f"Observed impact on local residents and daily commuters. "
            f"Immediate inspection by Mangalagiri Municipal Corporation (MTMC) requested."
        )

        insert_issue(
            ticket_id=ticket_id,
            category=cat,
            title=title,
            description=desc,
            severity=severity,
            area=loc_key,
            latitude=lat,
            longitude=lon,
            photo_path="",
            status=status,
            upvotes=upvotes,
            report_count=report_count,
            created_at=created_at
        )
        count += 1

    print(f"[SUCCESS] Successfully seeded 100 verified civic issues inside Mangalagiri, AP.")

    for title, desc, author in MANGALAGIRI_SUGGESTIONS:
        insert_suggestion(title, desc, author)

    print(f"[SUCCESS] Seeded {len(MANGALAGIRI_SUGGESTIONS)} community proposals for Mangalagiri.")
    print("[READY] Database seeding complete.")


if __name__ == "__main__":
    seed()
