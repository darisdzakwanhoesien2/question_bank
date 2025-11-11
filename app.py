import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List
# from openai import OpenAI  # Uncomment when ready to use GPT generation

# -------------------------------
# CONFIGURATION
# -------------------------------
BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "database"
RESULTS_DIR = BASE_DIR / "results" / "user_submissions"
PROMPT_FILE = BASE_DIR / "config" / "prompts" / "generate_questions.txt"

os.makedirs(RESULTS_DIR, exist_ok=True)

# --- Initialize OpenAI client (commented out for now) ---
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="Question Bank Generator & Test Simulator", layout="wide")
st.title("📘 Question Bank Generator & Test Simulator")

# -------------------------------
# UTILITY FUNCTIONS
# -------------------------------

def load_prompt() -> str:
    """Load generation prompt template."""
    if not os.path.exists(PROMPT_FILE):
        return "Prompt file not found."
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return f.read()

def generate_questions_from_pdf(pdf_path: str, package_id: str, source: str, level: str, subject: str) -> Dict:
    """Simulated version of GPT-based question generation."""
    import fitz  # PyMuPDF
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")

    # Placeholder simulation (GPT disabled)
    st.warning("⚠️ GPT generation is currently disabled. Using a sample placeholder instead.")
    return {
        "package_id": package_id,
        "source": source,
        "level": level,
        "mcqs": [
            {
                "id": f"{package_id}_mcq1",
                "question": f"Example MCQ question for {subject}.",
                "options": {
                    "A": "Example Option A",
                    "B": "Example Option B",
                    "C": "Example Option C",
                    "D": "Example Option D"
                },
                "correct_option": "A",
                "difficulty": "easy",
                "learning_objective": "Understand example placeholder question",
                "slide_refs": [1, 2]
            }
        ],
        "essay": [
            {
                "id": f"{package_id}_essay1",
                "prompt": f"Write an essay discussing key ideas of {subject}.",
                "expected_keywords": ["example", "placeholder", "essay"],
                "rubric": {
                    "total_points": 100,
                    "criteria": [
                        {"keyword": "example", "weight": 40, "description": "Mentions example concept"},
                        {"keyword": "placeholder", "weight": 40, "description": "Mentions placeholder concept"},
                        {"keyword": "essay", "weight": 20, "description": "Mentions essay structure"}
                    ],
                    "grading_notes": "This is a placeholder rubric until OpenAI is re-enabled."
                }
            }
        ]
    }

def save_json(data: Dict, subject: str, package_id: str):
    """Save generated JSON file to database folder."""
    out_dir = DB_DIR / subject / package_id
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "package.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    st.success(f"✅ Saved package.json to {out_dir}")

def load_packages(subject: str) -> List[str]:
    """List available packages for a given subject."""
    subject_dir = DB_DIR / subject
    if not subject_dir.exists():
        return []
    return [pkg for pkg in os.listdir(subject_dir) if not pkg.startswith('.')]

def grade_mcq(mcq_data, user_answers):
    """Compute MCQ score."""
    total, correct = len(mcq_data), 0
    for q in mcq_data:
        if user_answers.get(q["id"]) == q.get("correct_option"):
            correct += 1
    return correct, total

def grade_essay(essay_data, user_text):
    """Keyword-based essay scoring."""
    score = 0
    matched = []
    rubric = essay_data.get("rubric", {"criteria": [], "total_points": 100})
    for crit in rubric["criteria"]:
        if crit["keyword"].lower() in user_text.lower():
            score += crit["weight"]
            matched.append(crit["keyword"])
    return score, rubric["total_points"], matched

# -------------------------------
# APP SECTIONS
# -------------------------------
mode = st.sidebar.radio("Select Mode", ["🏗️ Generate Question Bank", "🧩 Take Test"])

# -------------------------------
# MODE 1: GENERATE QUESTION BANK
# -------------------------------
if mode == "🏗️ Generate Question Bank":
    st.header("📄 Generate Question Bank from PDF")

    subject = st.text_input("Subject name (e.g., machine_vision):")
    level = st.selectbox("Select difficulty level:", ["introductory", "undergraduate", "advanced_undergraduate", "graduate"])
    package_id = st.text_input("Package ID (e.g., pkg26):")
    pdf_file = st.file_uploader("Upload PDF file", type=["pdf"])

    if pdf_file and subject and package_id:
        pdf_path = BASE_DIR / "temp.pdf"
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getvalue())

        if st.button("🚀 Generate Questions"):
            result = generate_questions_from_pdf(
                pdf_path=str(pdf_path),
                package_id=package_id,
                source=pdf_file.name,
                level=level,
                subject=subject
            )
            if result:
                save_json(result, subject, package_id)
                st.json(result)

# -------------------------------
# MODE 2: TAKE TEST
# -------------------------------
elif mode == "🧩 Take Test":
    st.header("🧠 Take a Test")

    subjects = [d for d in os.listdir(DB_DIR) if os.path.isdir(DB_DIR / d)]
    if not subjects:
        st.warning("⚠️ No subjects found in the database folder.")
    else:
        subject = st.selectbox("Select subject:", subjects)
        packages = load_packages(subject)

        if packages:
            package_id = st.selectbox("Select package:", packages)
            package_file = DB_DIR / subject / package_id / "package.json"

            if package_file.exists():
                with open(package_file, "r", encoding="utf-8") as f:
                    package = json.load(f)

                st.subheader(f"📦 {package['package_id']} — {package['source']}")
                st.markdown(f"**Level:** {package['level']}")

                # --- MCQ Section ---
                if package["mcqs"]:
                    st.markdown("### Multiple Choice Questions")
                    user_mcq_answers = {}
                    for q in package["mcqs"]:
                        with st.expander(f"Q: {q['question']}"):
                            options_formatted = [f"{key}. {value}" for key, value in q["options"].items()]
                            selected = st.radio("Choose answer:", options_formatted, key=q["id"])
                            user_mcq_answers[q["id"]] = selected.split(".")[0].strip()
                else:
                    st.info("No MCQs available in this package.")

                # --- Essay Section ---
                st.markdown("### Essay Question(s)")
                essays = package.get("essay", [])

                # Handle single essay object case
                if isinstance(essays, dict):
                    essays = [essays]

                user_essay_answers = {}

                for idx, essay in enumerate(essays, start=1):
                    with st.expander(f"Essay {idx}: {essay['id']}"):
                        st.write(essay["prompt"])
                        response_key = f"essay_response_{idx}"
                        user_essay_answers[essay["id"]] = st.text_area(
                            f"Your response for Essay {idx}:",
                            key=response_key,
                            height=250
                        )

                if st.button("Submit Answers"):
                    # --- Grade MCQs ---
                    mcq_correct, mcq_total = grade_mcq(package.get("mcqs", []), user_mcq_answers)

                    # --- Grade Essays ---
                    total_essay_score = 0
                    total_possible = 0
                    all_matched = []

                    for essay in essays:
                        user_text = user_essay_answers.get(essay["id"], "")
                        essay_score, essay_total, matched = grade_essay(essay, user_text)
                        total_essay_score += essay_score
                        total_possible += essay_total
                        all_matched.extend(matched)
                        st.info(f"Essay {essay['id']}: {essay_score}/{essay_total} ({', '.join(matched) if matched else 'No matches'})")

                    # Normalize essay score
                    essay_percent = (total_essay_score / total_possible) if total_possible else 0
                    total_score = ((mcq_correct / mcq_total) * 50 + essay_percent * 50) if mcq_total else essay_percent * 100

                    st.success(f"MCQ: {mcq_correct}/{mcq_total}")
                    st.success(f"Essay Total: {total_essay_score}/{total_possible}")
                    st.metric("Final Score", f"{total_score:.1f} / 100")

                    # --- Save Results ---
                    result_data = {
                        "timestamp": datetime.now().isoformat(),
                        "subject": subject,
                        "package_id": package_id,
                        "mcq_score": mcq_correct,
                        "mcq_total": mcq_total,
                        "essay_score": total_essay_score,
                        "essay_total": total_possible,
                        "final_score": total_score,
                        "matched_keywords": all_matched,
                        "user_answers": user_mcq_answers,
                        "user_essay_answers": user_essay_answers
                    }
                    out_file = RESULTS_DIR / f"{subject}_{package_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(out_file, "w", encoding="utf-8") as f:
                        json.dump(result_data, f, indent=2)
                    st.success(f"✅ Results saved to {out_file}")
            else:
                st.error("❌ Selected package file not found.")
        else:
            st.warning("⚠️ No packages found for this subject.")
