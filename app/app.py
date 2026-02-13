import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from data import db
from data.seed_data import seed_all

st.set_page_config(page_title="Interview Prep Tracker", page_icon="\U0001f3af", layout="wide")

# -- Database initialization and seeding --
if "db_initialized" not in st.session_state:
    db.init_db()
    if not db.is_seeded():
        seed_all()
    st.session_state["db_initialized"] = True

# -- Sidebar --
with st.sidebar:
    st.title("\U0001f3af Interview Prep Tracker")
    st.caption("Senior/Staff SWE Interview Preparation")
    st.divider()

    coding_stats = db.get_coding_stats()
    sd_stats = db.get_system_design_stats()
    beh_stats = db.get_behavioral_stats()

    st.markdown("**Quick Stats**")
    st.metric("Coding Problems", coding_stats["total"], help="Total coding problems tracked")
    st.metric("System Design Topics", sd_stats["total"], help="Total system design topics")
    st.metric("Behavioral Stories", beh_stats["total"], help="Total behavioral stories")

    st.divider()
    st.markdown(
        "Use the **pages in the sidebar** to navigate between sections. "
        "The Study Plan page tracks your 8-week preparation schedule."
    )

# -- Main page content --
st.title("Welcome to Interview Prep Tracker")
st.write(
    "A comprehensive tool to organize and track your Senior/Staff Software Engineer "
    "interview preparation across coding, system design, and behavioral categories."
)

# Quick stats cards
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Coding")
    st.metric("Total Problems", coding_stats["total"])
    st.metric("Solved / Mastered", f"{coding_stats['solved']} / {coding_stats['mastered']}")
    patterns = coding_stats.get("by_pattern", [])
    if patterns:
        st.caption(f"{len(patterns)} patterns tracked")

with col2:
    st.subheader("System Design")
    st.metric("Total Topics", sd_stats["total"])
    st.metric("Reviewed", sd_stats["reviewed"])

with col3:
    st.subheader("Behavioral")
    st.metric("Total Stories", beh_stats["total"])
    by_cat = beh_stats.get("by_category", [])
    if by_cat:
        filled = sum(1 for c in by_cat if c["count"] > 0)
        st.caption(f"{filled} of 6 categories have stories")

st.divider()

# Page descriptions
st.subheader("Pages")
st.markdown(
    """
- **Coding Problems** -- Browse, filter, and track LeetCode problems by pattern and difficulty.
  Practice with spaced repetition scheduling.
- **System Design** -- Review system design topics across core, EKS-specific, and ML infra categories.
  Track study progress and confidence.
- **Study Plan** -- Follow an 8-week structured study plan with daily tasks.
  Check off completed items and monitor your progress.
- **Behavioral** -- Manage STAR-format stories for behavioral interviews.
  Practice with random question drills.
"""
)
