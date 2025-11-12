import streamlit as st
import json
import os
from pathlib import Path
import pandas as pd

# -------------------------------
# CONFIGURATION
# -------------------------------
# Fix: Go one level up (from /pages to project root)
BASE_DIR = Path(__file__).resolve().parents[1]
DB_DIR = BASE_DIR / "database"
RESULTS_DIR = BASE_DIR / "results" / "user_submissions"

# Ensure results directory exists
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="📊 View Results", layout="wide")
st.title("📊 Test Results Viewer")

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------

def list_results() -> list:
    """List all result JSON files inside results/user_submissions."""
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted([f for f in os.listdir(RESULTS_DIR) if f.endswith(".json")])
    return files

def load_json(path: Path):
    """Load JSON data from file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_package_file(subject: str, package_id: str) -> Path:
    """Get the package file path for a given subject and package."""
    pkg_path = DB_DIR / subject / package_id / "package.json"
    return pkg_path if pkg_path.exists() else None

def flatten_mcq_data(package_data, user_data):
    """Prepare MCQ dataframe comparing questions, answers, and correct options."""
    mcqs = package_data.get("mcqs", [])
    user_answers = user_data.get("user_answers", {})
    rows = []
    for q in mcqs:
        qid = q["id"]
        rows.append({
            "Question ID": qid,
            "Question": q["question"],
            "User Answer": user_answers.get(qid, "-"),
            "Correct Answer": q.get("correct_option", "-"),
            "Result": "✅ Correct" if user_answers.get(qid) == q.get("correct_option") else "❌ Incorrect"
        })
    return pd.DataFrame(rows)

def flatten_essay_data(package_data, user_data):
    """Prepare Essay dataframe comparing prompts and user responses."""
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
        matched_keywords = [kw for kw in expected_keywords if kw.lower() in user_response.lower()]
        rows.append({
            "Essay ID": eid,
            "Prompt": e["prompt"],
            "Expected Keywords": ", ".join(expected_keywords),
            "User Response (short)": user_response[:300] + ("..." if len(user_response) > 300 else ""),
            "Matched Keywords": ", ".join(matched_keywords) if matched_keywords else "None"
        })
    return pd.DataFrame(rows)

# -------------------------------
# UI LAYOUT
# -------------------------------

# Step 1️⃣: Check for results
all_files = list_results()
if not all_files:
    st.warning("⚠️ No result files found in `results/user_submissions/`.")
    st.info("Try running a test in the main app first to generate results.")
    if st.button("🔄 Reload"):
        st.experimental_rerun()
    st.stop()

# Step 2️⃣: Extract subjects
subjects = sorted(set([f.split("_package_")[0] for f in all_files]))
subject = st.selectbox("Select Subject:", subjects)

# Step 3️⃣: Filter by subject and get packages
# Step 3️⃣: Filter by subject and get packages
subject_files = [f for f in all_files if f.startswith(subject)]

# Extract package numbers safely (handles both _package_11_... and other variants)
packages = []
for f in subject_files:
    parts = f.split("_")
    if "package" in parts:
        idx = parts.index("package")
        if idx + 1 < len(parts):
            packages.append(parts[idx + 1])

packages = sorted(set(packages))
package_id = st.selectbox("Select Package ID:", packages)

# Step 4️⃣: Select submission file for chosen package
package_files = [f for f in subject_files if f"package_{package_id}" in f]
selected_file = st.selectbox("Select Submission File:", package_files)

# ✅ Safety: Stop if nothing selected yet
if not selected_file:
    st.info("👈 Please select a submission file to view details.")
    st.stop()

# Step 5️⃣: Load submission result
result_path = RESULTS_DIR / selected_file
if not result_path.exists():
    st.error(f"❌ File not found: {result_path}")
    st.stop()

result_data = load_json(result_path)
st.success(f"✅ Loaded submission file: {selected_file}")

# Step 6️⃣: Load corresponding question package
package_path = get_package_file(result_data["subject"], result_data["package_id"])
if not package_path:
    st.error("❌ Corresponding question package not found in the database.")
    st.stop()

package_data = load_json(package_path)
st.info(f"📦 Loaded question package: `{package_path}`")

# Step 7️⃣: Summary Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("📘 Subject", result_data["subject"])
col2.metric("📦 Package", result_data["package_id"])
col3.metric("✅ MCQ Score", f"{result_data['mcq_score']}/{result_data['mcq_total']}")
col4.metric("🧠 Final Score", f"{result_data['final_score']:.1f}/100")

st.divider()

# Step 8️⃣: MCQ Comparison Table
st.markdown("### 🧮 Multiple Choice Questions")
mcq_df = flatten_mcq_data(package_data, result_data)
if not mcq_df.empty:
    st.dataframe(mcq_df, use_container_width=True)
else:
    st.info("No MCQs available for this package.")

# Step 9️⃣: Essay Comparison Table
st.markdown("### ✍️ Essay Questions and Responses")
essay_df = flatten_essay_data(package_data, result_data)
if not essay_df.empty:
    st.dataframe(essay_df, use_container_width=True)
else:
    st.info("No essay questions found for this package.")

# Step 🔟: Download CSV
combined_df = pd.concat([mcq_df, essay_df], axis=0, ignore_index=True)
csv_data = combined_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇️ Download Comparison as CSV",
    data=csv_data,
    file_name=f"{subject}_{package_id}_comparison.csv",
    mime="text/csv"
)
