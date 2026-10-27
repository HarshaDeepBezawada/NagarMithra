# NagarMithra — Civic Web Portal
> **Official Tagline:** *"Every Report Counts"*  
> **Target Entity:** Greater Hyderabad Municipal Corporation (GHMC) / Urban Civic-Tech  
> **Design Philosophy:** Clean, transparent, student-explainable architecture with zero hidden complexity, parameterized SQL queries, and a standalone web portal paired with an alternative Streamlit dashboard.

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
├── nagarmithra.db               # Seeded SQLite database
├── logic.py                     # Core algorithms (Routing, Haversine, Priority, SLA)
├── database.py                  # SQLite persistence layer (Parameterized SQL, 2 tables)
├── server.py                    # Zero-dependency Python REST API & Static Server (Port 5000)
├── app.py                       # Streamlit Web Application (Port 8501)
├── seed.py                      # Demo data generator (100 reports across Hyderabad)
├── test_logic.py                # Automated pytest suite (5 core logic tests)
└── frontend/
    └── index.html               # Single-Page Civic Web App (Tailwind, Leaflet.js, Chart.js)
```

- **Frontend:** HTML5, Tailwind CSS (via CDN), FontAwesome 6 icons, Plus Jakarta Sans typography, Leaflet.js (OpenStreetMap), Chart.js (analytics).
- **Backend:** Python 3 standard library `http.server.HTTPServer` with custom `SimpleHTTPRequestHandler` (Zero third-party framework overhead, cross-platform UTF-8 safe).
- **Database:** SQLite 3 (`nagarmithra.db`) with absolute directory path resolution and 100% parameterized SQL (`?` placeholders).
- **Testing:** Pytest 9.x with 100% pass rate.

---

## 2. The 4 Core Algorithms & Mathematical Models

### 2.1 Automated Department Routing & Resolution SLAs
Maps incoming civic categories directly to their responsible administrative division and statutory resolution deadline:

| Category | Icon | Assigned Department | SLA Deadline |
|---|---|---|---|
| **Pothole** | 🕳️ | Roads & Traffic Infrastructure (GHMC) | 48 Hours |
| **Garbage Dump** | 🗑️ | Sanitation & Solid Waste Management | 24 Hours |
| **Streetlight Fault** | 💡 | Electricity & Public Lighting (TSSPDCL) | 36 Hours |
| **Water Leakage** | 🚰 | Water Supply & Drainage Board (HMWSSB) | 24 Hours |
| **Broken Footpath** | 🚶 | Public Works Department (PWD Walkways) | 72 Hours |
| **Fallback** | 📌 | General Municipal Administration | 48 Hours |

### 2.2 Haversine Spatial Duplicate Detection (<100 Metres)
Prevents duplicate work orders by calculating the spherical great-circle distance between an incoming report $(lat_1, lon_1)$ and active open tickets $(lat_2, lon_2)$:

$$\Delta\phi = \text{radians}(lat_2 - lat_1), \quad \Delta\lambda = \text{radians}(lon_2 - lon_1)$$
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\text{radians}(lat_1)) \cdot \cos(\text{radians}(lat_2)) \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right)$$
$$d = R \cdot c \quad (\text{where } R = 6,371,000\text{ metres})$$

- **Merging Condition:** If `category_incoming == category_existing` AND `status != "Resolved"` AND $d \le 100.0\text{ m}$:
  - The incoming complaint merges into the existing master ticket.
  - `report_count = report_count + 1`.
  - The priority score is dynamically recalculated and escalated.
  - The citizen receives an alert: *"🤝 Duplicate Merged into Master Ticket #NM-XXXX!"*
- **Unique Condition ($d > 100\text{ m}$ or different category):**
  - A new master ticket `#NM-XXXX` (random 4-digit ID) is created.

### 2.3 Dynamic Civic Priority Formula (0–100 Scale)
Combines severity, community corroboration (report volume), and public upvotes:

$$\text{Raw Score} = (\text{Severity} \times 10) + (\text{Report Count} \times 5) + (\text{Upvotes} \times 2)$$
$$\text{Priority Score} = \min(100, \max(0, \text{Raw Score}))$$

**Severity Input Scale (1 to 5):**
- 1 = Minor Inconvenience (+10)
- 2 = Moderate Obstruction (+20)
- 3 = Serious Hazard (+30)
- 4 = Severe Hazard (+40)
- 5 = Critical Danger (+50)

**Classification Tiers:**
- **Critical:** $\ge 80$ points (Red badge)
- **High:** $60 \le \text{Score} < 80$ (Orange badge)
- **Medium:** $40 \le \text{Score} < 60$ (Yellow badge)
- **Low:** $< 40$ points (Green badge)

### 2.4 Service Level Agreement (SLA) & Breach Engine
$$\text{Breached} = \begin{cases} 
\text{False} & \text{if } \text{Status} = \text{"Resolved"} \\
\text{True} & \text{if } (\text{Current Time} - \text{Created Time}) > \text{SLA Hours} \\
\text{False} & \text{otherwise}
\end{cases}$$

Overdue tickets display an animated ⚠️ SLA Breached indicator on both the public tracking page and the municipal staff console.

---

## 3. Geographic Coordinates & Hotspots (Hyderabad)

| Hotspot Name | Zone Characteristic | Latitude | Longitude |
|---|---|---|---|
| **Banjara Hills** | Commercial & Residential Arterial | 17.415600 | 78.435000 |
| **Madhapur** | IT Corridor / Hitec City | 17.448300 | 78.391500 |
| **Gachibowli** | Financial District & Outer Ring Road | 17.440100 | 78.348900 |
| **Charminar** | High-Density Historic Commercial Core | 17.361600 | 78.474700 |
| **Kukatpally** | High-Density Residential (KPHB) | 17.494800 | 78.399600 |

---

## 4. Launchers & Operational Commands

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

### 4. Re-seed Sample Data (100 Hyderabad Records)
```cmd
python seed.py
```

### Staff Console Passcode
- **Passcode:** `admin123`
