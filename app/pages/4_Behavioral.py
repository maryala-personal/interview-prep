import streamlit as st
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from data import db

st.set_page_config(page_title="Behavioral", page_icon="\U0001f3af", layout="wide")

st.title("\U0001f3af Behavioral Stories (STAR Format)")
st.caption("Prepare and practice behavioral interview stories organized by category.")

CATEGORIES = {
    "Leadership": "leadership",
    "Conflict": "conflict",
    "Technical Decision": "technical_decision",
    "Collaboration": "collaboration",
    "Mentoring": "mentoring",
    "Ambiguity": "ambiguity",
}

tabs = st.tabs(list(CATEGORIES.keys()))

for tab, (display_name, db_category) in zip(tabs, CATEGORIES.items()):
    with tab:
        stories = db.get_all_behavioral_stories(category=db_category)

        # -- Existing stories --
        if stories:
            for story in stories:
                sid = story["id"]
                with st.expander(f"{story['title'] or 'Untitled'} (ID {sid})", expanded=False):
                    st.markdown(f"**Applicable Question:** {story.get('applicable_questions', '')}")

                    situation = st.text_area(
                        "Situation",
                        value=story.get("situation", ""),
                        key=f"sit_{sid}",
                        height=100,
                    )
                    task = st.text_area(
                        "Task",
                        value=story.get("task", ""),
                        key=f"task_{sid}",
                        height=100,
                    )
                    action = st.text_area(
                        "Action",
                        value=story.get("action", ""),
                        key=f"act_{sid}",
                        height=100,
                    )
                    result = st.text_area(
                        "Result",
                        value=story.get("result", ""),
                        key=f"res_{sid}",
                        height=100,
                    )
                    company_tags = st.text_input(
                        "Company Tags",
                        value=story.get("company_tags", ""),
                        key=f"tags_{sid}",
                    )

                    col_save, col_delete = st.columns([1, 1])
                    with col_save:
                        if st.button("Save", key=f"save_{sid}"):
                            db.update_behavioral_story(
                                sid,
                                situation=situation,
                                task=task,
                                action=action,
                                result=result,
                                company_tags=company_tags,
                            )
                            st.success("Story updated!")
                            st.rerun()
                    with col_delete:
                        if st.button("Delete", key=f"del_{sid}", type="secondary"):
                            db.delete_behavioral_story(sid)
                            st.success("Story deleted.")
                            st.rerun()
        else:
            st.info(f"No stories yet for {display_name}. Add one below!")

        # -- Add new story form --
        with st.expander(f"Add New {display_name} Story", expanded=False):
            with st.form(key=f"add_form_{db_category}"):
                new_title = st.text_input("Title", key=f"new_title_{db_category}")
                new_question = st.text_input(
                    "Applicable Question", key=f"new_q_{db_category}"
                )
                new_situation = st.text_area(
                    "Situation", key=f"new_sit_{db_category}", height=100
                )
                new_task = st.text_area(
                    "Task", key=f"new_task_{db_category}", height=100
                )
                new_action = st.text_area(
                    "Action", key=f"new_act_{db_category}", height=100
                )
                new_result = st.text_area(
                    "Result", key=f"new_res_{db_category}", height=100
                )
                new_tags = st.text_input(
                    "Company Tags", key=f"new_tags_{db_category}"
                )

                submitted = st.form_submit_button("Add Story")
                if submitted:
                    if not new_title.strip():
                        st.error("Title is required.")
                    else:
                        db.add_behavioral_story(
                            category=db_category,
                            title=new_title.strip(),
                            applicable_questions=new_question.strip(),
                            situation=new_situation.strip(),
                            task=new_task.strip(),
                            action=new_action.strip(),
                            result=new_result.strip(),
                            company_tags=new_tags.strip(),
                        )
                        st.success(f"Added new {display_name} story!")
                        st.rerun()

# -- Practice Mode --
st.divider()
st.header("Practice Mode")
st.write(
    "Click the button to get a random behavioral question. "
    "Think about which story fits best, then reveal the suggested story."
)

all_stories = db.get_all_behavioral_stories()
questions_with_stories = [
    (s["applicable_questions"], s["title"], s["category"])
    for s in all_stories
    if s.get("applicable_questions", "").strip()
]

if not questions_with_stories:
    st.info("No questions available yet. Add stories with applicable questions above.")
else:
    if st.button("Random Question"):
        pick = random.choice(questions_with_stories)
        st.session_state["practice_question"] = pick[0]
        st.session_state["practice_story_title"] = pick[1]
        st.session_state["practice_story_category"] = pick[2]

    if "practice_question" in st.session_state:
        st.subheader("Question")
        st.info(st.session_state["practice_question"])

        with st.expander("Reveal Suggested Story"):
            cat_display = {v: k for k, v in CATEGORIES.items()}.get(
                st.session_state["practice_story_category"],
                st.session_state["practice_story_category"],
            )
            st.write(f"**Category:** {cat_display}")
            st.write(f"**Story:** {st.session_state['practice_story_title']}")
