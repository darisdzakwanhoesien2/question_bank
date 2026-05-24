https://chatgpt.com/c/69121bc5-b4cc-832d-b2a5-c1522b656433
https://chatgpt.com/g/g-6912cc3039d48191bd184701da3ba844-question-bank-generator/c/6912cd36-3c88-8328-81b6-a923aa2d02d5
Grok works for non-vision tasks: https://grok.com/c/6cad1efa-f963-4132-b4fc-62419c1c3cf8
Towards Data Mining Question Generative: https://grok.com/c/e2b5edfe-60d0-4d97-aee8-27dfdc6e4f2f 

Source of Information: 
https://notebooklm.google.com/notebook/5301d379-ffae-4675-966c-43086804816d
Prompt MCQ, Essay and Mixed into NotebookLM: https://chatgpt.com/c/6928415a-ae84-832a-8d6e-694e3aece3fc


https://chatgpt.com/c/695e4369-b72c-8329-8e74-27599552225a Note-taking strategy

test_question_bank_app/
│
├── app.py                              # Streamlit frontend (select package/test mode/run)
│
├── config/
│   ├── settings.yaml                   # General app configuration (paths, user roles, weights)
│   ├── prompts/
│   │   ├── generate_questions.txt      # The master question generation prompt
│   │   ├── rubric_guidelines.txt       # Defines rubric weighting standards
│   │   └── metadata_schema.json        # Defines JSON schema for validation
│   ├── evaluation.yaml                 # Global scoring weights, difficulty scaling, essay-to-total ratio
│
├── database/
│   ├── numerical_linear_algebra/
│   │   ├── package_1/
│   │   │   ├── source.pdf
│   │   │   ├── package.json            # Master combined file (MCQ + essay + rubric + metadata)
│   │   │   └── metadata.json           # Auto-generated metadata (e.g., title, topics, keywords)
│   │   ├── package_2/
│   │   │   ├── source.pdf
│   │   │   ├── package.json
│   │   │   └── metadata.json
│   │   ├── ...
│   │   └── combined/
│   │       ├── combined_mcqs.json
│   │       ├── combined_essays.json
│   │       └── combined_metadata.json
│   │
│   ├── data_mining_ethics/
│   │   ├── package_1/
│   │   │   ├── towards_data_mining_lecture_2_slides.pdf
│   │   │   ├── package.json
│   │   │   └── metadata.json
│   │   └── combined/
│   │       ├── combined_mcqs.json
│   │       └── combined_essays.json
│   │
│   └── registry.json                   # Lists all available subjects, packages, and metadata
│
├── generators/
│   ├── generate_package.py              # Reads PDF → sends to LLM → creates JSON output
│   ├── merge_packages.py                # Combines multiple package JSONs into a single combined file
│   ├── validate_schema.py               # Validates generated JSON against metadata_schema.json
│   ├── extract_text.py                  # PDF-to-text parser (PyMuPDF or PDFPlumber)
│   └── utils.py                         # Helper functions for IO, metadata tagging, keyword extraction
│
├── evaluation/
│   ├── essay_grader.py                  # Grades essay responses based on rubric keywords
│   ├── mcq_evaluator.py                 # Checks MCQ answers, computes total score
│   └── feedback_generator.py            # Generates human-readable feedback from rubric performance
│
├── pages/
│   ├── 1_Home.py                        # Welcome + subject selection
│   ├── 2_Take_Test.py                   # Test interface (MCQ/Essay)
│   ├── 3_Results.py                     # Results view with rubric explanation
│   └── 4_Admin_Panel.py                 # Upload PDFs, generate question JSONs
│
├── assets/
│   ├── logo.png
│   ├── styles.css
│   └── icons/
│
├── results/
│   ├── user_submissions/
│   │   ├── <user_id>_<timestamp>.json   # Stores user answers + auto-grading output
│   ├── analytics/
│   │   └── question_performance.json    # Aggregates difficulty and discrimination metrics
│
├── schemas/
│   ├── package_schema.json              # JSON Schema for validating generated package.json
│   ├── essay_rubric_schema.json         # JSON Schema for rubric fields
│   └── mcq_schema.json                  # JSON Schema for MCQ validation
│
├── logs/
│   ├── generation_log.txt
│   └── grading_log.txt
│
├── requirements.txt
├── README.md
└── .env
