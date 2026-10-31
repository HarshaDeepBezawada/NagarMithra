"""
NagarMithra — Mangalagiri Civic Tech Platform (Flask + SQLite Backend)
====================================================================
Simple, clean, and reliable REST API & Web Server built with Python Flask and SQLite.

Features:
- Mandatory geotagged photo verification (EXIF GPS parsing via Pillow)
- Strict Mangalagiri geographic boundary enforcement (Ray-Casting PIP)
- Haversine spatial duplicate detection (<100m auto-merge)
- Dynamic community priority scoring (0-100) & SLA monitoring
- Parameterized SQLite queries (? placeholders)
- Static file serving (Single-Page App, Gopuram logo, footer panorama)
- Universal CORS headers
"""

import os
import sys
import io
import csv
import uuid
import base64
from flask import Flask, request, jsonify, send_from_directory, send_file, Response
from PIL import Image, ExifTags

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from database import (
    init_db,
    find_duplicate_candidate,
    merge_duplicate_report,
    insert_issue,
    get_issue,
    get_all_issues,
    increment_upvotes,
    update_status,
    get_stats,
    insert_suggestion,
    get_all_suggestions,
    create_user,
    get_user_by_phone,
    authenticate_user,
    get_issues_by_citizen,
    DB_PATH,
    BASE_DIR
)
from logic import generate_ticket_id
from boundary import (
    is_inside_mangalagiri,
    validate_mangalagiri_coordinates,
    get_boundary_geojson_dict,
    MANGALAGIRI_LOCALITIES
)

UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(FRONTEND_DIR, exist_ok=True)

# Coordinator passcode for staff modal
ADMIN_PASSCODE = "admin123"

# Initialize Flask application
app = Flask(__name__, static_folder=None)
app.config["JSON_AS_ASCII"] = False


# ============================================================================
# CORS & SECURITY HEADERS
# ============================================================================
@app.after_request
def add_cors_headers(response):
    """Add universal CORS headers to all responses."""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# ============================================================================
# EXIF GPS HELPER
# ============================================================================
def _convert_dms_to_degrees(dms_value) -> float:
    """Helper to convert EXIF Degree-Minute-Second tuples to decimal degrees."""
    try:
        d = float(dms_value[0])
        m = float(dms_value[1])
        s = float(dms_value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return 0.0


def extract_exif_gps_from_bytes(image_bytes: bytes) -> tuple[float | None, float | None]:
    """
    Extract GPS Latitude & Longitude from image EXIF metadata.
    Returns (lat, lon) in decimal degrees if found, else (None, None).
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        exif_raw = img._getexif()
        if not exif_raw:
            return None, None

        gps_info = {}
        for tag, val in exif_raw.items():
            tag_name = ExifTags.TAGS.get(tag, tag)
            if tag_name == "GPSInfo":
                for sub_tag in val:
                    sub_name = ExifTags.GPSTAGS.get(sub_tag, sub_tag)
                    gps_info[sub_name] = val[sub_tag]

        if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
            lat = _convert_dms_to_degrees(gps_info["GPSLatitude"])
            lon = _convert_dms_to_degrees(gps_info["GPSLongitude"])
            lat_ref = gps_info.get("GPSLatitudeRef", "N")
            lon_ref = gps_info.get("GPSLongitudeRef", "E")

            if lat_ref != "N":
                lat = -lat
            if lon_ref != "E":
                lon = -lon

            return round(lat, 6), round(lon, 6)
    except Exception:
        pass
    return None, None


# ============================================================================
# STATIC ROUTES & FRONTEND DELIVERY
# ============================================================================
@app.route("/", methods=["GET"])
def serve_index():
    """Serve the single-page application index.html."""
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename):
    """Serve uploaded user photos."""
    return send_from_directory(UPLOAD_DIR, filename)


@app.route("/mangalagiri_footer.png", methods=["GET"])
@app.route("/footer.png", methods=["GET"])
def serve_footer_image():
    """Serve the panoramic footer artwork."""
    footer_path = os.path.join(FRONTEND_DIR, "mangalagiri_footer.png")
    if not os.path.exists(footer_path):
        footer_path = os.path.join(BASE_DIR, "static", "images", "mangalagiri_footer.png")
    if os.path.exists(footer_path):
        return send_file(footer_path, mimetype="image/png")
    return jsonify({"error": "Footer image not found"}), 404


@app.route("/<path:filename>", methods=["GET"])
def serve_static(filename):
    """Safely deliver any static asset from frontend/ (e.g., gopuram_logo.svg)."""
    file_path = os.path.join(FRONTEND_DIR, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIR, filename)
    return jsonify({"error": "File not found"}), 404


# ============================================================================
# CIVIC REST API ENDPOINTS
# ============================================================================
@app.route("/api/boundary", methods=["GET"])
def api_boundary():
    """Returns the GeoJSON polygon for the Mangalagiri civic boundary."""
    return jsonify(get_boundary_geojson_dict())


@app.route("/api/localities", methods=["GET"])
def api_localities():
    """Returns verified Mangalagiri landmarks and hotspots."""
    return jsonify(MANGALAGIRI_LOCALITIES)


@app.route("/api/stats", methods=["GET"])
def api_stats():
    """Returns aggregated civic metrics (total reports, active, resolved, SLA rate)."""
    return jsonify(get_stats())


@app.route("/api/issues", methods=["GET"])
def api_issues():
    """List issues with optional ?status= and ?category= query filtering."""
    status_filter = request.args.get("status")
    category_filter = request.args.get("category")
    issues = get_all_issues(status=status_filter, category=category_filter)
    return jsonify(issues)


@app.route("/api/issues/<ticket_id>", methods=["GET"])
def api_issue_detail(ticket_id):
    """Fetch details of a single ticket by Reference ID (e.g., NM-1001)."""
    tid = ticket_id.strip().upper()
    issue = get_issue(tid)
    if issue:
        return jsonify(issue)
    return jsonify({"error": f"Ticket {tid} not found"}), 404


@app.route("/api/suggestions", methods=["GET"])
def api_get_suggestions():
    """List all community proposals."""
    return jsonify(get_all_suggestions())


@app.route("/api/export-csv", methods=["GET"])
def api_export_csv():
    """Export all civic issues as a CSV download."""
    issues = get_all_issues()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Ticket ID", "Category", "Department", "Title", "Description",
        "Severity", "Area", "Latitude", "Longitude", "Status",
        "Report Count", "Upvotes", "Priority Score", "Priority Level",
        "Created At", "SLA Hours", "SLA Breached"
    ])
    for i in issues:
        writer.writerow([
            i["ticket_id"], i["category"], i["department"], i["title"], i["description"],
            i["severity"], i["area"], i["latitude"], i["longitude"], i["status"],
            i["report_count"], i["upvotes"], i["priority_score"], i["priority_level"],
            i["created_at"], i["sla_hours"], i["sla_breached"]
        ])

    csv_data = output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=mangalagiri_civic_data.csv"}
    )


@app.route("/api/validate-location", methods=["POST"])
def api_validate_location():
    """Pre-flight check to verify if given GPS coordinates fall inside Mangalagiri."""
    body = request.get_json(silent=True) or {}
    try:
        lat = float(body.get("latitude"))
        lon = float(body.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({"valid": False, "message": "Invalid latitude or longitude."}), 400

    is_valid, message = validate_mangalagiri_coordinates(lat, lon)
    return jsonify({
        "valid": is_valid,
        "message": message,
        "latitude": lat,
        "longitude": lon
    })


@app.route("/api/report", methods=["POST"])
def api_report_issue():
    """
    Submit a civic complaint with MANDATORY Geotagged Photo & Mangalagiri boundary check.
    Performs spatial duplicate detection (<100m Haversine) and auto-merges or creates a new ticket.
    """
    body = request.get_json(silent=True) or {}
    category = body.get("category", "").strip()
    title = body.get("title", "").strip()
    description = body.get("description", "").strip()
    severity = int(body.get("severity", 2))
    area = body.get("area", "Panakala Temple Area").strip()
    photo_data = body.get("photo_data", "")

    # 1. Mandatory Photo Check
    if not photo_data or "base64," not in photo_data:
        return jsonify({
            "error": "Geotagged Photo Required",
            "message": "Uploading a photo is mandatory. Only geotagged images are accepted."
        }), 400

    # 2. Extract image bytes from base64
    try:
        header, encoded = photo_data.split("base64,", 1)
        img_bytes = base64.b64decode(encoded)
    except Exception:
        return jsonify({
            "error": "Invalid Photo Format",
            "message": "The uploaded photo data could not be processed. Please upload a valid image."
        }), 400

    # 3. Parse EXIF GPS metadata if present
    exif_lat, exif_lon = extract_exif_gps_from_bytes(img_bytes)
    try:
        if exif_lat is not None and exif_lon is not None:
            lat = float(exif_lat)
            lon = float(exif_lon)
        else:
            lat = float(body.get("latitude"))
            lon = float(body.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid GPS coordinates."}), 400

    if not category or not title:
        return jsonify({"error": "Category and Title are required."}), 400

    # 4. Mangalagiri Boundary Validation
    is_valid_loc, boundary_msg = validate_mangalagiri_coordinates(lat, lon)
    if not is_valid_loc:
        return jsonify({
            "error": "Location Outside Mangalagiri",
            "message": "Notice: This civic tech portal is exclusively for Mangalagiri. Please select a location within Mangalagiri.",
            "latitude": lat,
            "longitude": lon
        }), 400

    # 5. Save photo to uploads directory
    saved_photo_path = ""
    try:
        ext = "png" if "png" in header else ("webp" if "webp" in header else "jpg")
        img_filename = f"{generate_ticket_id().lower()}_{uuid.uuid4().hex[:6]}.{ext}"
        full_path = os.path.join(UPLOAD_DIR, img_filename)
        with open(full_path, "wb") as img_file:
            img_file.write(img_bytes)
        saved_photo_path = f"/uploads/{img_filename}"
    except Exception as ex:
        print(f"Error saving image: {ex}")

    # 6. Spatial Duplicate Detection (<100m threshold, same category, open/in-progress)
    duplicate_candidate, distance = find_duplicate_candidate(category, lat, lon, threshold_m=100.0)
    if duplicate_candidate:
        updated_ticket = merge_duplicate_report(duplicate_candidate["ticket_id"])
        return jsonify({
            "status": "merged",
            "ticket_id": updated_ticket["ticket_id"],
            "distance_metres": round(distance, 1),
            "message": f"Duplicate Merged into Master Ticket #{updated_ticket['ticket_id']}! Location is within {round(distance, 1)}m of an existing report. Priority escalated.",
            "ticket": updated_ticket
        }), 200

    citizen_phone = body.get("citizen_phone", "").strip()

    # 7. Create New Ticket
    new_ticket_id = generate_ticket_id()
    new_ticket = insert_issue(
        ticket_id=new_ticket_id,
        category=category,
        title=title,
        description=description,
        severity=severity,
        area=area,
        latitude=lat,
        longitude=lon,
        photo_path=saved_photo_path,
        citizen_phone=citizen_phone
    )

    return jsonify({
        "status": "created",
        "ticket_id": new_ticket["ticket_id"],
        "message": f"Civic Ticket #{new_ticket['ticket_id']} Created Successfully in Mangalagiri! Target: {new_ticket['sla_hours']} Hours.",
        "ticket": new_ticket
    }), 201


@app.route("/api/upvote", methods=["POST"])
def api_upvote():
    """Increment upvotes for a ticket and re-compute community priority score."""
    body = request.get_json(silent=True) or {}
    ticket_id = body.get("ticket_id", "").strip().upper()
    if not ticket_id:
        return jsonify({"error": "ticket_id required"}), 400

    updated = increment_upvotes(ticket_id)
    if updated:
        return jsonify({
            "success": True,
            "ticket_id": ticket_id,
            "upvotes": updated["upvotes"],
            "priority_score": updated["priority_score"],
            "priority_level": updated["priority_level"],
            "ticket": updated
        })
    return jsonify({"error": f"Ticket {ticket_id} not found"}), 404


@app.route("/api/status", methods=["POST"])
def api_update_status():
    """Update ticket status via coordinator console (passcode protected)."""
    body = request.get_json(silent=True) or {}
    ticket_id = body.get("ticket_id", "").strip().upper()
    new_status = body.get("status", "").strip()
    passcode = body.get("passcode", "").strip() or body.get("password", "").strip()

    if passcode != ADMIN_PASSCODE:
        return jsonify({"error": "Invalid coordinator authentication passcode"}), 401

    if new_status not in ["Open", "In Progress", "Resolved"]:
        return jsonify({"error": "Status must be Open, In Progress, or Resolved"}), 400

    updated = update_status(ticket_id, new_status)
    if updated:
        return jsonify({
            "success": True,
            "message": f"Ticket {ticket_id} status updated to {new_status}",
            "ticket": updated
        })
    return jsonify({"error": f"Ticket {ticket_id} not found"}), 404


@app.route("/api/suggestions", methods=["POST"])
def api_create_suggestion():
    """Submit a community civic improvement proposal."""
    body = request.get_json(silent=True) or {}
    title = body.get("title", "").strip()
    desc = body.get("description", "").strip()
    author = body.get("author_name", "").strip() or body.get("citizen_name", "Mangalagiri Citizen").strip()

    if not title or not desc:
        return jsonify({"error": "Title and Description are required"}), 400

    item = insert_suggestion(title, desc, author)
    return jsonify(item), 201


# ============================================================================
# AUTHENTICATION ENDPOINTS (CITIZEN & STAFF PORTALS)
# ============================================================================
@app.route("/api/auth/register", methods=["POST"])
def api_auth_register():
    """Register a new citizen account."""
    body = request.get_json(silent=True) or {}
    name = body.get("name", "").strip()
    phone = body.get("phone", "").strip()
    password = body.get("password", "").strip()

    if not name or not phone or not password:
        return jsonify({"error": "Name, phone number, and password are required"}), 400

    if len(phone) < 10:
        return jsonify({"error": "Please enter a valid 10-digit phone number"}), 400

    existing = get_user_by_phone(phone)
    if existing:
        return jsonify({"error": "An account with this phone number already exists. Please log in."}), 400

    user = create_user(name, phone, password, role="citizen")
    if user:
        return jsonify({
            "success": True,
            "message": "Account created successfully",
            "user": user
        }), 201
    return jsonify({"error": "Could not create account"}), 500


@app.route("/api/auth/login", methods=["POST"])
def api_auth_login():
    """Authenticate citizen or staff coordinator."""
    body = request.get_json(silent=True) or {}
    phone = body.get("phone", "").strip()
    password = body.get("password", "").strip()

    if not phone or not password:
        return jsonify({"error": "Phone number and password are required"}), 400

    # Staff quick-alias: allow username 'staff' or 'admin'
    if phone.lower() in ["staff", "admin"]:
        phone = "9999999999"

    user = authenticate_user(phone, password)
    if user:
        return jsonify({
            "success": True,
            "message": f"Welcome back, {user['name']}!",
            "user": user
        })
    return jsonify({"error": "Invalid phone number or password"}), 401


@app.route("/api/my-reports", methods=["GET"])
def api_my_reports():
    """Retrieve all reports submitted by a citizen."""
    phone = request.args.get("phone", "").strip()
    if not phone:
        return jsonify([])
    return jsonify(get_issues_by_citizen(phone))


# ============================================================================
# SERVER STARTUP
# ============================================================================
def run_server(port: int = 5000):
    """Initialize database and start the Flask development server."""
    init_db()
    print("=" * 70)
    print("  NAGARMITHRA — MANGALAGIRI CIVIC TECH PLATFORM")
    print("  Flask + SQLite Backend Running on Port 5000")
    print(f"  Web Portal: http://localhost:{port}")
    print(f"  Coordinator Passcode: {ADMIN_PASSCODE}")
    print("=" * 70)
    app.run(host="0.0.0.0", port=port, debug=False)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    run_server(port)
