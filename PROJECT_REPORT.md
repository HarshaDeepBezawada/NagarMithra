# NAGARMITHRA (नगरमित्र) — URBAN CIVIC-TECH PLATFORM
## Comprehensive Academic Project Report & Viva Defense Guide

**Official Tagline:** *"Every Report Counts"*  
**Target Municipal Entity:** Greater Hyderabad Municipal Corporation (GHMC) / Urban Civic-Tech  
**Author/Student:** Second-Year Computer Science & Engineering (Artificial Intelligence)  
**Submission Scope:** Automated Spatial Deduplication, Dynamic Civic Prioritization & SLA Compliance Engine  

---

## 1. Executive Summary

Municipal corporations in metropolitan cities face immense challenges in triaging and resolving citizen grievances. Often, multiple citizens report the same road hazard or garbage dump, creating redundant work tickets, misallocating municipal crews, and lacking transparent tracking.

**NagarMithra** is a state-of-the-art urban civic-tech platform that combines:
1. A **Zero-Dependency Python REST Server** (`server.py`) serving an interactive Single-Page Civic Web Portal (`frontend/index.html`).
2. An **Executive Streamlit Analytics Dashboard** (`app.py`) for administrative telemetry.
3. A **Haversine Spatial Great-Circle Deduplication Algorithm** that automatically merges duplicate citizen reports within 100 metres into a single master work ticket.
4. A **Transparent Dynamic Civic Priority Formula (0–100 Scale)** integrating severity, corroborating reports, and public upvotes.
5. An **Automated Statutory Service Level Agreement (SLA) Engine** enforcing resolution deadlines between 24 and 72 hours.
6. A **100% Parameterized SQLite Persistence Layer** guaranteeing zero vulnerability to SQL injection.

---

## 2. Core Mathematical Models & Algorithms

### 2.1 Automated Department Routing & SLA Mapping
Each civic category maps directly to its statutory administrative authority and time limit:

$$\begin{array}{|l|c|l|c|}
\hline
\textbf{Category} & \textbf{Icon} & \textbf{Assigned Department} & \textbf{SLA Deadline} \\
\hline
\text{Pothole} & \text{🕳️} & \text{Roads \& Traffic Infrastructure (GHMC)} & 48\text{ Hours} \\
\text{Garbage Dump} & \text{🗑️} & \text{Sanitation \& Solid Waste Management} & 24\text{ Hours} \\
\text{Streetlight Fault} & \text{💡} & \text{Electricity \& Public Lighting (TSSPDCL)} & 36\text{ Hours} \\
\text{Water Leakage} & \text{🚰} & \text{Water Supply \& Drainage Board (HMWSSB)} & 24\text{ Hours} \\
\text{Broken Footpath} & \text{🚶} & \text{Public Works Department (PWD Walkways)} & 72\text{ Hours} \\
\text{Fallback} & \text{📌} & \text{General Municipal Administration} & 48\text{ Hours} \\
\hline
\end{array}$$

### 2.2 Haversine Great-Circle Spatial Distance & Deduplication
To compute the true geodesic distance $d$ between incoming report coordinates $(lat_1, lon_1)$ and active open tickets $(lat_2, lon_2)$:

$$\Delta\phi = \text{radians}(lat_2 - lat_1), \quad \Delta\lambda = \text{radians}(lon_2 - lon_1)$$

$$a = \sin^2\left(\frac{\Delta\phi}{2}\right) + \cos(\text{radians}(lat_1)) \cdot \cos(\text{radians}(lat_2)) \cdot \sin^2\left(\frac{\Delta\lambda}{2}\right)$$

$$c = 2 \cdot \text{atan2}\left(\sqrt{a}, \sqrt{1 - a}\right)$$

$$d = R \cdot c \quad (\text{where } R = 6,371,000\text{ metres})$$

**Spatial Merging Condition:**
$$\text{If } \text{category}_{\text{in}} = \text{category}_{\text{ticket}} \land \text{status} \neq \text{"Resolved"} \land d \le 100.0\text{ m}:$$
- Incoming grievance is merged into existing master ticket.
- $\text{report\_count} \leftarrow \text{report\_count} + 1$.
- Priority score is dynamically recalculated and escalated.
- Citizen receives confirmation: *"🤝 Duplicate Merged into Master Ticket #NM-XXXX!"*

### 2.3 Dynamic Civic Priority Formula (0–100 Scale)
Combines observed severity, community corroboration, and citizen upvoting:

$$\text{Raw Score} = (\text{Severity} \times 10) + (\text{Report Count} \times 5) + (\text{Upvotes} \times 2)$$

$$\text{Priority Score} = \min(100, \max(0, \text{Raw Score}))$$

**Classification Tiers:**
- **Critical ($\ge 80$ pts):** Immediate crew dispatch (Red badge).
- **High ($60 \le \text{Score} < 80$):** Escalated priority queue (Orange badge).
- **Medium ($40 \le \text{Score} < 60$):** Standard maintenance queue (Yellow badge).
- **Low ($< 40$ pts):** Routine inspection (Green badge).

### 2.4 Service Level Agreement (SLA) & Breach Engine
$$\text{Breached} = \begin{cases} 
\text{False} & \text{if } \text{Status} = \text{"Resolved"} \\
\text{True} & \text{if } (t_{\text{current}} - t_{\text{created}}) > \text{SLA Hours} \\
\text{False} & \text{otherwise}
\end{cases}$$

---

## 3. System Architecture & Tech Stack

```
+---------------------------------------------------------------------------------+
|                                 CLIENT TIER                                     |
|  Single-Page Web Portal (Port 5000)   <--->   Streamlit Dashboard (Port 8501)   |
|  [Tailwind CSS, Leaflet.js, Chart.js]         [Pandas, Folium / Pydeck]         |
+---------------------------------------------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|                                APPLICATION TIER                                 |
|                  server.py (Python Standard http.server.HTTPServer)             |
|                  REST Endpoints: /api/stats, /api/issues, /api/report,          |
|                                  /api/upvote, /api/status, /api/export-csv      |
|                                     |                                           |
|                  logic.py (Haversine, Priority, SLA, Routing Engines)           |
+---------------------------------------------------------------------------------+
                                      |
                                      v
+---------------------------------------------------------------------------------+
|                               PERSISTENCE TIER                                  |
|               database.py (SQLite 3 with Parameterized Queries)                 |
|               Tables: issues (17 columns) | suggestions (4 columns)             |
+---------------------------------------------------------------------------------+
```

---

## 4. Viva Voce Defense Questions & Answers

### Q1: Why did you build the backend using Python's built-in `http.server` rather than an external framework?
> **Answer:** *"Using Python's built-in `http.server` eliminates external web framework vulnerabilities, ensures zero runtime dependencies, guarantees immediate cross-platform portability on Windows/Linux, and demonstrates clear understanding of HTTP protocols, MIME streaming, and RESTful lifecycle management from foundational principles."*

### Q2: What is the computational complexity of the Haversine duplicate check?
> **Answer:** *"For an incoming complaint, the system queries active, non-resolved tickets of the matching category ($N$ tickets, typically indexed by category and status). Evaluating Haversine distance is $O(1)$ constant time per candidate, yielding an overall complexity of $O(N)$. In production with thousands of active tickets, spatial R-tree indexing or bounding-box pre-filtering can optimize this to $O(\log N)$."*

### Q3: How do you prevent SQL Injection attacks?
> **Answer:** *"100% of our SQL queries in `database.py` use SQLite parameterized query placeholders (`?`). User inputs are passed as bound data tuples to the SQLite engine, preventing string concatenation and making SQL injection impossible."*

### Q4: Why is the priority formula bounded at 100?
> **Answer:** *"The formula $\min(100, \max(0, \text{Raw Score}))$ enforces a normalized 0–100 scale. This prevents heavily upvoted issues from destabilizing administrative queue rankings and provides a clear four-tier classification (Low, Medium, High, Critical) suitable for executive triage."*

### Q5: How does the application preserve citizen privacy?
> **Answer:** *"Citizen phone numbers or emails are not publicly published on the tracking page. Complaints are identified solely by a clean 4-digit public ticket reference (e.g., `NM-1001`), allowing full transparency into municipal milestones without exposing personal contact info."*
