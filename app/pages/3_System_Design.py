"""System Design tracker page."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date
from data import db

st.set_page_config(page_title="System Design", page_icon="\U0001f3d7\ufe0f", layout="wide")

db.init_db()

# ── Solution file mapping ──
SOLUTIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "solutions")

SOLUTION_FILES = {
    "Design a URL Shortener (TinyURL)": "01-url-shortener.md",
    "Design a News Feed / Timeline": "02-news-feed.md",
    "Design a Chat/Messaging System": "03-chat-messaging.md",
    "Design a Rate Limiter": "04-rate-limiter.md",
    "Design a Web Crawler": "05-web-crawler.md",
    "Design a Notification System": "06-notification-system.md",
    "Design a Ride-Sharing Service": "07-ride-sharing.md",
    "Design a Real-Time Location Tracking System": "08-location-tracking.md",
    "Design a Distributed Cache": "09-distributed-cache.md",
    "Design Search Autocomplete / Typeahead": "10-search-autocomplete.md",
    "Design a Distributed Key-Value Store": "11-distributed-kv-store.md",
    "Design a Content Delivery Network (CDN)": "12-cdn.md",
    "Design YouTube / Netflix (Video Streaming)": "13-video-streaming.md",
    "Design Google Maps / Proximity Service": "14-google-maps.md",
    "Design a Distributed Task Scheduler": "15-task-scheduler.md",
    "Design a Metrics/Monitoring System": "16-metrics-monitoring.md",
    "Design a Distributed Log System (Kafka)": "17-distributed-log.md",
    "Design an Object Storage System (S3)": "18-object-storage.md",
    "Design a Container Orchestration System": "19-container-orchestration.md",
    "Design a Load Balancer": "20-load-balancer.md",
    "Design an Ad Click Aggregation System": "21-ad-click-aggregation.md",
    "Design a Hotel/Restaurant Reservation System": "22-reservation-system.md",
    "Design a Distributed File System (GFS/HDFS)": "23-distributed-filesystem.md",
    "Design an ML Feature Store / Training Pipeline": "24-ml-feature-store.md",
    "Design a Multi-Region Deployment System": "25-multi-region.md",
    "Design a Container Orchestration System (K8s Deep Dive)": "26-k8s-deep-dive.md",
    "Design a Control Plane": "27-control-plane.md",
    "Design a Data Plane": "28-data-plane.md",
    "Design a Service Mesh": "29-service-mesh.md",
    "Design a Cloud Load Balancer": "30-cloud-load-balancer.md",
    "Design an Auto-Scaling System": "31-auto-scaling.md",
    "Design a Cluster Scheduler": "32-cluster-scheduler.md",
    "Design a Container Registry": "33-container-registry.md",
    "Design a Multi-Tenant Kubernetes Platform": "34-multi-tenant-k8s.md",
}

st.title("\U0001f3d7\ufe0f System Design")

# ── Sidebar Filters ──
st.sidebar.header("Filters")

selected_category = st.sidebar.selectbox(
    "Category", options=["All", "core", "eks_specific", "ml_infra"]
)

selected_status = st.sidebar.selectbox(
    "Status", options=["All", "not_started", "studying", "reviewed", "confident"]
)

company_filter = st.sidebar.text_input("Company", placeholder="e.g. Meta, Uber")

# ── Build filters dict ──
filters = {}
if selected_category != "All":
    filters["category"] = selected_category
if selected_status != "All":
    filters["status"] = selected_status
if company_filter.strip():
    filters["company"] = company_filter.strip()

topics = db.get_all_system_design(filters if filters else None)

# ── Stats Bar ──
all_topics_unfiltered = db.get_all_system_design()
total_count = len(all_topics_unfiltered)
reviewed_count = sum(
    1 for t in all_topics_unfiltered if t["status"] in ("reviewed", "confident")
)
confident_count = sum(1 for t in all_topics_unfiltered if t["status"] == "confident")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Topics", total_count)
col2.metric("Reviewed", reviewed_count)
col3.metric("Confident", confident_count)
overall_pct = round((reviewed_count / total_count * 100), 1) if total_count > 0 else 0
col4.metric("Overall Progress", f"{overall_pct}%")

# ── Progress Overview by Category ──
st.header("Progress by Category")

category_labels = {"core": "Core", "eks_specific": "EKS-Specific", "ml_infra": "ML Infra"}
category_colors = {"core": "\U0001f7e2", "eks_specific": "\U0001f535", "ml_infra": "\U0001f7e0"}

category_stats = {}
for t in all_topics_unfiltered:
    cat = t["category"]
    if cat not in category_stats:
        category_stats[cat] = {"total": 0, "done": 0}
    category_stats[cat]["total"] += 1
    if t["status"] in ("reviewed", "confident"):
        category_stats[cat]["done"] += 1

prog_cols = st.columns(len(category_stats) if category_stats else 1)
for i, (cat, stat) in enumerate(sorted(category_stats.items())):
    label = category_labels.get(cat, cat)
    icon = category_colors.get(cat, "")
    pct = round(stat["done"] / stat["total"] * 100, 1) if stat["total"] > 0 else 0
    prog_cols[i].metric(f"{icon} {label}", f"{stat['done']}/{stat['total']} ({pct}%)")

# ── Topic Cards ──
st.header("Topics")

if not topics:
    st.info("No topics match the current filters.")

status_options = ["not_started", "studying", "reviewed", "confident"]

for topic in topics:
    cat_label = category_labels.get(topic["category"], topic["category"])
    cat_icon = category_colors.get(topic["category"], "")

    with st.expander(f"{cat_icon} **{topic['title']}** [{cat_label}]"):
        tcol1, tcol2 = st.columns(2)

        current_status = topic["status"]
        new_status = tcol1.selectbox(
            "Status",
            options=status_options,
            index=status_options.index(current_status),
            key=f"sd_status_{topic['id']}",
        )

        current_confidence = topic["confidence"]
        new_confidence = tcol2.slider(
            "Confidence",
            1,
            5,
            max(current_confidence, 1),
            key=f"sd_conf_{topic['id']}",
        )

        if topic["company_tags"]:
            st.write(f"**Companies:** {topic['company_tags']}")

        if topic["last_reviewed"]:
            st.caption(f"Last reviewed: {topic['last_reviewed']}")

        notes = st.text_area(
            "Notes (approach, key components, trade-offs)",
            value=topic["notes"] or "",
            height=150,
            key=f"sd_notes_{topic['id']}",
        )

        if st.button("Save", key=f"sd_save_{topic['id']}"):
            db.update_system_design(
                topic["id"],
                status=new_status,
                confidence=new_confidence,
                notes=notes,
                last_reviewed=date.today().isoformat(),
            )
            st.success(f"Updated '{topic['title']}'!")
            st.rerun()

        # ── Solution View & Download ──
        sol_file = SOLUTION_FILES.get(topic["title"])
        if sol_file:
            sol_path = os.path.join(SOLUTIONS_DIR, sol_file)
            if os.path.exists(sol_path):
                st.divider()
                view_col, dl_col = st.columns([3, 1])
                with dl_col:
                    with open(sol_path, "r", encoding="utf-8") as f:
                        sol_content = f.read()
                    st.download_button(
                        "Download Solution",
                        data=sol_content,
                        file_name=sol_file,
                        mime="text/markdown",
                        key=f"dl_{topic['id']}",
                    )
                with view_col:
                    if st.button("View Full Solution", key=f"view_{topic['id']}"):
                        st.session_state[f"show_sol_{topic['id']}"] = not st.session_state.get(f"show_sol_{topic['id']}", False)

                if st.session_state.get(f"show_sol_{topic['id']}", False):
                    st.markdown(sol_content)

st.caption(f"Showing {len(topics)} of {total_count} topics")
