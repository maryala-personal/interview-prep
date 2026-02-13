import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data import db
from datetime import date

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Preparation Dashboard")

# ── Overall Progress ──
coding_stats = db.get_coding_stats()
sd_stats = db.get_system_design_stats()
beh_stats = db.get_behavioral_stats()
streak = db.get_streak()

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_text = "active today" if streak > 0 else "no activity today"
    st.metric("🔥 Daily Streak", f"{streak} days", delta=delta_text)

with col2:
    solved = coding_stats["solved"]
    total = coding_stats["total"]
    st.metric("Coding Progress", f"{solved}/{total} solved")

with col3:
    reviewed = sd_stats["reviewed"]
    sd_total = sd_stats["total"]
    st.metric("System Design", f"{reviewed}/{sd_total} reviewed")

with col4:
    beh_total = beh_stats["total"]
    filled = sum(1 for s in db.get_all_behavioral_stories() if s.get("situation"))
    st.metric("Behavioral Stories", f"{filled}/{beh_total} written")

# ── Progress Bars ──
st.subheader("Overall Progress")

col_a, col_b, col_c = st.columns(3)
with col_a:
    pct = solved / total if total else 0
    st.progress(pct, text=f"Coding: {solved}/{total} ({pct:.0%})")
with col_b:
    pct_sd = reviewed / sd_total if sd_total else 0
    st.progress(pct_sd, text=f"System Design: {reviewed}/{sd_total} ({pct_sd:.0%})")
with col_c:
    pct_beh = filled / beh_total if beh_total else 0
    st.progress(pct_beh, text=f"Behavioral: {filled}/{beh_total} ({pct_beh:.0%})")

# ── Today's Focus ──
st.divider()
st.subheader("🎯 Today's Focus")

weakest = "coding"
weakest_pct = pct
if pct_sd < weakest_pct:
    weakest = "system_design"
    weakest_pct = pct_sd
if pct_beh < weakest_pct:
    weakest = "behavioral"
    weakest_pct = pct_beh

due_problems = db.get_due_for_review()

if weakest == "coding":
    if due_problems:
        p = due_problems[0]
        st.warning(
            f"**Focus on Coding** — Your weakest area ({pct:.0%} complete). "
            f"Start with: **{p['title']}** ({p['pattern']}, {p['difficulty']}). "
            f"Confidence: {p['confidence']}/5"
        )
    else:
        st.info("**Focus on Coding** — Solve new problems to build your repertoire.")
elif weakest == "system_design":
    st.warning(
        f"**Focus on System Design** — Only {pct_sd:.0%} reviewed. "
        f"Pick a topic and write out your approach, key components, and trade-offs."
    )
else:
    st.warning(
        f"**Focus on Behavioral Stories** — Only {filled}/{beh_total} stories written. "
        f"Write STAR stories for your EKS experience."
    )

# ── This Week's Activity ──
st.divider()
st.subheader("📅 This Week's Activity")

logs = db.get_daily_logs(7)
if logs:
    week_coding = sum(l["coding_count"] for l in logs)
    week_sd = sum(l["system_design_minutes"] for l in logs)
    week_beh = sum(l["behavioral_count"] for l in logs)

    wc1, wc2, wc3 = st.columns(3)
    wc1.metric("Problems Solved", week_coding)
    wc2.metric("System Design (min)", week_sd)
    wc3.metric("Behavioral Practiced", week_beh)
else:
    st.info("No activity logged this week. Start practicing to see stats here!")

# ── Confidence Heatmap by Pattern ──
st.divider()
st.subheader("🔥 Confidence by Pattern")

by_pattern = coding_stats["by_pattern"]
if by_pattern:
    df_pattern = pd.DataFrame(by_pattern)
    df_pattern["completion_pct"] = (df_pattern["done"] / df_pattern["total"] * 100).round(1)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_pattern["pattern"],
        y=df_pattern["avg_confidence"],
        name="Avg Confidence",
        marker_color=df_pattern["avg_confidence"].apply(
            lambda x: "#ff4b4b" if x < 2 else "#ffa726" if x < 3.5 else "#66bb6a"
        ),
        text=df_pattern["avg_confidence"],
        textposition="auto",
    ))
    fig.update_layout(
        xaxis_title="Pattern",
        yaxis_title="Average Confidence (0-5)",
        yaxis_range=[0, 5],
        height=400,
        xaxis_tickangle=-45,
        margin=dict(b=120),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Pattern completion table
    st.dataframe(
        df_pattern[["pattern", "total", "done", "completion_pct", "avg_confidence"]].rename(
            columns={
                "pattern": "Pattern",
                "total": "Total",
                "done": "Solved",
                "completion_pct": "Completion %",
                "avg_confidence": "Avg Confidence",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

# ── Recent Activity Log ──
st.divider()
st.subheader("📋 Recent Activity (Last 30 Days)")

logs_30 = db.get_daily_logs(30)
if logs_30:
    df_logs = pd.DataFrame(logs_30)
    st.dataframe(
        df_logs[["date", "coding_count", "system_design_minutes", "behavioral_count", "notes"]].rename(
            columns={
                "date": "Date",
                "coding_count": "Coding",
                "system_design_minutes": "SD Minutes",
                "behavioral_count": "Behavioral",
                "notes": "Notes",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No activity logged yet. Your daily practice will show up here.")

# ── Log Today's Activity ──
st.divider()
st.subheader("📝 Log Today's Activity")

with st.form("daily_log_form"):
    lc1, lc2, lc3 = st.columns(3)
    coding_count = lc1.number_input("Problems Solved", min_value=0, value=0)
    sd_minutes = lc2.number_input("System Design Minutes", min_value=0, value=0)
    beh_count = lc3.number_input("Behavioral Stories Practiced", min_value=0, value=0)
    notes = st.text_input("Notes (optional)")

    if st.form_submit_button("Log Activity"):
        db.log_daily(coding_count, sd_minutes, beh_count, notes)
        st.success("Activity logged!")
        st.rerun()
