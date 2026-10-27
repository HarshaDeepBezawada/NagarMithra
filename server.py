"""
NagarMithra — Mangalagiri REST API & Static Web Server
======================================================
Zero-dependency Python standard library server (http.server.HTTPServer)
serving the Mangalagiri Civic Web Portal on Port 5000.

Features:
- Mandatory geotagged photo verification (EXIF GPS parsing)
- Strict Mangalagiri geographic boundary enforcement
- Haversine spatial duplicate detection (<100m)
- Dynamic priority scoring (0-100)
- Statutory MTMC SLA monitoring
- GeoJSON boundary streaming & location validation endpoints
- Safe static file delivery (including custom footer artwork)
"""

import os
import sys
import json
import base64
import csv
import io
import mimetypes
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
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

# Admin passcode for municipal staff console
ADMIN_PASSCODE = "admin123"


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


class NagarMithraRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP Request Handler for the Mangalagiri Civic Portal."""

    server_version = "MangalagiriCivicPortal/2.1"

    def _send_json(self, status_code: int, data: dict | list):
        """Send a JSON HTTP response with UTF-8 encoding and CORS headers."""
        response_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(response_bytes)

    def _send_file(self, file_path: str, content_type: str = None):
        """Safely stream a static file with appropriate MIME type."""
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            self._send_json(404, {"error": "File not found"})
            return

        if not content_type:
            content_type, _ = mimetypes.guess_type(file_path)
            content_type = content_type or "application/octet-stream"

        with open(file_path, "rb") as f:
            content = f.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        """Route GET requests for frontend pages, static assets, and REST APIs."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        # 1. Root: Serve Single-Page App
        if path == "" or path == "/":
            index_path = os.path.join(FRONTEND_DIR, "index.html")
            self._send_file(index_path, "text/html; charset=utf-8")
            return

        # 2. Custom Footer Image delivery
        if path in ["/mangalagiri_footer.png", "/footer.png"]:
            footer_path = os.path.join(FRONTEND_DIR, "mangalagiri_footer.png")
            if not os.path.exists(footer_path):
                footer_path = os.path.join(BASE_DIR, "static", "images", "mangalagiri_footer.png")
            self._send_file(footer_path, "image/png")
            return

        # 3. Uploaded image delivery
        if path.startswith("/uploads/"):
            filename = os.path.basename(path)
            file_path = os.path.join(UPLOAD_DIR, filename)
            self._send_file(file_path)
            return

        # 4. GET /api/boundary (GeoJSON polygon for Mangalagiri service boundary)
        if path == "/api/boundary":
            geojson = get_boundary_geojson_dict()
            self._send_json(200, geojson)
            return

        # 5. GET /api/localities (List of verified Mangalagiri landmarks & localities)
        if path == "/api/localities":
            self._send_json(200, MANGALAGIRI_LOCALITIES)
            return

        # 6. GET /api/stats
        if path == "/api/stats":
            stats = get_stats()
            self._send_json(200, stats)
            return

        # 7. GET /api/issues
        if path == "/api/issues":
            status_filter = query.get("status", [None])[0]
            cat_filter = query.get("category", [None])[0]
            issues = get_all_issues(status=status_filter, category=cat_filter)
            self._send_json(200, issues)
            return

        # 8. GET /api/issues/<ticket_id>
        if path.startswith("/api/issues/"):
            ticket_id = path.split("/")[-1].upper()
            issue = get_issue(ticket_id)
            if issue:
                self._send_json(200, issue)
            else:
                self._send_json(404, {"error": f"Ticket {ticket_id} not found"})
            return

        # 9. GET /api/suggestions
        if path == "/api/suggestions":
            suggestions = get_all_suggestions()
            self._send_json(200, suggestions)
            return

        # 10. GET /api/export-csv
        if path == "/api/export-csv":
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
            csv_bytes = output.getvalue().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=mangalagiri_civic_data.csv")
            self.send_header("Content-Length", str(len(csv_bytes)))
            self.end_headers()
            self.wfile.write(csv_bytes)
            return

        self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        """Route POST requests for complaint submission, location checks, upvotes, status."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self._send_json(400, {"error": "Invalid JSON payload"})
            return

        # 1. POST /api/validate-location (Pre-flight location boundary check)
        if path == "/api/validate-location":
            try:
                lat = float(body.get("latitude"))
                lon = float(body.get("longitude"))
            except (TypeError, ValueError):
                self._send_json(400, {"valid": False, "message": "Invalid latitude or longitude."})
                return

            is_valid, message = validate_mangalagiri_coordinates(lat, lon)
            self._send_json(200, {
                "valid": is_valid,
                "message": message,
                "latitude": lat,
                "longitude": lon
            })
            return

        # 2. POST /api/report (Complaint submission with MANDATORY Geotagged Photo + Mangalagiri check)
        if path == "/api/report":
            category = body.get("category", "").strip()
            title = body.get("title", "").strip()
            description = body.get("description", "").strip()
            severity = int(body.get("severity", 3))
            area = body.get("area", "Panakala Temple Area").strip()
            photo_data = body.get("photo_data", "")

            # MANDATORY REQUIREMENT: Geotagged photo input is NOT optional
            if not photo_data or "base64," not in photo_data:
                self._send_json(400, {
                    "error": "Geotagged Photo Required",
                    "message": "Uploading a photo is mandatory. Only geotagged images are accepted."
                })
                return

            # Extract image raw bytes from base64
            try:
                header, encoded = photo_data.split("base64,", 1)
                img_bytes = base64.b64decode(encoded)
            except Exception:
                self._send_json(400, {
                    "error": "Invalid Photo Format",
                    "message": "The uploaded photo data could not be processed. Please upload a valid image."
                })
                return

            # Check EXIF GPS metadata from uploaded photo
            exif_lat, exif_lon = extract_exif_gps_from_bytes(img_bytes)

            try:
                # If EXIF GPS coordinates exist, use them as authoritative
                if exif_lat is not None and exif_lon is not None:
                    lat = float(exif_lat)
                    lon = float(exif_lon)
                else:
                    # Use client-tagged coordinates from device location
                    lat = float(body.get("latitude"))
                    lon = float(body.get("longitude"))
            except (TypeError, ValueError):
                self._send_json(400, {"error": "Invalid GPS coordinates."})
                return

            if not category or not title:
                self._send_json(400, {"error": "Category and Title are required"})
                return

            # CRITICAL REQUIREMENT: Independent Server-Side Boundary Validation
            is_valid_loc, boundary_msg = validate_mangalagiri_coordinates(lat, lon)
            if not is_valid_loc:
                self._send_json(400, {
                    "error": "Location Outside Mangalagiri",
                    "message": boundary_msg,
                    "latitude": lat,
                    "longitude": lon
                })
                return

            # Save uploaded photo to uploads directory
            saved_photo_path = ""
            try:
                ext = "jpg"
                if "png" in header:
                    ext = "png"
                elif "webp" in header:
                    ext = "webp"
                img_filename = f"{generate_ticket_id().lower()}_{uuid.uuid4().hex[:6]}.{ext}"
                full_path = os.path.join(UPLOAD_DIR, img_filename)
                with open(full_path, "wb") as img_file:
                    img_file.write(img_bytes)
                saved_photo_path = f"/uploads/{img_filename}"
            except Exception as ex:
                print(f"Error saving image: {ex}")

            # Spatial Duplicate Check (<100m threshold, same category, not resolved)
            duplicate_candidate, distance = find_duplicate_candidate(category, lat, lon, threshold_m=100.0)

            if duplicate_candidate:
                # Merge into existing ticket
                updated_ticket = merge_duplicate_report(duplicate_candidate["ticket_id"])
                self._send_json(200, {
                    "status": "merged",
                    "ticket_id": updated_ticket["ticket_id"],
                    "distance_metres": round(distance, 1),
                    "message": f"🤝 Duplicate Merged into Master Ticket #{updated_ticket['ticket_id']}! Location is within {round(distance, 1)}m of an existing Mangalagiri report. Priority escalated.",
                    "ticket": updated_ticket
                })
                return

            # Create new master ticket
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
                photo_path=saved_photo_path
            )

            self._send_json(201, {
                "status": "created",
                "ticket_id": new_ticket["ticket_id"],
                "message": f"🎉 Master Ticket #{new_ticket['ticket_id']} Created Successfully in Mangalagiri! SLA Target: {new_ticket['sla_hours']} Hours.",
                "ticket": new_ticket
            })
            return

        # 3. POST /api/upvote
        if path == "/api/upvote":
            ticket_id = body.get("ticket_id", "").strip().upper()
            if not ticket_id:
                self._send_json(400, {"error": "ticket_id required"})
                return

            updated = increment_upvotes(ticket_id)
            if updated:
                self._send_json(200, {
                    "success": True,
                    "ticket_id": ticket_id,
                    "upvotes": updated["upvotes"],
                    "priority_score": updated["priority_score"],
                    "priority_level": updated["priority_level"],
                    "ticket": updated
                })
            else:
                self._send_json(404, {"error": f"Ticket {ticket_id} not found"})
            return

        # 4. POST /api/status (Authenticated Staff Console)
        if path == "/api/status":
            ticket_id = body.get("ticket_id", "").strip().upper()
            new_status = body.get("status", "").strip()
            password = body.get("password", "").strip()

            if password != ADMIN_PASSCODE:
                self._send_json(401, {"error": "Invalid staff authentication passcode"})
                return

            if new_status not in ["Open", "In Progress", "Resolved"]:
                self._send_json(400, {"error": "Status must be Open, In Progress, or Resolved"})
                return

            updated = update_status(ticket_id, new_status)
            if updated:
                self._send_json(200, {
                    "success": True,
                    "message": f"Ticket {ticket_id} status updated to {new_status}",
                    "ticket": updated
                })
            else:
                self._send_json(404, {"error": f"Ticket {ticket_id} not found"})
            return

        # 5. POST /api/suggestions
        if path == "/api/suggestions":
            title = body.get("title", "").strip()
            desc = body.get("description", "").strip()
            author = body.get("citizen_name", "Anonymous").strip() or "Anonymous"

            if not title or not desc:
                self._send_json(400, {"error": "Title and Description are required"})
                return

            item = insert_suggestion(title, desc, author)
            self._send_json(201, item)
            return

        self._send_json(404, {"error": "Endpoint not found"})


def run_server(port: int = 5000):
    """Start the standard-library HTTP server."""
    init_db()
    server_address = ("", port)
    httpd = HTTPServer(server_address, NagarMithraRequestHandler)
    print("=" * 70)
    print(f"  MANGALAGIRI CIVIC ISSUE REPORTING PLATFORM — ANDHRA PRADESH")
    print(f"  Serving Mangalagiri Service Area Exclusively")
    print(f"  Web Portal: http://localhost:{port}")
    print(f"  Admin Passcode: {ADMIN_PASSCODE}")
    print(f"  Press Ctrl+C to terminate the server")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server cleanly...")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
