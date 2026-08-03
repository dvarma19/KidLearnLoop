# KidLearnLoop

KidLearnLoop is an AI-powered educational workflow for generating, evaluating, and tracking child-friendly math and English worksheets. The platform combines a FastAPI backend, React frontend, and lightweight dashboard tooling to help parents and educators create adaptive learning experiences with minimal manual effort.

## Overview

KidLearnLoop helps you:

- generate online/printable math and English worksheets for children
- evaluate submitted answer sheets using structured scoring logic
- produce AI-generated parent feedback based on recent history
- persist worksheet data and learning performance in SQLite
- expose a simple dashboard for child progress analysis
- support image-based answer submission through OCR workflows

## Project Structure

- `backend/` — FastAPI service, database models, AI agents, worksheet parsing and scoring
- `frontend/` — Streamlit and React UI entry points
- `generated_docs/` — exported DOCX worksheet files
- `db/` — database initialization and seeding helpers

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- React + Vite
- Streamlit
- Groq LLM integration
- python-docx
- easyocr

## Features

### Worksheet Generation

The backend can generate a worksheet tailored to a child profile and selected difficulty level. The generated raw output is normalized into structured math and English question sections, deduplicated, and saved for future evaluation.

### Evaluation Engine

Submitted worksheets are evaluated in two ways:

- math answers are matched against expected numeric answers
- English answers are passed through a semantic evaluator for approximate correctness scoring

### AI Feedback

The system builds a compact prompt from the child’s recent worksheet history and returns supportive parent-facing feedback that highlights strengths, weaknesses, and suggested next steps.

### Printable Output

The platform converts worksheet content into DOCX files so the assessment can be downloaded and printed.

### Progress Dashboard

A dashboard is available to view child history, worksheet scores, and AI feedback summaries.

## Prerequisites

Before running the project, make sure you have:

- Python installed
- a working virtual environment
- a Groq API key in your environment variables as `GROQ_API_KEY`

Optional environment variables:

- `GROQ_MODEL` — defaults to `llama-3.3-70b-versatile`

## Environment Setup

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Initialize the SQLite database:

```bash
python -m backend.db.init_db
```

5. Optionally seed sample records:

```bash
python -m backend.db.seed_dummy
```

## Running the Backend

Start the FastAPI backend:

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

You can also use the provided Windows batch helper:

```cmd
start.cmd
```

## Running the Frontends

### React App

```bash
cd frontend/react-app
npm install
npm run dev
```

### Streamlit Dashboard

```bash
streamlit run frontend/streamlit_dashboard.py
```

## API Overview

The backend exposes the following major endpoints:

- `GET /health` — health check
- `POST /worksheet/create` — generate a worksheet
- `GET /worksheet/docx/{worksheet_id}` — download generated DOCX
- `POST /worksheet/submit_worksheet` — submit structured worksheet answers
- `POST /worksheet/submit_image` — submit an image file for OCR-based evaluation
- `GET /dbstats/getChildren` — fetch child aliases
- `POST /dbstats/fetchChildHistory` — get child worksheet history
- `POST /dashboard` — fetch dashboard information for a child

## Development Notes

- The backend uses SQLite as the default persistence layer.
- Generated worksheets are stored as raw JSON in the database.
- The DOCX export is written into the `generated_docs/` folder.
- The codebase is organized around reusable backend agents and utility modules for generation, evaluation, history analysis, and formatting.

## Production Readiness Considerations

Before deploying this project to production, it is recommended to:

- move the database to a managed Postgres or MySQL service
- secure environment variables and secrets properly
- add authentication and authorization for admin endpoints
- add structured logging and monitoring
- add rate limiting and request validation hardening
- containerize the application with Docker

## License

This project is provided for educational and internal use as-is.
