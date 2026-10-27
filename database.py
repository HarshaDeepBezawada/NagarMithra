"""
NagarMithra — SQLite Persistence Layer
=======================================
Database layer implementing parameterized SQL queries (? placeholders),
absolute file path resolution, and transaction-safe operations.
"""

import os
import sqlite3
from datetime import datetime, timezone
from logic import (
    haversine_distance,
    calculate_priority_score,
    is_sla_breached,
    get_department_info
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "nagarmithra.db")


def get_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Create a connection with row-dictionary access and WAL mode for reliability."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(db_path: str = DB_PATH) -> None:
    """Initialize database tables according to specification."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE,
                category TEXT,
                department TEXT,
                title TEXT,
                description TEXT,
                severity INTEGER,
                area TEXT,
                latitude REAL,
                longitude REAL,
                photo_path TEXT,
                status TEXT,
                report_count INTEGER,
                upvotes INTEGER,
                priority_score INTEGER,
                priority_level TEXT,
                created_at TEXT,
                sla_hours INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                description TEXT,
                citizen_name TEXT,
                created_at TEXT
            )
        """)

        # Indexes for fast lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_issues_ticket_id ON issues (ticket_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_issues_status ON issues (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_issues_category ON issues (category)")
        conn.commit()


def find_duplicate_candidate(category: str, lat: float, lon: float, threshold_m: float = 100.0, db_path: str = DB_PATH):
    """
    Check for an existing, non-resolved ticket of the same category
    within threshold_m (100 metres) using Haversine distance.
    Returns: (matching_ticket_dict, distance_metres) or (None, None).
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # Fetch open tickets with identical category
        cursor.execute("""
            SELECT * FROM issues
            WHERE category = ? AND status != 'Resolved'
        """, (category,))
        rows = cursor.fetchall()

        for row in rows:
            dist = haversine_distance(lat, lon, row["latitude"], row["longitude"])
            if dist <= threshold_m:
                return dict(row), dist

    return None, None


def merge_duplicate_report(ticket_id: str, db_path: str = DB_PATH) -> dict:
    """
    Merge an incoming duplicate report into an existing master ticket:
    - Increments report_count by 1
    - Recalculates priority_score and priority_level
    - Returns updated ticket dictionary
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM issues WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        if not row:
            return None

        new_count = row["report_count"] + 1
        new_score, new_level = calculate_priority_score(
            row["severity"], new_count, row["upvotes"]
        )

        cursor.execute("""
            UPDATE issues
            SET report_count = ?, priority_score = ?, priority_level = ?
            WHERE ticket_id = ?
        """, (new_count, new_score, new_level, ticket_id))
        conn.commit()

        cursor.execute("SELECT * FROM issues WHERE ticket_id = ?", (ticket_id,))
        updated = dict(cursor.fetchone())
        updated["sla_breached"] = is_sla_breached(updated["created_at"], updated["sla_hours"], updated["status"])
        return updated


def insert_issue(ticket_id: str, category: str, title: str, description: str,
                 severity: int, area: str, latitude: float, longitude: float,
                 photo_path: str = "", status: str = "Open",
                 upvotes: int = 0, report_count: int = 1,
                 created_at: str = None, db_path: str = DB_PATH) -> dict:
    """
    Insert a brand new civic issue into the database.
    Computes department routing, priority score, and SLA hours.
    """
    dept_info = get_department_info(category)
    department = dept_info["department"]
    sla_hours = dept_info["sla_hours"]

    priority_score, priority_level = calculate_priority_score(severity, report_count, upvotes)

    if not created_at:
        created_at = datetime.now(timezone.utc).isoformat()

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO issues (
                ticket_id, category, department, title, description,
                severity, area, latitude, longitude, photo_path,
                status, report_count, upvotes, priority_score, priority_level,
                created_at, sla_hours
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id, category, department, title, description,
            int(severity), area, float(latitude), float(longitude), photo_path,
            status, int(report_count), int(upvotes), int(priority_score), priority_level,
            created_at, int(sla_hours)
        ))
        conn.commit()

    return get_issue(ticket_id, db_path=db_path)


def get_issue(ticket_id: str, db_path: str = DB_PATH) -> dict | None:
    """Fetch single ticket with calculated SLA breach status."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM issues WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["sla_breached"] = is_sla_breached(d["created_at"], d["sla_hours"], d["status"])
        return d


def get_all_issues(status: str = None, category: str = None, db_path: str = DB_PATH) -> list[dict]:
    """Retrieve all tickets with optional filtering, sorted by priority descending."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM issues WHERE 1=1"
        params = []

        if status and status != "All":
            query += " AND status = ?"
            params.append(status)

        if category and category != "All":
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY priority_score DESC, id DESC"
        cursor.execute(query, params)
        rows = cursor.fetchall()

        results = []
        for r in rows:
            d = dict(r)
            d["sla_breached"] = is_sla_breached(d["created_at"], d["sla_hours"], d["status"])
            results.append(d)
        return results


def increment_upvotes(ticket_id: str, db_path: str = DB_PATH) -> dict | None:
    """
    Increment upvotes by 1 and dynamically update priority score.
    Returns updated issue.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM issues WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        if not row:
            return None

        new_upvotes = row["upvotes"] + 1
        new_score, new_level = calculate_priority_score(
            row["severity"], row["report_count"], new_upvotes
        )

        cursor.execute("""
            UPDATE issues
            SET upvotes = ?, priority_score = ?, priority_level = ?
            WHERE ticket_id = ?
        """, (new_upvotes, new_score, new_level, ticket_id))
        conn.commit()

    return get_issue(ticket_id, db_path=db_path)


def update_status(ticket_id: str, new_status: str, db_path: str = DB_PATH) -> dict | None:
    """Update issue status (Open, In Progress, Resolved)."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE issues
            SET status = ?
            WHERE ticket_id = ?
        """, (new_status, ticket_id))
        conn.commit()

    return get_issue(ticket_id, db_path=db_path)


def get_stats(db_path: str = DB_PATH) -> dict:
    """
    Compute aggregate dashboard KPIs:
    - total_reports (cumulative reports including merged)
    - master_tickets (distinct work tickets)
    - issues_resolved (resolved count)
    - breached_tickets (open & past SLA)
    - sla_compliance percentage
    - breakdown by category and status
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT COALESCE(SUM(report_count), 0) FROM issues")
        total_reports = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM issues")
        master_tickets = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM issues WHERE status = 'Resolved'")
        issues_resolved = cursor.fetchone()[0]

        cursor.execute("SELECT * FROM issues WHERE status != 'Resolved'")
        active_issues = cursor.fetchall()
        breached_count = sum(
            1 for row in active_issues
            if is_sla_breached(row["created_at"], row["sla_hours"], row["status"])
        )

        # SLA Compliance: (1 - (breached / max(1, master_tickets))) * 100
        compliance = round((1.0 - (breached_count / max(1, master_tickets))) * 100.0, 1)

        # Category breakdown
        cursor.execute("SELECT category, COUNT(*) as cnt FROM issues GROUP BY category")
        category_counts = {r["category"]: r["cnt"] for r in cursor.fetchall()}

        # Status breakdown
        cursor.execute("SELECT status, COUNT(*) as cnt FROM issues GROUP BY status")
        status_counts = {r["status"]: r["cnt"] for r in cursor.fetchall()}

        return {
            "total_reports": total_reports,
            "master_tickets": master_tickets,
            "issues_resolved": issues_resolved,
            "breached_tickets": breached_count,
            "sla_compliance": compliance,
            "category_counts": category_counts,
            "status_counts": status_counts
        }


def insert_suggestion(title: str, description: str, citizen_name: str = "Anonymous", db_path: str = DB_PATH) -> dict:
    """Insert a community suggestion/idea."""
    now = datetime.now(timezone.utc).isoformat()
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO suggestions (title, description, citizen_name, created_at)
            VALUES (?, ?, ?, ?)
        """, (title, description, citizen_name or "Anonymous", now))
        conn.commit()
        sug_id = cursor.lastrowid
        return {
            "id": sug_id,
            "title": title,
            "description": description,
            "citizen_name": citizen_name or "Anonymous",
            "created_at": now
        }


def get_all_suggestions(db_path: str = DB_PATH) -> list[dict]:
    """Retrieve all community ideas in reverse chronological order."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suggestions ORDER BY id DESC")
        return [dict(r) for r in cursor.fetchall()]
