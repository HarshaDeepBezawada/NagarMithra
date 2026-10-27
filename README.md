# NagarMitra (नगरमित्र) — Civic Complaint Management System

> **A reliable, transparent, and structured civic grievance management platform connecting citizens with municipal administration.**

---

## 1. Project Overview

**NagarMitra** (meaning *"Friend of the City"*) is a full-stack civic-tech web platform designed to streamline the reporting, tracking, prioritization, and resolution of public infrastructure and municipal issues. Built using Python and Flask, the platform empowers citizens to report civic grievances with photographic evidence and enables administrative teams to triage, update, and resolve issues with an immutable audit trail.

---

## 2. Problem Statement

In many municipal areas, citizens face significant barriers when attempting to report infrastructure problems such as potholes, garbage accumulation, sewage overflows, and broken streetlights:
- Lack of centralized, transparent complaint tracking.
- Absence of reference numbers for citizen follow-up.
- Unstructured intake channels (phone calls, unlogged paper forms, sporadic social media posts).
- Lack of accountability and audit history for administrative actions.
- Opaque grievance resolution pipelines leaving citizens unaware of progress.

---

## 3. Objectives

- **Empower Citizens:** Provide a simple, accessible, mobile-responsive portal to file grievances without compulsory account registration.
- **Ensure Accountability:** Assign a unique reference code (`NM-XXXXXXXX`) to each grievance for real-time tracking without exposing private citizen data.
- **Streamline Administration:** Provide municipal authorities with a secure administrative dashboard featuring live metrics, search, filtering by category/priority/status, and status updates.
- **Maintain Audit Integrity:** Automatically generate an immutable status history record every time a complaint status or priority changes.
- **Academic Rigor:** Adhere to clean software engineering practices (Flask application factory, blueprints, ORM models, CSRF protection, comprehensive automated test suite).

---

## 4. Proposed Solution

NagarMitra establishes a five-stage operational workflow:

$$\text{REPORT} \longrightarrow \text{RECORD} \longrightarrow \text{PRIORITIZE} \longrightarrow \text{RESOLVE} \longrightarrow \text{TRACK}$$

1. **Report:** Citizens submit details (category, title, description, location, severity, and optional photo).
2. **Record:** Server validates all inputs, securely processes uploads, commits to the SQLite database, and returns a unique reference code.
3. **Prioritize:** Administrators review incoming issues via a protected dashboard with real-time counters and filter controls.
4. **Resolve:** Administrators inspect site details, dispatch municipal workers, append administrative resolution notes, and update statuses.
5. **Track:** Citizens check the status anytime using their reference code, seeing verified milestones and resolution notes while their private contact details remain protected.

---

## 5. Features

### Citizen-Facing Features
- **Landing Page:** Live database-backed grievance counters, civic category cards, and workflow walkthrough.
- **Complaint Submission:** Intuitive form supporting name, contact info, issue title, detailed description, category selection, priority level, location address, and optional image attachment.
- **Unique Reference Generation:** Auto-generated cryptographic reference codes (e.g., `NM-A1B2C3D4`).
- **Grievance Tracking:** Real-time status lookup showing dates, status badges, priority, location, and administrative resolution notes.
- **Privacy-Preserving:** Citizen phone numbers and emails are hidden on the public tracking page to prevent scraping and harassment.

### Administrator Features
- **Secure Authentication:** Protected login session with Werkzeug password hashing (PBKDF2/scrypt).
- **Executive Dashboard:** Live metrics displaying Total, Submitted, Acknowledged, In Progress, Resolved, Rejected, and High Priority counts.
- **Triage & Filtering:** Instant filtering by Status, Category, and Priority, combined with text search across reference numbers and titles.
- **Pagination:** Clean, scalable record pagination.
- **Detailed Complaint Review:** Full view of citizen submissions, location, and uploaded photos.
- **Audit-Logged Status Updates:** Transition complaints between Submitted $\rightarrow$ Acknowledged $\rightarrow$ In Progress $\rightarrow$ Resolved / Rejected with mandatory timestamped notes.
- **CSV Data Export:** One-click CSV export of all complaint data for offline reporting and municipal audits.

---

## 6. Technology Stack & Rationale

| Layer | Technology | Rationale |
|---|---|---|
| **Language** | Python 3.14+ | Standard, readable, extensive ecosystem for rapid prototyping and robust backend development. |
| **Backend Framework** | Flask 3.1.3 | Lightweight, modular micro-framework; avoids the unnecessary overhead of monolithic frameworks while enabling enterprise-grade design patterns. |
| **ORM & Database** | Flask-SQLAlchemy 3.1.1 & SQLite | Clean relational abstraction with zero external server dependencies for academic evaluation, easily migrated to PostgreSQL via `DATABASE_URL`. |
| **Forms & Security** | Flask-WTF 1.3.0 & WTForms 3.3.1 | Built-in CSRF protection tokens, robust server-side field validation, and secure file handling. |
| **Authentication** | Werkzeug 3.1.9 | Secure cryptographic password hashing (`generate_password_hash` / `check_password_hash`) and path-traversal-safe file utilities. |
| **Testing** | pytest 9.1.1 | Industry-standard Python testing suite with fixture-based database isolation and comprehensive route coverage. |
| **Frontend** | HTML5, Vanilla CSS3, Jinja2 | Custom, responsive UI with zero bloated third-party dependencies or external CDN vulnerabilities; reliable across offline environments. |

---

## 7. Architecture

NagarMitra follows the **Application Factory** and **Flask Blueprint** architectural patterns to guarantee high cohesion, low coupling, and easy testability:

```
+-------------------------------------------------------------------+
|                           Client Browser                          |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                         Flask Application                         |
|  [ create_app() Factory -> config.py (Dev / Test / Prod Configs)  |
+-------------------------------------------------------------------+
   |                    |                    |                   |
   v                    v                    v                   v
[ Main BP ]     [ Complaints BP ]      [ Auth BP ]          [ Admin BP ]
   /                 /report              /login             /dashboard
                     /track               /logout            /complaint/<id>
                     /success                                /export/csv
   |                    |                    |                   |
   +--------------------+--------------------+-------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|               Data Layer (Flask-SQLAlchemy ORM)                   |
|   Models: Complaint (1) <---> (N) StatusHistory <---> (1) Admin   |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                        SQLite Storage                             |
|          (nagarmitra.db / :memory: in automated testing)          |
+-------------------------------------------------------------------+
```

---

## 8. Directory Structure

```
NagarMitra/
├── app.py                      # Application entry point for development
├── config.py                   # Environment configuration (Dev, Test, Prod)
├── requirements.txt            # Pinned project dependencies
├── README.md                   # Complete project documentation
├── .env.example                # Example environment variable template
├── .gitignore                  # Git exclusion rules
├── nagarmitra.db               # SQLite database file
├── nagarmithra/                # Application package
│   ├── __init__.py             # Application factory & CLI commands
│   ├── extensions.py           # SQLAlchemy & CSRF instances
│   ├── models.py               # ORM Models (Complaint, StatusHistory, Admin)
│   ├── forms.py                # WTForms validation forms
│   ├── main/                   # Public landing page blueprint
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── complaints/             # Citizen complaint reporting & tracking
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── auth/                   # Administrator authentication & sessions
│   │   ├── __init__.py
│   │   └── routes.py
│   └── admin/                  # Admin dashboard, audit logs & CSV export
│       ├── __init__.py
│       └── routes.py
├── static/
│   ├── css/
│   │   └── style.css           # Custom responsive styling (Navy & Teal palette)
│   └── js/
│       └── main.js             # Mobile navigation toggle & flash auto-dismiss
├── templates/
│   ├── base.html               # Master layout template
│   ├── index.html              # Homepage with live counters & category cards
│   ├── report.html             # Complaint submission form
│   ├── success.html            # Confirmation page displaying reference number
│   ├── track.html              # Public complaint lookup page
│   ├── login.html              # Administrator login portal
│   ├── admin/
│   │   ├── dashboard.html      # Administrator management dashboard
│   │   └── complaint_detail.html # Detail review, status update & audit trail
│   └── errors/
│       ├── 404.html            # Not Found error page
│       ├── 413.html            # File size limit exceeded page
│       └── 500.html            # Internal server error page
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Pytest fixtures & isolated in-memory DB
│   ├── test_models.py          # Unit tests for ORM models & relationships
│   ├── test_complaints.py      # Tests for submission, tracking & privacy
│   ├── test_auth.py            # Tests for admin login, logout & access control
│   └── test_admin.py           # Tests for dashboard, status updates & CSV export
└── uploads/                    # Directory for user-uploaded grievance images
```

---

## 9. Database Schema & Relationships

### `complaints` Table
| Column | Type | Constraints / Attributes | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal identifier |
| `reference` | VARCHAR(20) | UNIQUE, NOT NULL, INDEXED | Public tracking reference (`NM-XXXXXXXX`) |
| `citizen_name` | VARCHAR(100) | NOT NULL | Submitter's full name |
| `citizen_contact` | VARCHAR(100) | NOT NULL | Submitter's phone or email |
| `title` | VARCHAR(200) | NOT NULL | Summary of grievance |
| `description` | TEXT | NOT NULL | Detailed breakdown |
| `category` | VARCHAR(50) | NOT NULL | roads, garbage, water, streetlights, drainage, other |
| `priority` | VARCHAR(20) | NOT NULL, DEFAULT 'medium' | low, medium, high, critical |
| `location` | VARCHAR(300) | NOT NULL | Street, landmark, or coordinates |
| `image_filename` | VARCHAR(255) | NULLABLE | Uploaded photo filename |
| `status` | VARCHAR(20) | NOT NULL, DEFAULT 'submitted'| submitted, acknowledged, in_progress, resolved, rejected |
| `admin_notes` | TEXT | NULLABLE | Notes recorded by administrator |
| `created_at` | DATETIME | NOT NULL, UTC | Creation timestamp |
| `updated_at` | DATETIME | NOT NULL, UTC | Last modification timestamp |
| `resolved_at` | DATETIME | NULLABLE, UTC | Resolution timestamp |

### `status_history` Table
| Column | Type | Constraints / Attributes | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal audit record ID |
| `complaint_id` | INTEGER | FOREIGN KEY (`complaints.id`), INDEXED | Linked grievance |
| `old_status` | VARCHAR(20) | NOT NULL | Status before transition |
| `new_status` | VARCHAR(20) | NOT NULL | Status after transition |
| `note` | TEXT | NULLABLE | Administrative action or rationale |
| `admin_id` | INTEGER | FOREIGN KEY (`admins.id`), NULLABLE | Administrator who executed change |
| `created_at` | DATETIME | NOT NULL, UTC | Timestamp of audit entry |

### `admins` Table
| Column | Type | Constraints / Attributes | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Internal admin ID |
| `username` | VARCHAR(80) | UNIQUE, NOT NULL, INDEXED | Administrator username |
| `password_hash` | VARCHAR(256)| NOT NULL | Secure salted cryptographic hash |
| `is_active` | BOOLEAN | NOT NULL, DEFAULT TRUE | Account status flag |
| `created_at` | DATETIME | NOT NULL, UTC | Account creation date |

---

## 10. Step-by-Step Windows CMD Setup & Run Instructions

Follow these exact commands in a standard **Windows Command Prompt (CMD)**:

### Step 1: Open Project Directory
```cmd
cd /d C:\Users\harsh\Documents\NagarMitra
```

### Step 2: Activate the Virtual Environment
```cmd
venv\Scripts\activate.bat
```
*(Your prompt will now display `(venv)` at the beginning).*

### Step 3: Install Required Dependencies
```cmd
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables (Optional for Dev)
To customize configuration or run in production mode, copy `.env.example` to `.env`:
```cmd
copy .env.example .env
```

### Step 5: Initialize Database & Create Administrator Account
The database initializes automatically when the application runs. To create an administrator account using the custom CLI:
```cmd
flask --app app.py create-admin --username admin --password admin123
```
*(Default test account `admin` / `admin123` is already configured in development).*

### Step 6: Run the Application
```cmd
python app.py
```

### Step 7: Access the Web Portal
Open your web browser and navigate to:
- **Public Portal:** [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
- **File a Complaint:** [http://127.0.0.1:5000/complaints/report](http://127.0.0.1:5000/complaints/report)
- **Track a Complaint:** [http://127.0.0.1:5000/complaints/track](http://127.0.0.1:5000/complaints/track)
- **Admin Login:** [http://127.0.0.1:5000/auth/login](http://127.0.0.1:5000/auth/login)
  - **Username:** `admin`
  - **Password:** `admin123`
- **Admin Dashboard:** [http://127.0.0.1:5000/admin/dashboard](http://127.0.0.1:5000/admin/dashboard)

---

## 11. Running the Automated Test Suite

NagarMitra includes an exhaustive 37-test automated test suite using `pytest`. Tests run against an isolated in-memory SQLite database to ensure zero interference with local development data.

Run all tests from the project root:
```cmd
pytest tests/ -v
```

Expected output:
```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1
collected 37 items

tests/test_admin.py::TestDashboard::test_dashboard_loads PASSED          [  2%]
tests/test_admin.py::TestDashboard::test_dashboard_stats PASSED          [  5%]
tests/test_admin.py::TestDashboard::test_dashboard_search PASSED         [  8%]
tests/test_admin.py::TestDashboard::test_dashboard_filter_status PASSED  [ 10%]
tests/test_admin.py::TestDashboard::test_dashboard_filter_no_results PASSED [ 13%]
tests/test_admin.py::TestComplaintDetail::test_detail_page_loads PASSED  [ 16%]
tests/test_admin.py::TestComplaintDetail::test_detail_page_404 PASSED    [ 18%]
tests/test_admin.py::TestStatusUpdate::test_update_status PASSED         [ 21%]
tests/test_admin.py::TestStatusUpdate::test_resolve_complaint PASSED     [ 24%]
tests/test_admin.py::TestCSVExport::test_export_csv PASSED               [ 27%]
tests/test_admin.py::TestEndToEndWorkflow::test_full_workflow PASSED     [ 29%]
tests/test_auth.py::TestLogin::test_login_page_loads PASSED              [ 32%]
tests/test_auth.py::TestLogin::test_login_success PASSED                 [ 35%]
tests/test_auth.py::TestLogin::test_login_wrong_password PASSED          [ 37%]
tests/test_auth.py::TestLogin::test_login_nonexistent_user PASSED        [ 40%]
tests/test_auth.py::TestLogin::test_logout PASSED                        [ 43%]
tests/test_auth.py::TestProtectedRoutes::test_dashboard_requires_login PASSED [ 45%]
tests/test_auth.py::TestProtectedRoutes::test_complaint_detail_requires_login PASSED [ 48%]
tests/test_auth.py::TestProtectedRoutes::test_export_requires_login PASSED [ 51%]
tests/test_complaints.py::TestHomePage::test_home_page_loads PASSED      [ 54%]
tests/test_complaints.py::TestHomePage::test_home_page_stats PASSED      [ 56%]
tests/test_complaints.py::TestComplaintSubmission::test_report_page_loads PASSED [ 59%]
tests/test_complaints.py::TestComplaintSubmission::test_submit_complaint PASSED [ 62%]
tests/test_complaints.py::TestComplaintSubmission::test_submit_complaint_missing_fields PASSED [ 64%]
tests/test_complaints.py::TestComplaintSubmission::test_submit_complaint_short_description PASSED [ 67%]
tests/test_complaints.py::TestComplaintTracking::test_track_page_loads PASSED [ 70%]
tests/test_complaints.py::TestComplaintTracking::test_track_valid_reference PASSED [ 72%]
tests/test_complaints.py::TestComplaintTracking::test_track_invalid_reference PASSED [ 75%]
tests/test_complaints.py::TestPrivacyProtection::test_tracking_hides_contact PASSED [ 78%]
tests/test_models.py::TestGenerateReference::test_format PASSED          [ 81%]
tests/test_models.py::TestGenerateReference::test_uniqueness PASSED      [ 83%]
tests/test_models.py::TestComplaintModel::test_create_complaint PASSED   [ 86%]
tests/test_models.py::TestComplaintModel::test_unique_reference PASSED   [ 89%]
tests/test_models.py::TestComplaintModel::test_status_history_relationship PASSED [ 91%]
tests/test_models.py::TestAdminModel::test_create_admin PASSED           [ 94%]
tests/test_models.py::TestAdminModel::test_unique_username PASSED        [ 97%]
tests/test_models.py::TestStatusHistoryModel::test_create_history PASSED [100%]

======================= 37 passed in 2.59s =======================
```

---

## 12. Complete Demonstration Walkthrough

For an academic project evaluation, follow this live demonstration script:

1. **Visit Home Page (`/`):** Point out the live database counters (Total, Pending, In Progress, Resolved), category grid, and civic workflow explanation.
2. **Submit a Complaint (`/complaints/report`):**
   - Name: `Ramesh Kumar`
   - Contact: `9876543210`
   - Title: `Damaged road and pothole near Sector 4 circle`
   - Description: `Large crater-like pothole causing traffic blockage and two-wheeler accidents.`
   - Category: `Roads & Potholes`
   - Priority: `High`
   - Location: `Sector 4 Circle, Ring Road`
   - Click **Submit Complaint**.
3. **Save Reference Number (`/complaints/success/<ref>`):** Copy the generated reference number (e.g., `NM-A1B2C3D4`).
4. **Track as Citizen (`/complaints/track`):** Paste the reference number. Notice the status is `Submitted`, priority is `High`, but the citizen's phone number is **not visible** for privacy protection.
5. **Log in as Administrator (`/auth/login`):**
   - Username: `admin` | Password: `admin123`
6. **Manage from Dashboard (`/admin/dashboard`):**
   - Show how the counters immediately reflect the new complaint.
   - Filter by `Roads & Potholes` or search by reference code.
   - Click **View** on the complaint.
7. **Execute Administrative Action (`/admin/complaint/<id>`):**
   - Change Status to `In Progress`.
   - Add Note: *"Road inspection team dispatched with repair crew."*
   - Click **Update Complaint**.
   - Show the newly recorded entry in the **Status History** table below with administrator attribution and exact timestamp.
8. **Resolve Complaint:**
   - Change Status to `Resolved`.
   - Add Note: *"Pothole filled with cold asphalt mix. Road cleared."*
   - Click **Update Complaint**.
9. **Verify Public Update (`/complaints/track`):**
   - Log out or open a separate tab.
   - Enter `NM-A1B2C3D4` on the tracking page.
   - Confirm status now shows `Resolved` along with the official resolution notes.
10. **Export Report (`/admin/export/csv`):** Click **Export CSV** on the dashboard to download the complete spreadsheet log.

---

## 13. Security & Data Integrity Measures

- **Password Hashing:** Passwords are never stored in plaintext; Werkzeug PBKDF2/scrypt cryptographic hashing is strictly enforced.
- **CSRF Defense:** All state-modifying POST requests are protected by Flask-WTF CSRF tokens.
- **SQL Injection Prevention:** 100% of queries use the SQLAlchemy ORM; no raw SQL strings or untrusted string interpolation are used.
- **Strict Server-Side Validation:** Form inputs are validated on the server with WTForms (length, required fields, choices), preventing client-side bypass.
- **Path Traversal & Safe Uploads:** Uploaded filenames are sanitized, assigned random UUID names, restricted to approved image extensions (`.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`), and limited to 5 MB via `MAX_CONTENT_LENGTH`.
- **Citizen Privacy:** Citizen phone numbers and emails are visible solely to authenticated administrators and are strictly omitted from public tracking pages.
- **Session Protection:** Administrative endpoints are guarded with the `@login_required` decorator; cookies are configured with `HttpOnly` and `SameSite=Lax`.

---

## 14. Known Limitations

- **Email/SMS Notifications:** Currently, notification is on-demand via the tracking portal rather than automated push SMS/Email alerts.
- **Single Admin Role:** All admin users share equal privileges; departmental sub-roles (e.g., Sanitation Officer vs. Roads Officer) are not yet segregated.
- **Single Database Host:** Configured for SQLite file storage for academic convenience; multi-worker concurrency will benefit from migrating to PostgreSQL.

---

## 15. Future Enhancements

- Integration with Mapbox or Leaflet OpenStreetMap for interactive GPS pin-drop location tagging.
- Automated SMS/WhatsApp notifications via Twilio or government SMS gateways.
- Multi-tier role-based access control (Zonal Officers, Department Heads, Municipal Commissioners).
- Machine-learning-assisted categorization and computer-vision-based pothole severity detection.

---

## 16. Troubleshooting Common Issues

### Issue 1: `ModuleNotFoundError: No module named 'flask'`
**Fix:** Ensure you activated the virtual environment:
```cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### Issue 2: Port 5000 Already in Use
**Fix:** Run on an alternate port:
```cmd
python -c "from app import app; app.run(port=5001)"
```

### Issue 3: Missing Admin Account
**Fix:** Run the CLI command:
```cmd
flask --app app.py create-admin --username admin --password admin123
```

---

## 17. Academic Project Disclaimer

This project, **NagarMitra**, is developed strictly for academic evaluation and demonstration purposes. It is not currently affiliated with, endorsed by, or connected to any real municipal corporation, government department, or official civic complaints portal.
