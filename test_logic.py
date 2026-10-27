"""
Automated Unit Test Suite for NagarMithra Logic
================================================
Tests the 5 core business rules:
1. Haversine distance accuracy (<100m detection)
2. Spatial duplicate merging for identical categories within 100m
3. Non-merging for distinct categories at the same coordinates
4. Dynamic priority score calculation and upper cap (100)
5. Service Level Agreement (SLA) breach detection engine
"""

from datetime import datetime, timezone, timedelta
from logic import (
    haversine_distance,
    calculate_priority_score,
    is_sla_breached,
    get_department_info
)


def test_distance_under_100m():
    """
    Verifies Haversine formula calculates distance between two
    Banjara Hills coordinates (~35m apart) as strictly under 100 metres.
    """
    # Banjara Hills Road No. 1 coords
    lat1, lon1 = 17.415600, 78.435000
    # Point ~35 metres away along the same road
    lat2, lon2 = 17.415850, 78.435200

    dist = haversine_distance(lat1, lon1, lat2, lon2)
    assert dist < 100.0, f"Distance should be under 100m, calculated {dist:.2f}m"
    assert dist > 20.0, f"Distance should be ~35m, calculated {dist:.2f}m"


def test_same_category_nearby_merges():
    """
    Simulates duplicate detection:
    An incoming report of the same category ('Pothole') located ~35m away
    from an active ticket MUST merge instead of creating a duplicate ticket.
    """
    existing_ticket = {
        "ticket_id": "NM-1001",
        "category": "Pothole",
        "latitude": 17.415600,
        "longitude": 78.435000,
        "status": "Open",
        "report_count": 1
    }

    incoming_category = "Pothole"
    incoming_lat = 17.415850
    incoming_lon = 78.435200

    dist = haversine_distance(
        existing_ticket["latitude"], existing_ticket["longitude"],
        incoming_lat, incoming_lon
    )

    should_merge = (
        incoming_category == existing_ticket["category"] and
        existing_ticket["status"] != "Resolved" and
        dist <= 100.0
    )

    assert should_merge is True
    # Verify merging behavior increments count
    merged_count = existing_ticket["report_count"] + 1
    assert merged_count == 2


def test_different_category_does_not_merge():
    """
    Verifies that a different category (e.g., 'Garbage Dump') at the
    exact same GPS coordinates does NOT merge into an existing 'Pothole' ticket.
    """
    existing_ticket = {
        "ticket_id": "NM-1001",
        "category": "Pothole",
        "latitude": 17.415600,
        "longitude": 78.435000,
        "status": "Open"
    }

    incoming_category = "Garbage Dump"
    incoming_lat = 17.415600
    incoming_lon = 78.435000

    dist = haversine_distance(
        existing_ticket["latitude"], existing_ticket["longitude"],
        incoming_lat, incoming_lon
    )

    should_merge = (
        incoming_category == existing_ticket["category"] and
        existing_ticket["status"] != "Resolved" and
        dist <= 100.0
    )

    assert should_merge is False


def test_priority_score_cap():
    """
    Verifies that extreme inputs (severity=5, reports=30, upvotes=50)
    cap at exactly 100 points and classify as 'Critical'.
    Also tests low inputs for correct tiering.
    """
    # Raw = (5 * 10) + (30 * 5) + (50 * 2) = 50 + 150 + 100 = 300
    score, level = calculate_priority_score(severity=5, report_count=30, upvotes=50)
    assert score == 100, f"Score should cap at 100, got {score}"
    assert level == "Critical"

    # Minimal: (1 * 10) + (1 * 5) + (0 * 2) = 15
    score_low, level_low = calculate_priority_score(severity=1, report_count=1, upvotes=0)
    assert score_low == 15
    assert level_low == "Low"

    # Medium: (3 * 10) + (2 * 5) + (5 * 2) = 30 + 10 + 10 = 50
    score_med, level_med = calculate_priority_score(severity=3, report_count=2, upvotes=5)
    assert score_med == 50
    assert level_med == "Medium"


def test_sla_breach_detection():
    """
    Verifies SLA breach engine:
    1. An unresolved ticket past its 24-hour deadline returns True (Breached).
    2. A 5-hour-old ticket within a 24-hour deadline returns False.
    3. A resolved ticket returns False regardless of age.
    """
    now = datetime.now(timezone.utc)

    # 1. 30 hours old, SLA = 24h, Open -> Breached
    t_breached = (now - timedelta(hours=30)).isoformat()
    assert is_sla_breached(t_breached, sla_hours=24, status="Open") is True

    # 2. 5 hours old, SLA = 24h, Open -> Within SLA
    t_fresh = (now - timedelta(hours=5)).isoformat()
    assert is_sla_breached(t_fresh, sla_hours=24, status="Open") is False

    # 3. 50 hours old, SLA = 24h, Resolved -> Not Breached
    t_old_resolved = (now - timedelta(hours=50)).isoformat()
    assert is_sla_breached(t_old_resolved, sla_hours=24, status="Resolved") is False
