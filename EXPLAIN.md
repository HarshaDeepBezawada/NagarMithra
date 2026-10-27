# NAGARMITHRA — 2-MINUTE VIVA PRESENTATION SCRIPT & WORKED EXAMPLES

---

## Part 1: The 2-Minute Word-for-Word Viva Presentation Script

> *"Good morning/afternoon, respected professors.*
>
> *My name is Harsh, and I am presenting **NagarMithra** — an intelligent urban civic-tech grievance platform built for the **Greater Hyderabad Municipal Corporation (GHMC)** under the tagline **'Every Report Counts'**.*
>
> *The fundamental problem in current municipal grievance systems is two-fold:*
> *First, citizens file duplicate complaints for the exact same road or garbage hazard, which overwhelms municipal control rooms.*
> *Second, civic prioritization is often arbitrary and lacks transparent accountability.*
>
> *To solve this, I designed and implemented a four-engine computational architecture:*
>
> 1. *First, an **Automated Haversine Geodesic Deduplication Engine**: When a citizen reports a problem, the server calculates great-circle distance against active tickets. If another report of the same category exists within **100 metres**, it automatically merges the new report into the existing master ticket, increments the corroboration count, and notifies the citizen instead of creating duplicate work orders.*
>
> 2. *Second, a **Dynamic Civic Priority Formula** on a 0-to-100 scale:*  
>    $$\text{Priority} = \min(100, (\text{Severity} \times 10) + (\text{Report Count} \times 5) + (\text{Upvotes} \times 2))$$  
>    *This guarantees that issues with higher severity, more citizen reports, and community upvotes rise to the top of the municipal dispatch queue.*
>
> 3. *Third, an **Automated Department Routing & SLA Engine**: Civic categories map directly to statutory deadlines — 24 hours for water leaks and garbage, 36 hours for streetlights, and 48 hours for potholes. Any ticket exceeding its deadline automatically triggers an animated **⚠️ SLA Breached** alert.*
>
> 4. *Fourth, an accessible dual-interface deployment:*
>    *A zero-dependency **Single-Page Web Portal on Port 5000** featuring interactive **Leaflet.js GIS maps** and **Chart.js analytics**, paired with an **Executive Streamlit Dashboard on Port 8501**.*
>
> *All database operations use 100% parameterized SQLite queries, and our business logic is verified by automated pytest unit tests with a 100% pass rate.*
>
> *Thank you, and I would now be happy to demonstrate the live system or answer questions on the mathematical models."*

---

## Part 2: Step-by-Step Worked Mathematical Examples

### Example 1: Haversine Spatial Duplicate Detection
Suppose an active Pothole ticket exists at Banjara Hills:
- Ticket `NM-1001`: $\text{lat}_1 = 17.415600^\circ$, $\text{lon}_1 = 78.435000^\circ$

A citizen reports a Pothole nearby:
- Incoming Report: $\text{lat}_2 = 17.415850^\circ$, $\text{lon}_2 = 78.435200^\circ$

**Step 1:** Convert degree differences to radians:
- $\Delta\phi = \text{radians}(17.415850 - 17.415600) = \text{radians}(0.000250) \approx 0.0000043633\text{ rad}$
- $\Delta\lambda = \text{radians}(78.435200 - 78.435000) = \text{radians}(0.000200) \approx 0.0000034907\text{ rad}$

**Step 2:** Compute intermediate Haversine term $a$:
- $\sin^2(\Delta\phi / 2) \approx (0.0000021817)^2 \approx 4.76 \times 10^{-12}$
- $\cos(\phi_1) \approx \cos(17.4156^\circ) \approx 0.95418$
- $\cos(\phi_2) \approx \cos(17.41585^\circ) \approx 0.95418$
- $\sin^2(\Delta\lambda / 2) \approx (0.0000017453)^2 \approx 3.05 \times 10^{-12}$
- $a = 4.76 \times 10^{-12} + (0.95418 \times 0.95418 \times 3.05 \times 10^{-12}) \approx 7.54 \times 10^{-12}$

**Step 3:** Angular distance $c$:
- $c = 2 \cdot \text{atan2}(\sqrt{a}, \sqrt{1 - a}) \approx 2 \times 2.746 \times 10^{-6} \approx 5.492 \times 10^{-6}\text{ rad}$

**Step 4:** Surface distance $d$:
- $d = 6,371,000 \times 5.492 \times 10^{-6} \approx \mathbf{34.98\text{ metres}}$

**Decision:**
Since $34.98\text{ m} \le 100.0\text{ m}$ and both are Potholes, the system **merges** the report into `NM-1001`!

---

### Example 2: Dynamic Priority Score Calculation
Suppose `NM-1001` initially has:
- Severity = 4 (Severe Hazard)
- Report Count = 1
- Upvotes = 0

$$\text{Initial Raw Score} = (4 \times 10) + (1 \times 5) + (0 \times 2) = 40 + 5 + 0 = 45\text{ pts (Medium)}$$

Now, after 2 duplicate reports merge and 12 citizens upvote:
- Severity = 4
- Report Count = $1 + 2 = 3$
- Upvotes = 12

$$\text{Escalated Raw Score} = (4 \times 10) + (3 \times 5) + (12 \times 2) = 40 + 15 + 24 = 79\text{ pts (High)}$$

If one more citizen corroborates ($+5$ pts):
$$\text{New Raw Score} = 79 + 5 = \mathbf{84\text{ pts (Critical — Red Badge)}}$$
The ticket automatically enters the municipal emergency triage list!
