# Code Review and Fix Report

This document summarizes the issues found in the codebase, what was fixed, and why.

## 1) Bugs, Errors, or Broken Logic Identified

- `app.py`: PDF file handle risk in `generate_questions_from_pdf`.
  - The PDF was opened without a context manager, so file handles could remain open longer than necessary.

- `app.py`: Temporary PDF cleanup risk.
  - Uploaded files were always written to `temp.pdf` but never deleted after generation, causing stale temp file buildup.

- `app.py`: Package listing could include non-directory items.
  - `load_packages` used `os.listdir` and only filtered dotfiles, which could surface invalid package entries.

- `app.py`: Fragile package metadata access.
  - UI used direct dictionary indexing (`package['package_id']`, `package['source']`, `package['level']`), which can raise `KeyError` for malformed or partial JSON.

## 2) Fixes Applied

### File Updated
- `app.py`

### Changes
- Reordered imports for readability and consistency.
- Wrapped PDF opening in a context manager:
  - `with fitz.open(pdf_path) as doc:`
- Added guaranteed temp-file cleanup with `try/finally` around generation.
- Hardened `load_packages`:
  - now returns only actual directories
  - sorted output for stable UI ordering
- Replaced fragile dictionary indexing in the test UI header/level with safe `.get(...)` defaults.
- Added a small metadata field (`source_text_chars`) to make extracted content presence observable in placeholder mode.

## 3) Code Cleanup Performed

- Reduced redundancy by using a compact text extraction expression:
  - `"".join(page.get_text("text") for page in doc)`
- Normalized formatting in nested dictionaries and function calls for better readability.
- Improved deterministic behavior by sorting package lists.

## 4) Inline Comments Added for Complex Logic

Inline comments were added in `app.py` where logic benefits from context:

- In PDF generation flow:
  - explains why context extraction remains in placeholder mode and why resource cleanup matters.
- In submit/generation flow:
  - explains temp-file deletion purpose and lifecycle.

## 5) Fixed Version + Summary of What Changed and Why

### Fixed Version
- The fixed implementation is in:
  - `app.py`
- Original `README.md` content has been moved to:
  - `notes.md`

### Why these changes were made
- Prevent runtime/resource issues (open file handles, stale temp files).
- Make package selection safer and more predictable.
- Avoid avoidable UI crashes from missing package JSON keys.
- Improve maintainability and readability without changing intended app behavior.

## Validation

- Syntax check passed:
  - `python3 -m py_compile app.py pages/02_Question_Add.py pages/01_View_Results.py pages/3_📊_View_Results_Expanded.py pages/3_📊_View_Results_Table.py`

---

# Project Documentation

## 1. Project Overview

`question_bank` is a Streamlit-based application for building, delivering, and reviewing question-bank assessments from structured JSON packages.

The project solves three related problems:
- Creating reusable question packages (MCQ + essay) from source learning material.
- Running interactive tests and auto-grading responses.
- Persisting and reviewing submission outcomes for learning analytics and feedback.

Current generation is placeholder-based in `app.py` (GPT integration is scaffolded but disabled).

## 2. Tech Stack

- Language:
  - Python 3

- Framework/UI:
  - Streamlit

- Core Libraries:
  - `pandas` (tabular result views and CSV export)
  - `PyMuPDF` / `fitz` (PDF text extraction for package generation flow)
  - Standard library: `json`, `os`, `pathlib`, `datetime`, `uuid`, `typing`, `re`

- Data Format:
  - JSON files for packages and user submissions

## 3. Architecture Overview

High-level components:

- `app.py`
  - Main entrypoint.
  - Two modes:
    - Generate Question Bank (PDF upload -> JSON package)
    - Take Test (load package -> render MCQ/essay -> grade -> save submission)

- `pages/`
  - `02_Question_Add.py`: helper UI to build MCQ JSON interactively.
  - `01_View_Results.py`: results viewer with MCQ/essay comparison tables.
  - `3_📊_View_Results_Expanded.py`: expanded per-question review UI.
  - `3_📊_View_Results_Table.py`: table-focused results review UI.

- `database/`
  - Stores subject/package question banks at:
  - `database/<subject>/<package_id>/package.json`

- `results/user_submissions/`
  - Stores per-test submission outputs:
  - `<subject>_<package_id>_<timestamp>.json`

Data flow:
1. Author/generator creates `package.json`.
2. Test taker selects subject/package and submits answers.
3. App grades MCQ and essays (keyword/rubric matching for essay).
4. App writes graded result JSON.
5. Results pages read both package + submission and render review tables.

## 4. Installation & Setup

### Prerequisites

- Python 3.10+ recommended
- `pip`

### Steps

1. Clone repository and enter project directory.

```bash
git clone <your-repo-url>
cd question_bank
```

2. (Recommended) Create and activate a virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Run the Streamlit app.

```bash
streamlit run app.py
```

5. Open the local URL shown in terminal (usually `http://localhost:8501`).

## 5. Usage Guide

### A) Generate a Question Package

1. Open app sidebar mode: `🏗️ Generate Question Bank`.
2. Enter:
- Subject (example: `machine_vision`)
- Difficulty level
- Package ID (example: `package_35`)
3. Upload a PDF.
4. Click `🚀 Generate Questions`.
5. App saves to:
- `database/<subject>/<package_id>/package.json`

Note: Generation currently returns placeholder essay content in `app.py` unless GPT integration is re-enabled.

### B) Take a Test

1. Switch mode to `🧩 Take Test`.
2. Select subject and package.
3. Answer MCQs and essay prompts.
4. Click `Submit Answers`.
5. View scores and final metric.
6. Submission file is saved to:
- `results/user_submissions/<subject>_<package_id>_<timestamp>.json`

### C) Review Results

Use any results page in `pages/` to:
- Select submission files
- Compare user MCQ answers vs correct answers
- Inspect essay keyword matching
- Export CSV comparisons

## 6. API Reference (If Applicable)

This project currently does **not** expose HTTP REST/GraphQL endpoints.

Internal callable logic (function-level API) is primarily in `app.py` and results pages:
- `generate_questions_from_pdf(pdf_path, package_id, source, level, subject) -> dict`
- `save_json(data, subject, package_id) -> None`
- `load_packages(subject) -> list[str]`
- `grade_mcq(mcq_data, user_answers) -> (correct_count, total_count)`
- `grade_essay(essay_data, user_text) -> (score, total_points, matched_keywords)`

If you plan to add a backend API, define schema contracts for package and submission payloads first.

## 7. Environment Variables

`.env` is optional in the current state. Recommended variables:

- `OPENAI_API_KEY`
  - Required only if GPT generation is re-enabled.

Optional (future hardening):
- `RESULTS_DIR`
- `DATABASE_DIR`
- `APP_ENV` (e.g., `dev`, `prod`)

Minimal example:

```env
OPENAI_API_KEY=your_api_key_here
```

## 8. Contributing Guide

1. Fork the repo.
2. Create a feature branch.

```bash
git checkout -b feat/your-change
```

3. Make focused changes with clear commit messages.
4. Run basic checks before PR:

```bash
python3 -m py_compile app.py pages/02_Question_Add.py pages/01_View_Results.py pages/3_📊_View_Results_Expanded.py pages/3_📊_View_Results_Table.py
```

5. Open a Pull Request including:
- What changed
- Why it changed
- Any migration/data impact
- Screenshots for UI updates (if applicable)

Contribution expectations:
- Keep JSON structures backward-compatible where possible.
- Avoid hardcoding local paths.
- Add inline comments only where logic is non-obvious.

## 9. License

No license file is currently present in the repository.

Recommendation:
- Add a `LICENSE` file (for example, MIT, Apache-2.0, or GPL-3.0) and update this section to match.

---

# Scaling Guide

## 1. Current Bottlenecks

What will break first under load in the current implementation:

- File-based storage contention:
  - `results/user_submissions/*.json` writes are local filesystem operations with no queueing/locking strategy.
- Directory scanning latency:
  - result viewers use repeated `os.listdir` + in-memory filtering; this slows as file count grows.
- Single-process app runtime:
  - Streamlit app execution is not designed as a high-concurrency stateless API tier.
- In-memory processing per request:
  - package/result parsing and DataFrame builds happen repeatedly without shared cache layer.
- No auth/multi-tenant controls:
  - all data is effectively global; privacy/isolation and auditability will fail at scale.

## 2. Database Scaling

Move from JSON files to managed database + object storage.

Recommended data model split:
- Relational DB (metadata, users, attempts, scores, package indices)
- Object storage (large package JSON versions, raw uploads, exports)

### Indexing

Suggested initial indexes:
- `submissions(user_id, submitted_at DESC)`
- `submissions(subject, package_id, submitted_at DESC)`
- `packages(subject, package_id, version)` unique
- `essay_scores(submission_id)`

### Caching

- Use Redis for:
  - hot package metadata
  - recent submissions list
  - precomputed leaderboard/analytics views
- Cache invalidation on package publish and submission write events.

### Read Replicas

- Add DB read replicas when read-heavy dashboards start impacting write latency.
- Route analytics/result browsing to replicas; keep writes on primary.

### Sharding (later-stage)

- Prefer logical partitioning before true sharding:
  - partition by `tenant_id` or `subject` or time (`submitted_at` month).
- Use sharding only when single-primary scaling ceiling is reached.

## 3. Backend Scaling

Current app should evolve into separate services.

Target backend split:
- `web-ui` service (Streamlit or migrated frontend)
- `api` service (FastAPI/Node/Go; stateless)
- `worker` service (grading, package generation, async processing)
- `queue` (SQS/PubSub/Service Bus + DLQ)

### Load balancing

- Put API behind managed load balancer.
- Use health checks, connection draining, and autoscaling policies.

### Horizontal vs Vertical

- MVP/early growth: vertical scaling is fastest.
- Sustained growth: horizontal scaling for API/worker pods.
- Keep sessions stateless; store session/auth in Redis/JWT-backed flows.

## 4. Frontend Scaling

If remaining on Streamlit:
- Front with CDN + reverse proxy for static assets.
- Paginate and virtualize large result tables.
- Cache expensive computed views.

If migrating to web app framework:
- Use Next.js/Nuxt/SvelteKit for SSR/SSG where needed.
- Lazy load heavy charts/tables.
- Split bundles and prefetch route-critical assets.

### CDN

- Cache static assets globally.
- Signed URLs for private downloadable result exports.

### SSR/SSG options

- SSR for authenticated dashboards requiring fresh data.
- SSG for docs/help/marketing pages.
- Hybrid ISR for semi-static analytics pages.

## 5. Infrastructure (Recommended Cloud Setup)

Below is one practical AWS-first reference. Equivalent GCP/Azure options are listed.

### AWS (recommended baseline)

- Compute:
  - ECS Fargate or EKS for API + workers
  - App Runner acceptable for early stages
- Networking:
  - ALB + CloudFront + Route53 + ACM
- Data:
  - RDS PostgreSQL (Multi-AZ)
  - ElastiCache Redis
  - S3 for artifacts/exports/raw docs
- Async:
  - SQS + DLQ
- Observability:
  - CloudWatch + X-Ray + OpenSearch (optional)
- Security:
  - IAM least privilege, Secrets Manager, WAF, Shield Standard
- CI/CD:
  - GitHub Actions -> ECR -> ECS deploy

### GCP equivalents

- Cloud Run/GKE, Cloud SQL (Postgres), Memorystore (Redis), GCS, Pub/Sub, Cloud CDN, Cloud Armor, Secret Manager.

### Azure equivalents

- AKS/App Service, Azure Database for PostgreSQL, Azure Cache for Redis, Blob Storage, Service Bus, Front Door/CDN, Key Vault, Defender for Cloud.

## 6. Cost Estimate (Rough Monthly Infra)

Assumptions:
- Moderate usage patterns, not video-heavy.
- Includes compute, DB, cache, storage, network egress, and monitoring.
- Excludes engineering payroll and enterprise support contracts.

### ~1k users/month (early production)
- Compute: $50-$150
- DB: $60-$150
- Redis/cache: $20-$60
- Storage + CDN + egress: $20-$80
- Observability/misc: $20-$60
- Total: **~$150-$500/month**

### ~10k users/month (growth)
- Compute: $200-$800
- DB (larger instance + backups): $200-$700
- Redis/cache: $80-$250
- Storage + CDN + egress: $150-$600
- Observability/misc: $100-$300
- Total: **~$700-$2,650/month**

### ~100k users/month (scaled production)
- Compute: $1,500-$6,000
- DB cluster/read replicas: $1,500-$8,000
- Redis/cache: $400-$2,000
- Storage + CDN + egress: $1,000-$8,000
- Observability/security/misc: $500-$3,000
- Total: **~$4,900-$27,000/month**

Notes:
- Costs vary heavily with traffic shape, region, retention, and egress.
- Egress and analytics workloads are usually the fastest cost multipliers.

## 7. Roadmap (MVP -> Production-Grade)

1. Stabilize data contracts
- Define strict schemas for package/submission payloads.
- Add schema validation and migration versioning.

2. Extract backend API
- Move grading/submission logic into a stateless API service.
- Keep Streamlit as thin client initially.

3. Replace file storage writes
- Write submission metadata to Postgres.
- Store large blobs/artifacts in object storage.

4. Introduce async workers
- Queue grading/generation jobs.
- Add retry policy + dead-letter queue.

5. Add caching layer
- Redis cache for hot package/result queries.
- Add cache invalidation hooks on writes.

6. Add auth + tenancy
- OIDC/SAML-ready auth.
- Tenant isolation at data and API layers.

7. Observability and SLOs
- Central logs, metrics, tracing.
- Define SLOs (latency, error rate, job completion time).

8. Scale reads/writes
- Add DB read replicas.
- Partition large tables; archive cold data.

9. Security hardening
- WAF, secrets rotation, vulnerability scans, audit logging.
- Data retention and privacy controls.

10. Global performance
- CDN optimization, multi-region read strategy if needed.
- Disaster recovery runbooks and regular restore drills.

---

# Competitive Landscape (10 Similar Apps/Companies)

Notes:
- "Tech stack" is listed only where publicly known or strongly indicated.
- "Scale" uses public signals (reported users/institutions/enterprise footprint), not audited MAU for every platform.

## 1) Quizlet
- What they do: Study sets, flashcards, quizzes, and AI-assisted study workflows for students.
- Tech stack (known): Web + mobile apps; exact backend stack not publicly detailed.
- Business model: Freemium + subscription (Quizlet Plus) + advertising.
- Scale: Publicly reports ~60M learners / MAU-level usage signals.
- Why successful: Huge UGC content network and strong student habit loop.
- Your niche opportunity: Focus on instructor-grade assessment integrity and rubric-first essay evaluation (not just study tools).

## 2) Kahoot!
- What they do: Game-based quizzes for classrooms and workplace learning/engagement.
- Tech stack (known): Cloud SaaS, web/mobile apps; exact internal stack not fully disclosed.
- Business model: Freemium + paid education/workplace plans + content ecosystem.
- Scale: Publicly reports billions of cumulative participants and multi-million educator usage.
- Why successful: Viral game UX and low-friction participation.
- Your niche opportunity: Position as "serious assessment + feedback quality" vs trivia/game-first engagement.

## 3) Canvas (Instructure)
- What they do: Full LMS with assignments, quizzes, grading, and integrations.
- Tech stack (known): SaaS LMS platform with APIs and large-scale cloud operations.
- Business model: Institutional subscriptions (schools, colleges, organizations).
- Scale: Publicly states tens of millions of users and peak multi-million concurrency.
- Why successful: Deep institutional fit, reliability, ecosystem integrations.
- Your niche opportunity: Lightweight, assessment-centric workflow without full LMS complexity.

## 4) Moodle
- What they do: Open-source LMS with extensive plugin ecosystem and assessment tooling.
- Tech stack (known): Open-source PHP-based LMS ecosystem.
- Business model: Open source core + partner services/hosting/support.
- Scale: Public Moodle statistics report very large global registered-site/user footprint.
- Why successful: Flexibility, ownership, and strong global community.
- Your niche opportunity: Offer opinionated defaults and faster out-of-box assessment workflows than highly customizable LMS setups.

## 5) Blackboard (Anthology)
- What they do: Enterprise LMS for higher-ed/corporate learning with assessment capabilities.
- Tech stack (known): Enterprise SaaS LMS; specific internals not fully public.
- Business model: Institutional contracts and platform services.
- Scale: Broad higher-ed presence and large institutional customer base.
- Why successful: Longstanding enterprise procurement footprint and institutional integrations.
- Your niche opportunity: Better UX and faster deployment for teams that find legacy LMS tooling heavy.

## 6) Google Classroom
- What they do: Assignment and classroom workflow management integrated with Google Workspace.
- Tech stack (known): Google cloud ecosystem; deep integration with Drive/Docs/Workspace.
- Business model: Included with Google Workspace for Education tiers (free + paid editions).
- Scale: Very large global K-12/higher-ed footprint (widely adopted at school-system level).
- Why successful: Zero-friction adoption where schools already use Google accounts.
- Your niche opportunity: Advanced testing analytics and richer rubric-driven grading than baseline classroom workflows.

## 7) ExamSoft
- What they do: High-stakes digital assessment and secure/offline exam delivery.
- Tech stack (known): Secure exam client + assessment SaaS platform.
- Business model: Institutional licensing (professional schools, certification contexts).
- Scale: Large footprint in professional/high-stakes testing contexts.
- Why successful: Reliability focus for controlled exam environments.
- Your niche opportunity: Mid-stakes and formative assessments with better authoring UX and lower operational overhead.

## 8) Questionmark
- What they do: Enterprise assessment platform for certification, compliance, and workforce testing.
- Tech stack (known): Enterprise assessment SaaS with integrations.
- Business model: B2B licensing and enterprise contracts.
- Scale: Global enterprise/government deployments.
- Why successful: Compliance posture, enterprise features, and reporting depth.
- Your niche opportunity: Serve SMEs/academic programs needing enterprise-like quality without enterprise complexity/pricing.

## 9) ProProfs Quiz Maker
- What they do: Quiz/test authoring and deployment for education and business training.
- Tech stack (known): Web SaaS platform; exact backend stack not publicly detailed.
- Business model: Freemium + subscription tiers.
- Scale: Broad SMB and training-market adoption signals.
- Why successful: Easy authoring and all-in-one tool packaging.
- Your niche opportunity: Differentiated quality controls (question schema validation, versioning, auditability) for more rigorous assessment use.

## 10) ClassMarker
- What they do: Online testing platform for graded exams/quizzes and certification-style use.
- Tech stack (known): Hosted SaaS exam platform.
- Business model: Subscription/usage-based plans.
- Scale: Long-running global product used by educators and businesses.
- Why successful: Simplicity, reliability, and focused exam workflow.
- Your niche opportunity: Add richer AI-assisted generation + transparent rubric scoring + modern analytics layer.

## Where You Can Carve a Clear Niche

Suggested positioning for this project:

- Assessment-first (not LMS-first):
  - Keep creation -> delivery -> grading -> review tightly integrated.
- Transparent grading:
  - Show rubric criteria matches, score rationale, and per-question diagnostics.
- Lightweight deployability:
  - Faster than enterprise LMS rollouts; more rigorous than casual quiz tools.
- JSON-native, versioned content ops:
  - Treat question banks as versioned assets with migration/validation pipelines.
- AI-assisted, human-governed authoring:
  - Use AI for drafting, but keep deterministic schemas and review gates.

## Source Links

- Quizlet About: https://quizlet.com/mission
- Quizlet audience/scale signal: https://quizlet.com/ads/Audiences
- Kahoot company and key numbers: https://kahoot.com/company/
- Canvas scale signal: https://www.instructure.com/canvas
- Moodle live stats: https://stats.moodle.org/?lang=en_us
- Moodle 500M users announcement: https://moodle.com/news/500-million-users-on-registered-moodle-sites/
- Blackboard (Anthology) product page: https://www.anthology.com/blackboard/
- Anthology scale signal (institutions): https://www.blackboard.com/news/anthology-celebrates-transformational-first-year-serving-over-2000-higher-education
- Google Classroom product overview PDF (includes scale claim): https://www.govconnection.com/media/l3en4sbp/google-classroom.pdf
- ExamSoft about: https://examsoft.com/about-examsoft/
- Questionmark platform: https://www.questionmark.com/platform/
- ClassMarker about: https://www.classmarker.com/online-testing/about
- ProProfs about: https://www.proprofs.com/about/
