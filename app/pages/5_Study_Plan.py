import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import streamlit as st
from datetime import date, timedelta
from data import db

st.set_page_config(page_title="Study Plan", page_icon="📅", layout="wide")

st.title("📅 8-Week Study Plan")

WEEK_LABELS = {
    1: "Week 1: Foundations (Arrays, Pointers, Search)",
    2: "Week 2: Core Algorithms (DP, Backtracking, Greedy)",
    3: "Week 3: Advanced Patterns (Graphs, Trees, Heaps)",
    4: "Week 4: Data Structures & Design",
    5: "Week 5: Spaced Review & EKS Deep Dive",
    6: "Week 6: Company-Specific Practice",
    7: "Week 7: Full Mock Interviews",
    8: "Week 8: Final Review & Polish",
}

# ── Start Date ──
col1, col2 = st.columns([1, 3])
with col1:
    start_date = st.date_input("Plan Start Date", value=date.today())
    if "prev_start_date" not in st.session_state:
        st.session_state.prev_start_date = start_date
    if start_date != st.session_state.prev_start_date:
        db.set_study_start_date(start_date.isoformat())
        st.session_state.prev_start_date = start_date

# Calculate current week
days_elapsed = (date.today() - start_date).days
current_week = max(1, min(8, (days_elapsed // 7) + 1))

with col2:
    if days_elapsed < 0:
        st.info(f"Plan starts in {-days_elapsed} days")
    elif days_elapsed > 55:
        st.success("Plan completed! Review and continue practicing.")
    else:
        st.info(f"You're in **{WEEK_LABELS[current_week]}** (Day {days_elapsed + 1})")

# ── Get Plan Data ──
plan_data = db.get_study_plan()

# Group by week
weeks = {}
for task in plan_data:
    w = task["week"]
    if w not in weeks:
        weeks[w] = []
    weeks[w].append(task)

# ── Overall Progress ──
total_tasks = len(plan_data)
completed_tasks = sum(1 for t in plan_data if t["completed"])
pct = completed_tasks / total_tasks if total_tasks else 0

st.progress(pct, text=f"Overall: {completed_tasks}/{total_tasks} tasks completed ({pct:.0%})")

st.divider()

# ── Weekly Cards ──
for week_num in range(1, 9):
    label = WEEK_LABELS[week_num]
    tasks = weeks.get(week_num, [])
    week_completed = sum(1 for t in tasks if t["completed"])
    week_total = len(tasks)
    week_pct = week_completed / week_total if week_total else 0

    is_current = (week_num == current_week) and (0 <= days_elapsed <= 55)

    # Badge for current week
    badge = " ← Current Week" if is_current else ""
    if week_pct == 1.0:
        badge = " ✓ Complete"

    with st.expander(f"{label}{badge} ({week_completed}/{week_total})", expanded=is_current):
        st.progress(week_pct)

        day_labels = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        for i, task in enumerate(tasks):
            day_label = day_labels[i] if i < len(day_labels) else f"Day {i+1}"
            week_start = start_date + timedelta(weeks=week_num - 1)
            task_date = week_start + timedelta(days=i)

            is_today = task_date == date.today()
            prefix = "→ " if is_today else ""

            col_check, col_text = st.columns([0.05, 0.95])
            with col_check:
                checked = st.checkbox(
                    "done",
                    value=bool(task["completed"]),
                    key=f"task_{task['id']}",
                    label_visibility="collapsed",
                )
            with col_text:
                style = "~~" if checked else "**" if is_today else ""
                date_str = task_date.strftime("%b %d")
                st.markdown(f"{prefix}{style}{day_label} ({date_str}): {task['task_text']}{style}")

            # Handle toggle
            if checked != bool(task["completed"]):
                db.toggle_study_task(task["id"])
                st.rerun()

st.divider()

# ── Week Summary Table ──
st.subheader("📊 Weekly Summary")

summary_data = []
for week_num in range(1, 9):
    tasks = weeks.get(week_num, [])
    done = sum(1 for t in tasks if t["completed"])
    total = len(tasks)
    summary_data.append({
        "Week": WEEK_LABELS[week_num].split(":")[0],
        "Focus": WEEK_LABELS[week_num].split(": ")[1] if ": " in WEEK_LABELS[week_num] else "",
        "Completed": f"{done}/{total}",
        "Progress": f"{done/total:.0%}" if total else "0%",
        "Status": "✓" if done == total else "→" if week_num == current_week else "",
    })

import pandas as pd
st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
