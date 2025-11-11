https://chatgpt.com/c/69121bc5-b4cc-832d-b2a5-c1522b656433

test_simulator_app/
│
├── app.py
│
├── config/
│   ├── settings.yaml
│   ├── subjects.yaml
│
├── database/
│   ├── math/
│   │   ├── package_1/
│   │   │   ├── mcq/
│   │   │   │   ├── questions.json
│   │   │   │   ├── metadata.json
│   │   │   ├── essay/
│   │   │   │   ├── questions.json
│   │   │   │   ├── rubric.json
│   │   │
│   │   ├── package_2/
│   │   │   ├── mcq/
│   │   │   │   ├── questions.json
│   │   │   ├── essay/
│   │   │   │   ├── questions.json
│   │   │   │   ├── rubric.json
│   │
│   │   └── combined/
│   │       ├── combined_mcq.json        # auto-generated across all packages
│   │       ├── combined_essay.json
│   │       ├── combined_rubric.json
│
│   ├── physics/
│   │   ├── package_1/
│   │   ├── package_2/
│   │   └── combined/
│   │       ├── combined_mcq.json
│   │       ├── combined_essay.json
│
│   ├── chemistry/
│   │   ├── package_1/
│   │   └── combined/
│   │       ├── combined_mcq.json
│   │       ├── combined_essay.json
│
│   └── index.json                       # optional registry of all subjects and packages
│
├── modules/
│   ├── data_loader.py                   # Loads/merges questions per subject
│   ├── test_builder.py                  # Builds test sessions
│   ├── grading.py                       # Grades MCQs & essays
│   ├── utils.py
│
├── pages/
│   ├── 1_Home.py
│   ├── 2_Select_Package.py              # choose subject + package + mode
│   ├── 3_Take_Test.py
│   ├── 4_Review_Results.py
│   ├── 5_Admin_Panel.py
│
├── results/
│   ├── user_scores.json
│
├── assets/
│   ├── logo.png
│   ├── styles.css
│
├── requirements.txt
└── README.md
# question_bank
