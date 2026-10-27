# MANGALAGIRI CIVIC ISSUE REPORTING PLATFORM
> **Official Tagline:** *"Our Mangalagiri, Our Pride, Our Duty!"*  
> **Target Entity:** Mangalagiri-Tadepalli Municipal Corporation (MTMC) / Urban Civic-Tech  
> **Jurisdiction:** Exclusively serving **Mangalagiri, Andhra Pradesh, India**  
> **Design Philosophy:** Clean, transparent, student-explainable architecture with zero hidden complexity, parameterized SQL queries, strict Ray-Casting GeoJSON boundary enforcement, and a standalone web portal paired with an alternative Streamlit dashboard.

---

## 1. System Architecture & Tech Stack

```
nagarmithra_project/
├── run_website.bat              # 1-click Windows launcher for Full Web Portal (Port 5000)
├── run_streamlit.bat            # 1-click Windows launcher for Streamlit Dashboard (Port 8501)
├── run_tests.bat                # 1-click test runner (pytest)
├── PROJECT_REPORT.md            # Comprehensive academic submission report & viva Q&A
├── EXPLAIN.md                   # 2-minute viva presentation script & worked examples
├── requirements.txt             # Minimal Python requirements
├── README.md                    # Project documentation & setup instructions
├── mangalagiri_boundary.geojson # Official Mangalagiri service area GeoJSON polygon
├── nagarmithra.db               # Seeded SQLite database (100 Mangalagiri records)
├── boundary.py                  # Ray-casting point-in-polygon boundary validation engine
├── logic.py                     # Core algorithms (Routing, Haversine, Priority, SLA)
├── database.py                  # SQLite persistence layer (Parameterized SQL, 2 tables)
├── server.py                    # Zero-dependency Python REST API & Static Server (Port 5000)
├── app.py                       # Streamlit Web Application (Port 8501)
├── seed.py                      # Demo data generator (100 reports across Mangalagiri)
├── test_logic.py                # Automated pytest suite (7 core logic & boundary tests)
└── frontend/
    ├── index.html               # Single-Page Civic Web App (Tailwind, Leaflet.js, Chart.js)
    └── mangalagiri_footer.png   # Custom panoramic artwork visual foundation for footer
```

- **Frontend:** HTML5, Tailwind CSS (via CDN), FontAwesome 6 icons, Plus Jakarta Sans typography, Leaflet.js (OpenStreetMap with Mangalagiri boundary overlay), Chart.js.
- **Backend:** Python 3 standard library `http.server.HTTPServer` with custom `SimpleHTTPRequestHandler` (Zero third-party framework overhead, cross-platform UTF-8 safe).
- **Database:** SQLite 3 (`nagarmithra.db`) with absolute directory path resolution and 100% parameterized SQL (`?` placeholders).
- **Boundary Engine:** Ray-Casting Point-in-Polygon (PIP) algorithm with fast-path bounding-box pre-filtering.
- **Testing:** Pytest 9.x with 100% pass rate.

---

## 2. The Mangalagiri Service Boundary Requirement

### 2.1 Geographic Service Area
The platform exclusively serves the **Mangalagiri** municipal area in Andhra Pradesh, India:
- Center: `[16.4350° N, 80.5580° E]`
- Key localities covered:
  - **Sri Panakala Lakshmi Narasimha Swamy Temple** (Historic Hill Shrine)
  - **Mangalagiri Handloom Weavers Colony** (GI Cotton Fabric Heritage)
  - **AIIMS Mangalagiri Campus** (National Apex Healthcare)
  - **ACA International Cricket Stadium** (Sports Complex)
  - **Mangalagiri Railway Station & Kothapet Old Town**
  - **Chinakakani & NRI General Hospital**
  - **Navuluru & Atmakur Residential Zones**
  - **Yerrabalem / Amaravati Bypass Corridor**
  - **Mangalagiri Eco-Park & Reserve Forest**

### 2.2 Dual-Layer Boundary Validation
Boundary validation is strictly enforced on both **client** and **server**:
1. **Frontend (Leaflet.js):** Clicking or pinning coordinates outside the boundary displays the error modal and disables submission while preserving form inputs.
2. **Backend (`server.py`):** `POST /api/report` executes `validate_mangalagiri_coordinates(lat, lon)` using `boundary.py`. Any attempt to bypass the frontend returns an HTTP `400 Bad Request` with:
   ```json
   {
     "error": "Location Outside Mangalagiri",
     "message": "This platform currently accepts civic complaints only within the designated Mangalagiri service area, Andhra Pradesh. The location you selected does not fall within our supported area. Please select a location inside Mangalagiri to continue."
   }
   ```

---

## 3. The 4 Core Algorithms & Mathematical Models

### 3.1 Automated MTMC Department Routing & Statutory SLAs
| Category | Icon | Assigned Municipal Division | SLA Limit |
|---|---|---|---|
| **Pothole** | 🕳️ | MTMC Roads & Traffic Infrastructure Wing | **48 Hours** |
| **Garbage Dump** | 🗑️ | MTMC Public Health & Sanitation Wing | **24 Hours** |
| **Streetlight Fault** | 💡 | Electricity & Public Lighting (APCPDCL / MTMC) | **36 Hours** |
| **Water Leakage** | 🚰 | MTMC Water Works & Drainage Department | **24 Hours** |
| **Broken Footpath** | 🚶 | MTMC Town Planning & Walkways Wing | **72 Hours** |
| **Public Infrastructure** | 🏛️ | MTMC Public Works & Civic Assets | **48 Hours** |
| **Other** | 📋 | MTMC General Grievance Cell | **48 Hours** |

### 3.2 Haversine Spatial Great-Circle Deduplication (<100 Metres)
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\text{lat}_1) \cdot \cos(\text{lat}_2) \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$d = R \cdot 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right) \quad (R = 6,371,000\text{ m})$$
- If an active ticket of the same category is found within **100 metres**, the report is automatically **merged** into the master ticket, `report_count` increments, and the priority score escalates.

### 3.3 Dynamic Civic Priority Formula (0–100 Scale)
$$\text{Raw Score} = (\text{Severity} \times 10) + (\text{Report Count} \times 5) + (\text{Upvotes} \times 2)$$
$$\text{Priority Score} = \min(100, \max(0, \text{Raw Score}))$$
- **Critical:** $\ge 80$ points (Red badge)
- **High:** $60 \le \text{Score} < 80$ (Orange badge)
- **Medium:** $40 \le \text{Score} < 60$ (Yellow badge)
- **Low:** $< 40$ points (Green badge)

### 3.4 Service Level Agreement (SLA) & Breach Engine
$$\text{Breached} = (\text{Status} \neq \text{"Resolved"}) \land ((\text{Current Time} - \text{Created Time}) > \text{SLA Hours})$$
Overdue tickets display an animated **⚠️ SLA Breached** alert.

---

## 4. Custom Footer Artwork Integration

The website footer is built directly upon the supplied panoramic sketch artwork:
- **Image File:** `frontend/mangalagiri_footer.png`
- **Features depicted in artwork:** Sri Panakala Lakshmi Narasimha Swamy Temple, Weavers Monument, Mangalagiri Railway Station, ACA Stadium, AIIMS Mangalagiri, Amrita, and TTD Amaravati.
- **Layered Contact Information:**
  - Tagline: *"Our Mangalagiri, Our Pride, Our Duty!"*
  - Civic Support Email: `support.mangalagiri@nagarmithra.org` (clickable `mailto:`)
  - Citizen Helpline: `08645-230000` (clickable `tel:`)
  - Emergency Discom: `1912` | Police / Fire: `100 / 101`

---

## 5. Launchers & Operational Commands

### 1. Launch Full Web Portal (Recommended)
Double click `run_website.bat` OR run:
```cmd
python server.py
```
> **Serves at:** [http://localhost:5000](http://localhost:5000)

### 2. Launch Streamlit Dashboard (Alternative)
Double click `run_streamlit.bat` OR run:
```cmd
streamlit run app.py
```
> **Serves at:** [http://localhost:8501](http://localhost:8501)

### 3. Execute Test Suite
Double click `run_tests.bat` OR run:
```cmd
pytest test_logic.py -v
```

### 4. Re-seed Sample Data (100 Mangalagiri Records)
```cmd
python seed.py
```

### Staff Console Passcode
- **Passcode:** `admin123`
