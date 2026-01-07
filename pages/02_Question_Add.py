import streamlit as st
import json
import re
from uuid import uuid4

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="MCQ Question Bank Builder",
    layout="wide"
)

st.title("🧠 MCQ Question Bank Builder")
st.caption("Add, label, parse, and export multiple-choice questions")

# =====================================================
# SESSION STATE
# =====================================================
if "questions" not in st.session_state:
    st.session_state.questions = []

# =====================================================
# HELPERS
# =====================================================
def parse_mcq_block(text: str):
    """
    Parses raw MCQ text into question + options
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 3:
        return None, None

    question = lines[0]
    options_raw = lines[1:]

    option_labels = list("ABCDE")
    options = {}

    for i, opt in enumerate(options_raw):
        if i >= len(option_labels):
            break
        options[option_labels[i]] = opt.rstrip(".")

    return question, options

# =====================================================
# SIDEBAR — PACKAGE INFO
# =====================================================
st.sidebar.header("📦 Question Set")

package_id = st.sidebar.text_input("Package ID", "pkg_exposure_01")
source = st.sidebar.text_input("Source", "imaging_exposure.pdf")
level = st.sidebar.selectbox(
    "Level",
    ["introductory", "intermediate", "advanced_undergraduate", "graduate"]
)

# =====================================================
# QUESTION INPUT
# =====================================================
st.header("✏️ Add New Question")

raw_text = st.text_area(
    "Paste MCQ text",
    height=200,
    placeholder="Paste question + options here"
)

if raw_text:
    question, options = parse_mcq_block(raw_text)

    if question and options:
        st.subheader("🔍 Parsed Preview")

        st.markdown(f"**Question:** {question}")
        for k, v in options.items():
            st.write(f"{k}. {v}")

        correct_option = st.selectbox(
            "Correct Option",
            list(options.keys())
        )

        difficulty = st.selectbox(
            "Difficulty",
            ["easy", "medium", "hard"]
        )

        learning_objective = st.text_input(
            "Learning Objective",
            placeholder="e.g., Understand exposure and f-number relationships"
        )

        slide_refs = st.text_input(
            "Slide References (comma-separated)",
            placeholder="e.g., 12, 13"
        )

        if st.button("➕ Add Question"):
            st.session_state.questions.append({
                "id": f"{package_id}_mcq_{uuid4().hex[:6]}",
                "question": question,
                "options": options,
                "correct_option": correct_option,
                "difficulty": difficulty,
                "learning_objective": learning_objective,
                "slide_refs": [
                    int(s.strip())
                    for s in slide_refs.split(",")
                    if s.strip().isdigit()
                ]
            })
            st.success("Question added!")

    else:
        st.error("Could not parse question. Please check formatting.")

# =====================================================
# QUESTION LIST
# =====================================================
st.header("📚 Current Questions")

if st.session_state.questions:
    for i, q in enumerate(st.session_state.questions, 1):
        with st.expander(f"Question {i}"):
            st.write(q["question"])
            for k, v in q["options"].items():
                marker = "✅" if k == q["correct_option"] else ""
                st.write(f"{k}. {v} {marker}")
            st.caption(f"Difficulty: {q['difficulty']}")
else:
    st.info("No questions added yet.")

# =====================================================
# EXPORT
# =====================================================
st.header("📤 Export")

export_data = {
    "package_id": package_id,
    "source": source,
    "level": level,
    "mcqs": st.session_state.questions
}

st.download_button(
    "⬇️ Download JSON",
    data=json.dumps(export_data, indent=2),
    file_name=f"{package_id}.json",
    mime="application/json"
)
