"""
NagarMithra — Mangalagiri Executive Streamlit Dashboard
========================================================
Runs on Port 8501 via:
    streamlit run app.py

Provides an alternative interactive data science & municipal management
dashboard for Mangalagiri, Andhra Pradesh (MTMC).
"""

import os
import sys
from datetime import datetime, timezone

# Ensure UTF-8 console output
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import streamlit as st
import pandas as pd
import numpy as np

from database import (
    init_db,
    get_all_issues,
    get_stats,
    get_issue,
    update_status,
    insert_issue,
    find_duplicate_candidate,
    merge_duplicate_report,
    get_all_suggestions,
    insert_suggestion,
    DB_PATH
)
from logic import (
    DEPARTMENT_ROUTING,
    calculate_priority_score,
    generate_ticket_id
)
from boundary import (
    is_inside_mangalagiri,
    validate_mangalagiri_coordinates,
    MANGALAGIRI_LOCALITIES
)

# Page Configuration
st.set_page_config(
    page_title="Mangalagiri Civic Dashboard — MTMC",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #0f1f1d;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #0f766e;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("NagarMithra")
st.sidebar.caption("Mangalagiri Civic Issue Reporting Platform • Andhra Pradesh")
st.sidebar.markdown("---")

view_mode = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 City Overview & KPIs",
        "🗺️ Live Mangalagiri GIS Map",
        "📋 Work Order Explorer",
        "📝 Submit New Hazard",
        "🛡️ Municipal Staff Console",
        "💡 Community Ideas Wall"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Web Portal:** Full Single-Page Web App is running at **http://localhost:5000**.")


# -----------------------------------------------------------------------------
# 1. CITY OVERVIEW & KPIS
# -----------------------------------------------------------------------------
if view_mode == "📊 City Overview & KPIs":
    st.markdown('<div class="main-header">Mangalagiri Municipal Telemetry</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">"Our Mangalagiri, Our Pride, Our Duty!" • Serving Mangalagiri, Andhra Pradesh</div>', unsafe_allow_html=True)

    # Show custom footer banner artwork at top of dashboard
    if os.path.exists("frontend/mangalagiri_footer.png"):
        st.image("frontend/mangalagiri_footer.png", use_container_width=True, caption="Panakala Temple, Weavers Monument, Mangalagiri Station, ACA Stadium, AIIMS Mangalagiri & TTD Amaravati")

    stats = get_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Citizen Reports", stats.get("total_reports", 0), help="Cumulative reports including spatial merges")
    with col2:
        st.metric("Master Work Orders", stats.get("master_tickets", 0), help="Unique municipal tickets")
    with col3:
        st.metric("Issues Resolved", stats.get("issues_resolved", 0), delta=f"+{stats.get('issues_resolved', 0)} closed")
    with col4:
        st.metric("SLA Compliance Rate", f"{stats.get('sla_compliance', 0)}%", delta=f"{stats.get('breached_tickets', 0)} breached", delta_color="inverse")

    st.markdown("---")

    issues = get_all_issues()
    if issues:
        df = pd.DataFrame(issues)

        col_left, col_right = st.columns([6, 4])
        with col_left:
            st.subheader("📊 Work Orders by Civic Category")
            cat_counts = df['category'].value_counts()
            st.bar_chart(cat_counts, color="#0f766e")

        with col_right:
            st.subheader("🍩 Status Distribution")
            status_counts = df['status'].value_counts()
            st.dataframe(status_counts, use_container_width=True)

        st.markdown("---")
        st.subheader("🔥 Top 10 Critical Priority Hazards in Mangalagiri")
        top10 = df.sort_values(by="priority_score", ascending=False).head(10)
        st.dataframe(
            top10[[
                "ticket_id", "category", "area", "severity", "report_count",
                "upvotes", "priority_score", "priority_level", "status", "sla_breached"
            ]],
            use_container_width=True
        )


# -----------------------------------------------------------------------------
# 2. LIVE GIS MAP
# -----------------------------------------------------------------------------
elif view_mode == "🗺️ Live Mangalagiri GIS Map":
    st.markdown('<div class="main-header">Mangalagiri Civic Spatial Map</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Haversine GPS Pinning & Hotspot Clustering • Bounded within Mangalagiri, AP</div>', unsafe_allow_html=True)

    issues = get_all_issues()
    if issues:
        df = pd.DataFrame(issues)
        
        col1, col2 = st.columns(2)
        with col1:
            cat_filter = st.selectbox("Filter Category", ["All"] + list(df['category'].unique()))
        with col2:
            status_filter = st.selectbox("Filter Status", ["All", "Open", "In Progress", "Resolved"])

        filtered_df = df.copy()
        if cat_filter != "All":
            filtered_df = filtered_df[filtered_df['category'] == cat_filter]
        if status_filter != "All":
            filtered_df = filtered_df[filtered_df['status'] == status_filter]

        st.caption(f"Showing {len(filtered_df)} geo-tagged tickets verified inside Mangalagiri, Andhra Pradesh:")

        # Map display
        map_df = filtered_df[['latitude', 'longitude']].rename(columns={'latitude': 'lat', 'longitude': 'lon'})
        st.map(map_df, zoom=13)

        st.dataframe(
            filtered_df[['ticket_id', 'category', 'area', 'priority_score', 'status', 'created_at']],
            use_container_width=True
        )


# -----------------------------------------------------------------------------
# 3. WORK ORDER EXPLORER
# -----------------------------------------------------------------------------
elif view_mode == "📋 Work Order Explorer":
    st.markdown('<div class="main-header">Mangalagiri Work Order Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Search, Filter & Inspect Municipal Grievances</div>', unsafe_allow_html=True)

    search_id = st.text_input("🔍 Search by Ticket Reference (e.g. NM-1001)", "").strip().upper()
    
    if search_id:
        issue = get_issue(search_id)
        if issue:
            st.success(f"Ticket Found: {issue['ticket_id']} — {issue['title']}")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Category", issue["category"])
            c2.metric("Status", issue["status"])
            c3.metric("Priority Score", f"{issue['priority_score']} ({issue['priority_level']})")
            c4.metric("SLA Hours", f"{issue['sla_hours']}h")

            st.write(f"**Department:** {issue['department']}")
            st.write(f"**Locality:** {issue['area']} ({issue['latitude']:.6f}, {issue['longitude']:.6f})")
            st.write(f"**Description:** {issue['description']}")
            st.write(f"**Corroborated Submissions:** {issue['report_count']} citizens")
            st.write(f"**Community Upvotes:** {issue['upvotes']}")
            if issue['sla_breached']:
                st.error("⚠️ This ticket has breached its statutory MTMC resolution SLA deadline!")
            else:
                st.info("✅ Currently within standard resolution timeframe.")
        else:
            st.error(f"No ticket found matching '{search_id}'")

    st.markdown("---")
    issues = get_all_issues()
    if issues:
        df = pd.DataFrame(issues)
        st.dataframe(df, use_container_width=True)
        
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Mangalagiri Civic CSV Report",
            csv_data,
            "mangalagiri_civic_data.csv",
            "text/csv"
        )


# -----------------------------------------------------------------------------
# 4. SUBMIT NEW HAZARD
# -----------------------------------------------------------------------------
elif view_mode == "📝 Submit New Hazard":
    st.markdown('<div class="main-header">File a Civic Grievance in Mangalagiri</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Mangalagiri Service Boundary Enforced • Haversine Deduplication (&le; 100m)</div>', unsafe_allow_html=True)

    with st.form("citizen_report_form"):
        col_a, col_b = st.columns(2)
        with col_a:
            category = st.selectbox("Category", list(DEPARTMENT_ROUTING.keys()))
            area = st.selectbox("Mangalagiri Locality / Landmark", list(MANGALAGIRI_LOCALITIES.keys()))
        with col_b:
            coords = MANGALAGIRI_LOCALITIES[area]
            lat = st.number_input("Latitude", value=float(coords["lat"]), format="%.6f")
            lon = st.number_input("Longitude", value=float(coords["lon"]), format="%.6f")

        title = st.text_input("Grievance Title *", placeholder="e.g., Deep dangerous pothole on Panakala Temple Car Street")
        description = st.text_area("Detailed Description", placeholder="Mention landmarks, duration, and obstruction severity in Mangalagiri...")
        severity = st.slider("Observed Hazard Severity (1 = Minor, 5 = Critical Danger)", min_value=1, max_value=5, value=3)

        submitted = st.form_submit_button("Submit Civic Grievance", use_container_width=True)

        if submitted:
            if not title:
                st.error("Please enter a title for the grievance.")
            elif not is_inside_mangalagiri(lat, lon):
                st.error(
                    "❌ **Location Outside Mangalagiri!**\n\n"
                    "This platform currently accepts civic complaints only within the designated Mangalagiri service area, Andhra Pradesh. "
                    "The location you selected does not fall within our supported area. Please select a location inside Mangalagiri to continue."
                )
            else:
                # Run Haversine spatial duplicate check
                candidate, distance = find_duplicate_candidate(category, lat, lon, threshold_m=100.0)

                if candidate:
                    merged = merge_duplicate_report(candidate["ticket_id"])
                    st.warning(
                        f"🤝 **Duplicate Merged into Master Ticket #{merged['ticket_id']}!**\n\n"
                        f"Your report is located within **{distance:.1f} metres** of an active report. "
                        f"Corroboration count escalated to **{merged['report_count']} citizens**. "
                        f"Priority recalculated to **{merged['priority_score']} ({merged['priority_level']})**."
                    )
                else:
                    new_id = generate_ticket_id()
                    created = insert_issue(
                        ticket_id=new_id,
                        category=category,
                        title=title,
                        description=description,
                        severity=severity,
                        area=area,
                        latitude=lat,
                        longitude=lon
                    )
                    st.success(
                        f"🎉 **Master Work Ticket Created: #{created['ticket_id']}!**\n\n"
                        f"Routed to **{created['department']}**. Statutory SLA: **{created['sla_hours']} Hours**."
                    )


# -----------------------------------------------------------------------------
# 5. MUNICIPAL STAFF CONSOLE
# -----------------------------------------------------------------------------
elif view_mode == "🛡️ Municipal Staff Console":
    st.markdown('<div class="main-header">Municipal Staff Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">MTMC Officer Verification & Status Updates</div>', unsafe_allow_html=True)

    issues = get_all_issues()
    ticket_options = [f"{i['ticket_id']} — {i['title'][:40]} [{i['status']}]" for i in issues]

    selected_option = st.selectbox("Choose Work Order Ticket", ticket_options)
    selected_tid = selected_option.split(" — ")[0]
    ticket = get_issue(selected_tid)

    if ticket:
        st.write(f"**Current Status:** `{ticket['status']}` | **Department:** `{ticket['department']}`")
        new_status = st.radio("Update Operational Status", ["Open", "In Progress", "Resolved"], horizontal=True)
        passcode = st.text_input("Staff Security Passcode (default: admin123)", type="password")

        if st.button("Commit Status Update", use_container_width=True):
            if passcode == "admin123":
                updated = update_status(selected_tid, new_status)
                st.success(f"Ticket #{selected_tid} status successfully updated to '{new_status}'!")
                st.rerun()
            else:
                st.error("Incorrect staff security passcode.")


# -----------------------------------------------------------------------------
# 6. COMMUNITY IDEAS WALL
# -----------------------------------------------------------------------------
elif view_mode == "💡 Community Ideas Wall":
    st.markdown('<div class="main-header">Mangalagiri Community Ideas Wall</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Collaborative Citizen Proposals for Mangalagiri</div>', unsafe_allow_html=True)

    with st.expander("➕ Propose a Civic Improvement for Mangalagiri"):
        with st.form("new_idea_form"):
            idea_title = st.text_input("Proposal Title *")
            idea_desc = st.text_area("Detailed Description *")
            idea_author = st.text_input("Your Name / Resident Society", "Anonymous")
            if st.form_submit_button("Post to Ideas Wall"):
                if idea_title and idea_desc:
                    insert_suggestion(idea_title, idea_desc, idea_author)
                    st.success("Your civic proposal has been posted!")
                    st.rerun()
                else:
                    st.error("Please provide both title and description.")

    suggestions = get_all_suggestions()
    for s in suggestions:
        with st.container():
            st.subheader(f"💡 {s['title']}")
            st.write(s['description'])
            st.caption(f"Proposed by **{s['citizen_name']}** on {s['created_at'][:10]}")
            st.markdown("---")