# SkillBridge — Verifiable Skill Passport & Explainable Matching Platform

SkillBridge converts verified coursework, projects, hackathon competitions, and credentials into a portable **Digital Skill Passport** and matches students to internships and project teams with 100% explainability and fairness guarantees.

---

## Architecture Overview

- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS
- **Backend**: Python 3.10+ + FastAPI + SQLAlchemy + Pydantic v2 + Uvicorn
- **Database**: SQLite (local development default) / PostgreSQL (production ready)
- **Matching Engine**: Deterministic, evidence-backed matching service with strict demographic fairness guarantees

---

## Getting Started

### 1. Backend Setup & Startup

From the project root:

```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
# On Windows (PowerShell):
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# On macOS/Linux:
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the FastAPI backend server (runs on http://127.0.0.1:8000)
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- **Interactive API Documentation (Swagger)**: `http://127.0.0.1:8000/api/docs`
- **API Health Check**: `http://127.0.0.1:8000/api/health`

---

### 2. Frontend Setup & Startup

From the project root (in a separate terminal):

```bash
# Install frontend dependencies (if not already installed)
npm install

# (Optional) Verify environment variables in .env
# VITE_API_URL=http://127.0.0.1:8000

# Start Vite development server (runs on http://localhost:3000)
npm run dev
```

---

### 3. Running Backend Automated Tests

To execute the test suites verifying matching, unverified evidence penalties, 404 error handling, demographic fairness, Team Builder candidate matching, and persistent activities:

```bash
cd backend
# Phase 3 & 4 tests:
.\.venv\Scripts\python test_phase3.py
.\.venv\Scripts\python test_phase4.py

# Phase 6 Team Builder & Activities test suite:
.\.venv\Scripts\python test_phase6.py
```

---

### 4. Running Frontend Build & Typechecks

```bash
# Run TypeScript compilation check & production bundle build
cmd /c "npm run build"
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Health check (`{ "status": "ok", ... }`) |
| `GET` | `/api/docs` | Interactive Swagger API documentation |
| `GET` | `/api/students` | List registered students |
| `GET` | `/api/students/{id}` | Get student profile, verified skills, and evidence |
| `POST` | `/api/students` | Register a new student |
| `GET` | `/api/skills` | List all competencies & categories |
| `POST` | `/api/skills` | Create a new skill definition |
| `GET` | `/api/evidence` | List all submitted evidence items (Admin queue) |
| `POST` | `/api/evidence` | Submit new evidence (coursework, project, competition, certificate, internship) |
| `PATCH`| `/api/evidence/{id}/status` | Update evidence verification status (`verified`, `pending`, `rejected`) |
| `GET` | `/api/internships` | List all internship opportunities |
| `POST` | `/api/internships` | Create an internship opportunity with required skill levels |
| `GET` | `/api/recommendations/students/{student_id}` | Retrieve ranked internship recommendations with explainability rationale |
| `GET` | `/api/recommendations/students/{student_id}/internships/{internship_id}` | Detailed single-match explainability breakdown |
| `GET` | `/api/teams` | List all project teams |
| `POST` | `/api/teams` | Create project team with required skill competencies |
| `GET` | `/api/teams/{id}` | Get team details, roster, and skill requirements |
| `POST` | `/api/teams/{id}/members` | Add or invite student candidate to team |
| `GET` | `/api/teams/{id}/candidates` | Explainable candidate recommendations based on verified skill complementarity |
| `GET` | `/api/activities` | List persistent activity and notification log entries |
| `POST` | `/api/activities` | Record persistent activity log entry |
| `PATCH`| `/api/activities/{id}/read` | Mark activity notification as read |

---

## Explainable Matching Formula & Fairness Guarantee

$$\text{match\_score} = \text{round}\left(\frac{\text{satisfied\_required\_skills}}{\text{total\_required\_skills}} \times 100, 1\right)$$

- **Evidence Requirement**: Skills only contribute to the match score when supported by verified artifacts (`verification_status == 'verified'`).
- **Proficiency Threshold**: Requires $\text{student\_proficiency} \ge \text{required\_proficiency}$. Insufficient proficiencies are explicitly flagged.
- **Fairness Guarantee**: No protected attributes (gender, religion, caste, race, age, disability, university prestige) are ever factored into matching or ranking.

