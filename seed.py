"""
NagarMithra — Demo Data Generator
==================================
Seeds the SQLite database with 100 realistic civic grievance tickets
distributed across 5 major Hyderabad zones with varied categories,
severities, statuses, upvotes, and SLA compliance dates.
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
from logic import HYDERABAD_HOTSPOTS

SAMPLE_TITLES = {
    "Pothole": [
        "Deep crater near Road No. 12 junction",
        "Multiple potholes causing traffic slow-down",
        "Sunken manhole creating bike hazard",
        "Asphalt washed away after recent rains",
        "Large pothole near metro pillar #42",
        "Damaged road surface outside commercial complex",
        "Dangerous road depression on flyover exit ramp",
        "Pothole cluster near school crossing zone"
    ],
    "Garbage Dump": [
        "Overflowing community garbage dumper",
        "Illegal commercial waste dumped on roadside",
        "Uncollected residential garbage bins for 3 days",
        "Rotting food waste attracting stray cattle",
        "Construction debris blocking public sidewalk",
        "Foul smell from uncleared municipal skip",
        "Open waste heap near local vegetable market",
        "Plastic and organic waste dumped in vacant plot"
    ],
    "Streetlight Fault": [
        "Complete dark stretch of 6 non-functional poles",
        "Flickering high-mast lamp near bus shelter",
        "Exposed wiring hanging from damaged lighting pole",
        "Streetlights remain ON during broad daylight",
        "Dark junction posing security risk at night",
        "Solar streetlamp battery damaged by tree branch",
        "Unlit pedestrian crossing on main arterial",
        "Broken glass enclosure on decorative park lamp"
    ],
    "Water Leakage": [
        "Drinking water pipeline burst flooding road",
        "Continuous freshwater leakage from valve joint",
        "Sub-surface pipe fracture causing water pooling",
        "Low water pressure and muddy supply in locality",
        "Damaged public water tap leaking 24/7",
        "Water supply pipe cracked by excavator digging",
        "Water logging near residential apartments",
        "Overhead municipal tank overflow drain clogged"
    ],
    "Broken Footpath": [
        "Missing paver blocks causing pedestrian trip hazard",
        "Cracked concrete slab over stormwater drain",
        "Broken tactile pavers for visually impaired citizens",
        "Caved-in footpath section near hospital entrance",
        "Displaced curb stones pushing pedestrians onto road",
        "Encroached and damaged walkway near metro station",
        "Slippery algae buildup on broken walkway",
        "Exposed iron reinforcement on storm-drain slab"
    ]
}

SAMPLE_SUGGESTIONS = [
    ("Solar Rooftop Mandate for Commercial Hubs", "GHMC should mandate rooftop solar panels on all commercial buildings in Madhapur and Gachibowli to reduce peak grid stress.", "Vikram Rao"),
    ("Automated Underground Waste Compactor Bins", "Deploy sensor-enabled hydraulic underground bins in historic Charminar streets to eliminate open visual garbage heaps.", "Fatima Zahra"),
    ("Dedicated Bicycle Corridors along Metro Corridors", "Create dedicated green-painted cycling tracks beneath the Miyapur-LB Nagar and Nagole-Raidurg metro lines.", "Karthik Reddy"),
    ("Real-Time Water Leakage Acoustic Sensor Pilot", "Implement IoT acoustic leak noise loggers across HMWSSB water transmission mains to prevent treated water loss.", "Ananya Sharma"),
    ("Smart LED Dimming System for Residential Colonies", "Introduce automated motion-based dimming for secondary streetlights after 1:00 AM across KPHB and Banjara Hills.", "Suresh Kumar")
]


def seed():
    """Seed 100 realistic tickets and demo suggestions."""
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"[CLEANUP] Removed existing database: {DB_PATH}")
        except Exception:
            pass

    init_db()
    print("[INIT] Initialized empty SQLite schema.")

    now = datetime.now(timezone.utc)
    categories = list(SAMPLE_TITLES.keys())
    hotspot_names = list(HYDERABAD_HOTSPOTS.keys())
    statuses = ["Open", "In Progress", "Resolved"]
    # 50% Open, 25% In Progress, 25% Resolved
    status_weights = [0.5, 0.25, 0.25]

    for i in range(1, 101):
        ticket_id = f"NM-{1000 + i}"
        cat = random.choice(categories)
        title = random.choice(SAMPLE_TITLES[cat])
        area = random.choice(hotspot_names)
        base_coords = HYDERABAD_HOTSPOTS[area]

        # Small GPS jitter (+/- 0.005 degrees, ~500m radius around hotspot)
        lat = round(base_coords["lat"] + random.uniform(-0.0045, 0.0045), 6)
        lon = round(base_coords["lon"] + random.uniform(-0.0045, 0.0045), 6)

        severity = random.randint(1, 5)
        status = random.choices(statuses, weights=status_weights)[0]
        report_count = random.choices([1, 2, 3, 4, 5, 8], weights=[0.55, 0.20, 0.12, 0.07, 0.04, 0.02])[0]
        upvotes = random.randint(0, 35)

        # Vary created_at timestamp: from 2 hours ago up to 5 days ago
        hours_ago = random.uniform(1.0, 120.0)
        created_at = (now - timedelta(hours=hours_ago)).isoformat()

        desc = (
            f"Civic grievance reported near {area} zone. "
            f"Observed impact on daily traffic and public convenience. "
            f"Immediate inspection by responsible municipal department requested."
        )

        insert_issue(
            ticket_id=ticket_id,
            category=cat,
            title=title,
            description=desc,
            severity=severity,
            area=area,
            latitude=lat,
            longitude=lon,
            photo_path="",
            status=status,
            upvotes=upvotes,
            report_count=report_count,
            created_at=created_at
        )

    print("[SUCCESS] Successfully seeded 100 civic issues across Hyderabad.")

    for title, desc, author in SAMPLE_SUGGESTIONS:
        insert_suggestion(title, desc, author)

    print(f"[SUCCESS] Seeded {len(SAMPLE_SUGGESTIONS)} community proposals.")
    print("[READY] Database seeding complete.")


if __name__ == "__main__":
    seed()
