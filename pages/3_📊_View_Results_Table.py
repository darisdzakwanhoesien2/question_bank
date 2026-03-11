import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd

# -------------------------------
# CONFIG
# -------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "database"
RESULTS_DIR = BASE_DIR / "results" / "user_submissions"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="📊 View Results", layout="wide")
st.title("📊 Test Results Viewer")

# -------------------------------
# HELPERS
# -------------------------------

def list_results():
    return sorted([f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")])


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_package_file(subject: str, package_id: str):
    path = DB_DIR / subject / package_id / "package.json"
    return path if path.exists() else None


def build_mcq_table(package_data, result_data):
    mcqs = package_data.get("mcqs", [])
    user_answers = result_data.get("user_answers", {})

    rows = []

    for i, q in enumerate(mcqs, 1):
        qid = q["id"]
        options = q.get("options", {})

        user_key = user_answers.get(qid, "-")
        correct_key = q.get("correct_option", "-")

        user_text = options.get(user_key, "-")
        correct_text = options.get(correct_key, "-")

        rows.append({
            "No": i,
            "Question": q["question"],
            "Your Answer": f"({user_key}) {user_text}",
            "Correct Answer": f"({correct_key}) {correct_text}",
            "Result": "✅ Correct" if user_key == correct_key else "❌ Incorrect"
        })

    return pd.DataFrame(rows)


def build_essay_table(package_data, result_data):
    essays = package_data.get("essay", [])
    if isinstance(essays, dict):
        essays = [essays]

    user_essays = result_data.get("user_essay_answers", {})
    rows = []

    for i, e in enumerate(essays, 1):
        eid = e["id"]
        rubric = e.get("rubric", {})
        expected_keywords = [c["keyword"] for c in rubric.get("criteria", [])]
        user_response = user_essays.get(eid, "")

        matched = [kw for kw in expected_keywords if kw.lower() in user_response.lower()]

        rows.append({
            "No": i,
            "Prompt": e["prompt"],
            "Expected Keywords": ", ".join(expected_keywords),
            "Matched Keywords": ", ".join(matched) if matched else "None",
            "Your Answer (preview)": user_response[:300] + ("..." if len(user_response) > 300 else "")
        })

    return pd.DataFrame(rows)

# -------------------------------
# UI — SELECT RESULT
# -------------------------------

files = list_results()

if not files:
    st.warning("No result files found in results/user_submissions/")
    st.stop()

subjects = sorted(set([f.split("_package_")[0] for f in files]))
subject = st.selectbox("📘 Subject", subjects)

subject_files = [f for f in files if f.startswith(subject)]

packages = []
for f in subject_files:
    parts = f.split("_")
    if "package" in parts:
        idx = parts.index("package")
        if idx + 1 < len(parts):
            packages.append(parts[idx + 1])

packages = sorted(set(packages))
package_id = st.selectbox("📦 Package ID", packages)

package_files = [f for f in subject_files if f"package_{package_id}" in f]
selected_file = st.selectbox("🧾 Submission File", package_files)

if not selected_file:
    st.stop()

# -------------------------------
# LOAD DATA
# -------------------------------

result_path = RESULTS_DIR / selected_file
result_data = load_json(result_path)

package_path = get_package_file(result_data["subject"], result_data["package_id"])
if not package_path:
    st.error("Question package not found in database.")
    st.stop()

package_data = load_json(package_path)

# -------------------------------
# SUMMARY
# -------------------------------

st.success(f"Loaded: {selected_file}")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Subject", result_data["subject"])
c2.metric("Package", result_data["package_id"])
c3.metric("MCQ Score", f"{result_data['mcq_score']}/{result_data['mcq_total']}")
c4.metric("Final Score", f"{result_data['final_score']:.1f}/100")

st.divider()

# -------------------------------
# MCQ TABLE
# -------------------------------

st.markdown("## 🧮 Multiple Choice Questions — Review Table")

mcq_df = build_mcq_table(package_data, result_data)

show_wrong_only = st.checkbox("Show only incorrect questions")

if show_wrong_only:
    mcq_df = mcq_df[mcq_df["Result"] == "❌ Incorrect"]

st.dataframe(mcq_df, use_container_width=True, hide_index=True)

st.divider()

# -------------------------------
# ESSAY TABLE
# -------------------------------

st.markdown("## ✍️ Essay Questions — Review Table")

essay_df = build_essay_table(package_data, result_data)

if essay_df.empty:
    st.info("No essay questions in this package.")
else:
    st.dataframe(essay_df, use_container_width=True, hide_index=True)

st.divider()

# -------------------------------
# DOWNLOAD CSV
# -------------------------------

combined_df = pd.concat(
    [mcq_df, essay_df],
    axis=0,
    ignore_index=True
)

csv_data = combined_df.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Download Results as CSV",
    data=csv_data,
    file_name=f"{subject}_{package_id}_results.csv",
    mime="text/csv"
)
