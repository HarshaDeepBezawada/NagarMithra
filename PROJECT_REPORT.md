# MANGALAGIRI CIVIC ISSUE REPORTING PLATFORM
## Comprehensive Academic Project Report & Viva Voce Defense Guide

**Official Tagline:** *"Our Mangalagiri, Our Pride, Our Duty!"*  
**Municipal Jurisdiction:** Mangalagiri-Tadepalli Municipal Corporation (MTMC), Andhra Pradesh, India  
**Target Entity:** Mangalagiri Civic Administration  
**Author/Student:** Second-Year Computer Science & Engineering (Artificial Intelligence)  
**Submission Focus:** Mangalagiri Service Boundary Enforcement, Haversine Spatial Deduplication, Dynamic Civic Prioritization & SLA Compliance Engine  

---

## 1. Executive Summary

Urban municipal corporations require specialized civic-tech systems tailored to their defined service boundaries. **NagarMithra: Mangalagiri Civic Issue Reporting Platform** is an intelligent civic-service website designed exclusively for **Mangalagiri, Andhra Pradesh, India**.

Key highlights of the platform:
1. **Strict Mangalagiri-Only Geographic Boundary:** Uses an authoritative GeoJSON polygon of Mangalagiri and an independent server-side Ray-Casting Point-in-Polygon (PIP) engine. Grievances reported outside Mangalagiri are blocked with a polite explanation.
2. **Zero-Dependency Python REST Server (`server.py`):** Runs on Python's built-in `http.server.HTTPServer` on Port 5000 with zero external framework overhead.
3. **Executive Streamlit Telemetry Dashboard (`app.py`):** Runs on Port 8501 for administrative data science and geospatial analytics.
4. **Haversine Geodesic Deduplication Engine (<100m):** Automatically merges spatial duplicates into master tickets.
5. **Dynamic Civic Priority Formula (0–100 Scale):** Normalizes severity, corroboration, and community upvotes into a 4-tier triage system.
6. **Statutory MTMC Resolution SLAs:** Binds categories to 24–72 hour resolution deadlines with automated breach alerts.
7. **Custom Footer Artwork Integration:** Directly incorporates the provided panoramic sketch artwork featuring Panakala Temple, Handloom Weaver Monument, Mangalagiri Railway Station, ACA Stadium, and AIIMS Mangalagiri with layered contact information.

---

## 2. The Mangalagiri Service Boundary Model

### 2.1 The Ray-Casting Point-in-Polygon (PIP) Algorithm
To determine whether an incoming coordinate $(P_{lat}, P_{lon})$ lies inside the Mangalagiri polygon $V = \{v_1, v_2, \dots, v_n\}$:

1. **Bounding Box Pre-Filtering (Fast Path):**
   $$\text{If } P_{lat} < \min(V_{lat}) \lor P_{lat} > \max(V_{lat}) \lor P_{lon} < \min(V_{lon}) \lor P_{lon} > \max(V_{lon}) \implies \mathbf{False}$$
2. **Ray Intersection Test:**
   An imaginary horizontal ray is extended from $(P_{lat}, P_{lon})$ to $+\infty$ along the longitude axis. For each polygon edge $(v_i, v_{i+1})$:
   $$\text{If } \min(v_{i, lat}, v_{i+1, lat}) < P_{lat} \le \max(v_{i, lat}, v_{i+1, lat}):$$
   $$\text{Longitude Intersect } X = \frac{(P_{lat} - v_{i, lat}) \cdot (v_{i+1, lon} - v_{i, lon})}{v_{i+1, lat} - v_{i, lat}} + v_{i, lon}$$
   $$\text{If } P_{lon} \le X \implies \text{Toggle Intersect Counter}$$
3. **Parity Check:**
   $$\text{Point is Inside } \iff (\text{Total Intersections} \pmod 2) = 1$$

---

## 3. Core Mathematical Formulations

### 3.1 Department Routing & Resolution SLAs (MTMC Mangalagiri)
| Category | Icon | Responsible Division | Statutory SLA |
|---|---|---|---|
| **Pothole** | 🕳️ | MTMC Roads & Traffic Infrastructure Wing | 48 Hours |
| **Garbage Dump** | 🗑️ | MTMC Public Health & Sanitation Wing | 24 Hours |
| **Streetlight Fault** | 💡 | Electricity & Public Lighting (APCPDCL / MTMC) | 36 Hours |
| **Water Leakage** | 🚰 | MTMC Water Works & Drainage Department | 24 Hours |
| **Broken Footpath** | 🚶 | MTMC Town Planning & Walkways Wing | 72 Hours |
| **Public Infrastructure** | 🏛️ | MTMC Public Works & Civic Assets | 48 Hours |
| **Other** | 📋 | MTMC General Grievance Cell | 48 Hours |

### 3.2 Haversine Geodesic Distance Formula
$$\Delta\phi = \text{radians}(lat_2 - lat_1), \quad \Delta\lambda = \text{radians}(lon_2 - lon_1)$$
$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\text{radians}(lat_1)) \cdot \cos(\text{radians}(lat_2)) \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right)$$
$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right)$$
$$d = 6,371,000 \cdot c \quad (\text{metres})$$

**Merging Rule:**
$$\text{If } \text{category}_{\text{in}} = \text{category}_{\text{ticket}} \land \text{status} \neq \text{"Resolved"} \land d \le 100.0\text{ m} \implies \text{MERGE}$$

### 3.3 Dynamic Civic Priority Formula
$$\text{Raw Score} = (\text{Severity} \times 10) + (\text{Report Count} \times 5) + (\text{Upvotes} \times 2)$$
$$\text{Priority Score} = \min(100, \max(0, \text{Raw Score}))$$

---

## 4. Viva Voce Defense Questions & Answers (Tailored for Mangalagiri)

### Q1: Why is this platform restricted exclusively to Mangalagiri?
> **Answer:** *"Urban local bodies like the Mangalagiri-Tadepalli Municipal Corporation (MTMC) manage distinct jurisdictional boundaries and ward boundaries. Operating a city-specific portal ensures high-precision location verification, allows realistic 24-to-72-hour SLA tracking, and prevents administrative confusion with neighboring corporations like Vijayawada (VMC) or Guntur (GMC)."*

### Q2: How do you enforce the Mangalagiri geographic boundary?
> **Answer:** *"We enforce boundary validation at two distinct layers. On the frontend, a GeoJSON boundary polygon is visually rendered in Leaflet.js, and coordinate selections are evaluated immediately to guide the user. On the backend in `server.py` and `boundary.py`, every incoming POST request is independently tested using a Ray-Casting Point-in-Polygon (PIP) algorithm. Even if a user bypasses client scripts, invalid coordinates receive an HTTP 400 Bad Request error."*

### Q3: What landmarks are incorporated into the platform?
> **Answer:** *"The platform incorporates authentic Mangalagiri landmarks represented in our panoramic artwork: the Sri Panakala Lakshmi Narasimha Swamy Temple hill shrine, the Handloom Weavers Colony, the Mangalagiri Railway Station, the ACA International Cricket Stadium, the AIIMS Mangalagiri campus, and TTD Amaravati."*

### Q4: How is citizen privacy protected on the public portal?
> **Answer:** *"Citizen phone numbers and email addresses are not exposed publicly on the tracking portal. Complaints are referenced solely by unique 4-digit public work order IDs (e.g. `NM-1001`), providing full municipal transparency without risking citizen harassment."*

### Q5: How do you handle duplicate complaints for the same road or drain?
> **Answer:** *"Our Haversine spatial deduplication engine checks active complaints of the same category. If a report is filed within 100 metres of an existing open ticket, it automatically merges into that ticket, increments the corroboration count, escalates the priority score, and displays an alert to the citizen."*
