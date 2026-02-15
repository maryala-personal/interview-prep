"""Coding Problems tracker page."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
from datetime import date
from data import db

st.set_page_config(page_title="Coding Problems", page_icon="\U0001f4bb", layout="wide")

db.init_db()

st.title("\U0001f4bb Coding Problems")

# ── Pattern Study Guides Section ──
st.header("\U0001f4d6 Pattern Study Guides")

st.markdown("""
**Master every coding pattern with comprehensive guides!** Each guide includes:
- 🎯 ELI5 explanations with real-world analogies
- 💡 Brute force → Optimized solutions
- ⚡ Time/Space complexity analysis
- 🏆 Pro tips for senior engineers
- 📝 Practice problems (Easy → Hard)
""")

# Pattern selection
PATTERN_GUIDES = {
    "Two Pointers": "two_pointers.md",
    "Sliding Window": "sliding_window.md",
    "Binary Search": "binary_search.md",
    "BFS (Breadth-First Search)": "bfs.md",
    "DFS (Depth-First Search)": "dfs.md",
    "Dynamic Programming": "dynamic_programming.md",
    "Backtracking": "backtracking.md",
    "Greedy Algorithms": "greedy.md",
    "Graph Algorithms": "graph_algorithms.md",
    "Topological Sort": "topological_sort.md",
    "Heap / Priority Queue": "heap.md",
    "Trie (Prefix Tree)": "trie.md",
    "Union-Find": "union_find.md",
    "Monotonic Stack/Queue": "monotonic_stack_queue.md",
    "Prefix Sum": "prefix_sum.md",
    "Intervals": "intervals.md",
    "Matrix / Grid": "matrix_grid.md",
    "Linked List": "linked_list.md",
    "Tree Traversals": "tree_traversals.md",
    "Bit Manipulation": "bit_manipulation.md",
    "String/Array Manipulation": "string_array.md",
    "Design / Data Structures": "design.md",
}

selected_pattern = st.selectbox(
    "📚 Select a Pattern to Study",
    options=["-- Choose a pattern --"] + list(PATTERN_GUIDES.keys()),
    key="pattern_guide_selector"
)

if selected_pattern and selected_pattern != "-- Choose a pattern --":
    pattern_file = PATTERN_GUIDES[selected_pattern]
    pattern_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "solutions",
        "coding_patterns",
        pattern_file
    )

    if os.path.exists(pattern_path):
        with open(pattern_path, 'r', encoding='utf-8') as f:
            guide_content = f.read()

        # Display the guide with custom styling
        st.markdown("---")
        st.markdown(guide_content, unsafe_allow_html=True)
        st.markdown("---")
    else:
        st.warning(f"Guide for {selected_pattern} not found at: {pattern_path}")

st.markdown("---")

# ── Sidebar Filters ──
st.sidebar.header("Filters")

all_patterns = db.get_coding_patterns()
selected_patterns = st.sidebar.multiselect("Pattern", options=all_patterns, default=[])

selected_difficulty = st.sidebar.selectbox(
    "Difficulty", options=["All", "Easy", "Medium", "Hard"]
)

selected_status = st.sidebar.selectbox(
    "Status", options=["All", "not_started", "attempted", "solved", "mastered"]
)

company_filter = st.sidebar.text_input("Company", placeholder="e.g. Meta, Uber")

confidence_range = st.sidebar.slider("Confidence Range", 0, 5, (0, 5))

# ── Build filters dict ──
filters = {}
if selected_difficulty != "All":
    filters["difficulty"] = selected_difficulty
if selected_status != "All":
    filters["status"] = selected_status
if company_filter.strip():
    filters["company"] = company_filter.strip()
if confidence_range[0] > 0:
    filters["min_confidence"] = confidence_range[0]
if confidence_range[1] < 5:
    filters["max_confidence"] = confidence_range[1]

# The DB filter only supports a single pattern, so we fetch with other filters
# and then filter by selected patterns in Python if multiple are chosen.
if len(selected_patterns) == 1:
    filters["pattern"] = selected_patterns[0]

all_problems = db.get_all_coding_problems(filters if filters else None)

if selected_patterns and len(selected_patterns) > 1:
    all_problems = [p for p in all_problems if p["pattern"] in selected_patterns]

# ── Pattern Summary Section ──
st.header("Pattern Summary")

stats = db.get_coding_stats()
by_pattern = stats["by_pattern"]

if by_pattern:
    pattern_df = pd.DataFrame(by_pattern)
    pattern_df["completion_pct"] = (
        (pattern_df["done"] / pattern_df["total"]) * 100
    ).round(1)
    pattern_df.columns = ["Pattern", "Total", "Solved/Mastered", "Avg Confidence", "Completion %"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Problems", stats["total"])
    col2.metric("Solved + Mastered", stats["solved"])
    col3.metric("Mastered", stats["mastered"])

    st.dataframe(
        pattern_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Completion %": st.column_config.ProgressColumn(
                "Completion %", min_value=0, max_value=100, format="%.1f%%"
            ),
            "Avg Confidence": st.column_config.NumberColumn(format="%.1f"),
        },
    )
else:
    st.info("No coding problems in the database yet. Add some below or seed the database.")

# ── Problems Table with Inline Editing ──
st.header("Problems")

if all_problems:
    status_options = ["not_started", "attempted", "solved", "mastered"]

    for idx, problem in enumerate(all_problems):
        with st.container():
            cols = st.columns([2, 3, 1, 1, 2, 1.5, 2, 1.5])
            cols[0].text(problem["pattern"])
            lc_label = f"#{problem['leetcode_num']}" if problem["leetcode_num"] else ""
            cols[1].text(f"{problem['title']} {lc_label}")
            cols[2].text(problem["difficulty"])

            new_status = cols[3].selectbox(
                "Status",
                options=status_options,
                index=status_options.index(problem["status"]),
                key=f"status_{problem['id']}",
                label_visibility="collapsed",
            )

            new_confidence = cols[4].slider(
                "Confidence",
                0,
                5,
                problem["confidence"],
                key=f"conf_{problem['id']}",
                label_visibility="collapsed",
            )

            cols[5].text(problem["last_practiced"] or "Never")
            cols[6].text(f"Practiced: {problem['times_practiced']}x")

            if new_status != problem["status"] or new_confidence != problem["confidence"]:
                if cols[7].button("Save", key=f"save_{problem['id']}"):
                    db.update_coding_problem(
                        problem["id"], status=new_status, confidence=new_confidence
                    )
                    st.rerun()

    st.caption(f"Showing {len(all_problems)} problems")
else:
    st.info("No problems match the current filters.")

# ── Practice Now (Spaced Repetition) ──
st.header("Practice Now")

due_problems = db.get_due_for_review()

if due_problems:
    top_problem = due_problems[0]
    st.subheader(f"Next Up: {top_problem['title']}")
    pcol1, pcol2, pcol3 = st.columns(3)
    pcol1.write(f"**Pattern:** {top_problem['pattern']}")
    pcol2.write(f"**Difficulty:** {top_problem['difficulty']}")
    pcol3.write(f"**LC#:** {top_problem['leetcode_num'] or 'N/A'}")

    st.write(f"**Status:** {top_problem['status']} | **Current Confidence:** {top_problem['confidence']}")
    st.write(f"**Times Practiced:** {top_problem['times_practiced']} | **Last Practiced:** {top_problem['last_practiced'] or 'Never'}")

    if top_problem.get("url"):
        st.markdown(f"[Open on LeetCode]({top_problem['url']})")

    practice_confidence = st.slider(
        "Rate your confidence after practicing", 1, 5, 3, key="practice_confidence"
    )

    if st.button("Mark Practiced"):
        db.practice_coding_problem(top_problem["id"], practice_confidence)
        st.success(
            f"Marked '{top_problem['title']}' as practiced with confidence {practice_confidence}!"
        )
        st.rerun()

    if len(due_problems) > 1:
        with st.expander(f"See all {len(due_problems)} problems due for review"):
            due_df = pd.DataFrame(due_problems)[
                ["pattern", "title", "leetcode_num", "difficulty", "status", "confidence", "next_review"]
            ]
            due_df.columns = ["Pattern", "Title", "LC#", "Difficulty", "Status", "Confidence", "Next Review"]
            st.dataframe(due_df, use_container_width=True, hide_index=True)
else:
    st.success("No problems due for review right now. Great job!")

# ── Add Problem Form ──
st.header("Add Problem")

from data.ai_helper import classify_problem

with st.expander("Add a new coding problem", expanded=True):
    # AI Lookup
    lookup_col, lookup_btn_col = st.columns([4, 1])
    query = lookup_col.text_input(
        "Problem name or LeetCode URL",
        placeholder="e.g. 'Two Sum', 'LRU Cache', or https://leetcode.com/problems/two-sum/",
        key="ai_lookup_query",
    )
    do_lookup = lookup_btn_col.button("Lookup with AI", type="primary", use_container_width=True)

    if do_lookup and query.strip():
        with st.spinner("Classifying problem..."):
            result = classify_problem(query.strip())
        if result:
            st.session_state["ai_result"] = result
        else:
            st.error(
                "Could not classify. Make sure ANTHROPIC_API_KEY is set as an environment variable, "
                "and the `anthropic` package is installed."
            )

    # Pre-fill from AI result if available
    ai = st.session_state.get("ai_result", {})

    with st.form("add_problem_form", clear_on_submit=True):
        add_col1, add_col2 = st.columns(2)
        new_pattern = add_col1.text_input("Pattern", value=ai.get("pattern", ""), placeholder="e.g. Two Pointers")
        new_title = add_col2.text_input("Title", value=ai.get("title", ""), placeholder="e.g. Two Sum")
        add_col3, add_col4 = st.columns(2)
        new_lc_num = add_col3.number_input(
            "LeetCode #", min_value=0, step=1, value=ai.get("leetcode_num", 0)
        )
        diff_options = ["Easy", "Medium", "Hard"]
        new_difficulty = add_col4.selectbox(
            "Difficulty",
            options=diff_options,
            index=diff_options.index(ai["difficulty"]) if ai.get("difficulty") in diff_options else 1,
        )
        new_company_tags = st.text_input(
            "Company Tags", value=ai.get("company_tags", ""), placeholder="e.g. Meta, Uber, Microsoft"
        )

        submitted = st.form_submit_button("Add Problem")
        if submitted:
            if not new_pattern.strip() or not new_title.strip():
                st.error("Pattern and Title are required.")
            else:
                url = ai.get("url", "")
                kwargs = {
                    "pattern": new_pattern.strip(),
                    "title": new_title.strip(),
                    "difficulty": new_difficulty,
                    "company_tags": new_company_tags.strip(),
                }
                if new_lc_num > 0:
                    kwargs["leetcode_num"] = new_lc_num
                if url:
                    kwargs["url"] = url
                db.add_coding_problem(**kwargs)
                st.session_state.pop("ai_result", None)
                st.success(f"Added '{new_title.strip()}' to {new_pattern.strip()}!")
                st.rerun()
