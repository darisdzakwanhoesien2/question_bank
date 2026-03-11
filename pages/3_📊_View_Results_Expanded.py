import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd

# -------------------------------
# CONFIGURATION
# -------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "database"
RESULTS_DIR = BASE_DIR / "results" / "user_submissions"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="📊 View Results", layout="wide")
st.title("📊 Test Results Viewer")

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------

def list_results() -> list:
    return sorted([f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")])


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_package_file(subject: str, package_id: str) -> Path | None:
    pkg_path = DB_DIR / subject / package_id / "package.json"
    return pkg_path if pkg_path.exists() else None


def flatten_mcq_data(package_data, user_data):
    mcqs = package_data.get("mcqs", [])
    user_answers = user_data.get("user_answers", {})

    rows = []

    for q in mcqs:
        qid = q["id"]
        options = q.get("options", {})

        user_key = user_answers.get(qid, "-")
        correct_key = q.get("correct_option", "-")

        user_text = options.get(user_key, "-") if isinstance(options, dict) else "-"
        correct_text = options.get(correct_key, "-") if isinstance(options, dict) else "-"

        rows.append({
            "Question ID": qid,
            "Question": q["question"],
            "User Answer Key": user_key,
            "User Answer Text": user_text,
            "Correct Answer Key": correct_key,
            "Correct Answer Text": correct_text,
            "Result": "Correct" if user_key == correct_key else "Incorrect"
        })

    return pd.DataFrame(rows)


def flatten_essay_data(package_data, user_data):
    essays = package_data.get("essay", [])
    if isinstance(essays, dict):
        essays = [essays]

    user_essays = user_data.get("user_essay_answers", {})
    rows = []

    for e in essays:
        eid = e["id"]
        rubric = e.get("rubric", {})
        expected_keywords = [c["keyword"] for c in rubric.get("criteria", [])]
        user_response = user_essays.get(eid, "")

        matched_keywords = [
            kw for kw in expected_keywords if kw.lower() in user_response.lower()
        ]

        rows.append({
            "Essay ID": eid,
            "Prompt": e["prompt"],
            "Expected Keywords": ", ".join(expected_keywords),
            "Matched Keywords": ", ".join(matched_keywords) if matched_keywords else "None",
            "User Response (preview)": user_response[:400] + ("..." if len(user_response) > 400 else "")
        })

    return pd.DataFrame(rows)


# -------------------------------
# UI
# -------------------------------

# Step 1: Results exist?
all_files = list_results()

if not all_files:
    st.warning("⚠️ No result files found in results/user_submissions/")
    st.stop()

# Step 2: Subject select
subjects = sorted(set([f.split("_package_")[0] for f in all_files]))
subject = st.selectbox("📘 Select Subject", subjects)

# Step 3: Package select
subject_files = [f for f in all_files if f.startswith(subject)]

packages = []
for f in subject_files:
    parts = f.split("_")
    if "package" in parts:
        idx = parts.index("package")
        if idx + 1 < len(parts):
            packages.append(parts[idx + 1])

packages = sorted(set(packages))
package_id = st.selectbox("📦 Select Package ID", packages)

# Step 4: Submission file select
package_files = [f for f in subject_files if f"package_{package_id}" in f]
selected_file = st.selectbox("🧾 Select Submission", package_files)

if not selected_file:
    st.stop()

# Step 5: Load result
result_path = RESULTS_DIR / selected_file

if not result_path.exists():
    st.error("Result file not found.")
    st.stop()

result_data = load_json(result_path)

# Step 6: Load package
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
# MCQ DETAILED VIEW
# -------------------------------

st.markdown("## 🧮 Multiple Choice Review")

show_only_wrong = st.checkbox("Show only incorrect answers", False)

mcqs = package_data.get("mcqs", [])
user_answers = result_data.get("user_answers", {})

wrong_count = 0

for i, q in enumerate(mcqs, 1):
    qid = q["id"]
    options = q.get("options", {})

    user_key = user_answers.get(qid, "-")
    correct_key = q.get("correct_option", "-")
    is_correct = user_key == correct_key

    if show_only_wrong and is_correct:
        continue

    if not is_correct:
        wrong_count += 1

    with st.expander(f"Q{i} — {'✅' if is_correct else '❌'}"):
        st.markdown(f"**Question:** {q['question']}")

        for k, v in options.items():
            label = f"({k}) {v}"

            if k == correct_key:
                st.success(f"✔ Correct: {label}")
            elif k == user_key:
                st.error(f"✖ Your Answer: {label}")
            else:
                st.write(label)

        st.markdown(f"**Your Answer:** {user_key}")
        st.markdown(f"**Correct Answer:** {correct_key}")

if show_only_wrong:
    st.info(f"Total incorrect questions: {wrong_count}")

st.divider()

# -------------------------------
# ESSAY VIEW
# -------------------------------

st.markdown("## ✍️ Essay Review")

essay_df = flatten_essay_data(package_data, result_data)

if essay_df.empty:
    st.info("No essay questions in this package.")
else:
    st.dataframe(essay_df, use_container_width=True)

st.divider()

# -------------------------------
# CSV DOWNLOAD
# -------------------------------

mcq_df = flatten_mcq_data(package_data, result_data)
combined_df = pd.concat([mcq_df, essay_df], axis=0, ignore_index=True)

csv_data = combined_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Full Comparison (CSV)",
    data=csv_data,
    file_name=f"{subject}_{package_id}_review.csv",
    mime="text/csv"
)
