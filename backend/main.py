import json
import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Body
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any

from backend.core.dbstats import DBStats

try:
    from .db.models import Worksheet
    from .agents.generator import WorksheetGenerator
    from .agents.evaluator import Evaluator
    from .agents.difficulty import DifficultyAdapter
    from .utils.formatter import format_printable_worksheet
    from .utils.answer_parser import parse_answers
    from .agents.ocr import OCRAgent
    from .agents.ai_feedback import AIFeedbackAgent
    from .utils.docx_generator import generate_docx_from_printable
except ImportError:  # pragma: no cover - support running as a script
    from backend.db.models import Worksheet
    from backend.agents.generator import WorksheetGenerator
    from backend.agents.evaluator import Evaluator
    from backend.agents.difficulty import DifficultyAdapter
    from .utils.formatter import format_printable_worksheet
    from .utils.answer_parser import parse_answers
    from .agents.ocr import OCRAgent
    from .agents.ai_feedback import AIFeedbackAgent
    from .utils.docx_generator import generate_docx_from_printable

load_dotenv(Path(__file__).resolve().parents[1] / ".env")
logger = logging.getLogger(__name__)

engine = create_engine("sqlite:///kidlearnloop.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI(title="KidLearnLoop")
ocr_agent = OCRAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _normalize_worksheet_payload(payload):
    try:
        if not isinstance(payload, dict):
            return []

        questions = []
        for section_name in ("math", "english"):
            items = payload.get(section_name, []) or []
            if not isinstance(items, list):
                continue
            for item in items[:5]:
                if not isinstance(item, dict):
                    continue
                question_text = item.get("question") or item.get("q")
                question = {
                    "type": section_name,
                    "id": item.get("id"),
                    "question": question_text,
                    "answer": item.get("answer"),
                    "explanation": item.get("explanation"),
                }
                questions.append(question)
        return questions
    except Exception:
        logger.exception("Failed to normalize worksheet payload")
        return []


def _normalize_sectioned_worksheet_payload(payload):
    try:
        if not isinstance(payload, dict):
            return {"math": [], "english": []}

        normalized = {"math": [], "english": []}
        for section_name in ("math", "english"):
            items = payload.get(section_name, []) or []
            if not isinstance(items, list):
                continue

            for item in items[:5]:
                if not isinstance(item, dict):
                    continue

                normalized[section_name].append({
                    "id": item.get("id"),
                    "question": item.get("question") or item.get("q"),
                    "answer": item.get("answer"),
                    "explanation": item.get("explanation"),
                })

        return normalized
    except Exception:
        logger.exception("Failed to normalize sectioned worksheet payload")
        return {"math": [], "english": []}


def _flatten_sectioned_questions(sectioned_questions):
    try:
        flattened = []
        for section_name in ("math", "english"):
            for item in sectioned_questions.get(section_name, []) or []:
                flattened.append({
                    "type": section_name,
                    "id": item.get("id"),
                    "question": item.get("question"),
                    "answer": item.get("answer"),
                    "explanation": item.get("explanation"),
                })
        return flattened
    except Exception:
        logger.exception("Failed to flatten sectioned questions")
        return []


def _group_worksheet_questions(questions):
    try:
        grouped = {"math": [], "english": []}
        for question in questions:
            section = question.get("type")
            if section not in grouped:
                continue
            grouped[section].append({
                "id": question.get("id"),
                "question": question.get("question"),
                "answer": question.get("answer"),
                "explanation": question.get("explanation"),
            })
        return grouped
    except Exception:
        logger.exception("Failed to group worksheet questions")
        return {"math": [], "english": []}


def _deduplicate_questions(questions):
    try:
        unique_questions = []
        seen = set()

        for question in questions:
            section = question.get("type")
            question_text = question.get("question") or question.get("q") or ""
            text = question_text.strip().lower()
            if not section or not text:
                continue

            key = (section, text)
            if key in seen:
                continue

            seen.add(key)
            normalized_question = dict(question)
            normalized_question.setdefault("question", question_text)
            unique_questions.append(normalized_question)

        return unique_questions
    except Exception:
        logger.exception("Failed to deduplicate questions")
        return []


def _extract_json_object(text):
    try:
        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escaped = False

        for index in range(start, len(text)):
            char = text[index]

            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    return text[start:index + 1]

        return None
    except Exception:
        logger.exception("Failed to extract JSON object")
        return None


def _repair_groq_json_text(text):
    try:
        cleaned = text.strip()

        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, count=1, flags=re.IGNORECASE)
            cleaned = re.sub(r"\s*```$", "", cleaned, count=1)
        elif cleaned.startswith("`"):
            cleaned = cleaned[1:].strip()

        cleaned = cleaned.strip()
        if not cleaned:
            return ""

        try:
            cleaned = bytes(cleaned, "utf-8").decode("unicode_escape")
        except Exception:
            pass

        cleaned = re.sub(r'\]\s*\],\s*("(?:math|english)")', r'],\1', cleaned)
        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
        cleaned = re.sub(r'("explanation"\s*:\s*"[^"]*")\s*(\])', r'\1}\2', cleaned)
        cleaned = cleaned.strip("\n")
        return cleaned
    except Exception:
        logger.exception("Failed to repair Groq JSON text")
        return ""


def _parse_worksheet_sections(text):
    try:
        if not text:
            return {"math": [], "english": []}

        cleaned = _repair_groq_json_text(text)
        if not cleaned:
            return {"math": [], "english": []}

        extracted = _extract_json_object(cleaned)
        if extracted is None:
            return {"math": [], "english": []}

        repaired = _repair_groq_json_text(extracted)

        try:
            parsed = json.loads(repaired)
        except json.JSONDecodeError:
            return {"math": [], "english": []}

        return _normalize_sectioned_worksheet_payload(parsed)
    except Exception:
        logger.exception("Failed to parse worksheet sections")
        return {"math": [], "english": []}


def _parse_worksheet_text(text):
    try:
        sectioned_questions = _parse_worksheet_sections(text)
        flattened_questions = _flatten_sectioned_questions(sectioned_questions)
        return _deduplicate_questions(flattened_questions)
    except Exception:
        logger.exception("Failed to parse worksheet text")
        return []


GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
ai_feedback_agent = AIFeedbackAgent(api_key=GROQ_API_KEY, model_name=GROQ_MODEL)
generator = WorksheetGenerator(api_key=GROQ_API_KEY, model_name=GROQ_MODEL)
# generator = WorksheetGenerator(model_name="google/flan-t5-base")
# generator = WorksheetGenerator(model_name="mistralai/Mistral-7B-Instruct-v0.2")
# FLAN‑T5: fast, reliable JSON‑like output
# Mistral‑7B: more creative, heavier, still free on HF Spaces
evaluator = Evaluator()
adapter = DifficultyAdapter()
DOCS_DIR = "generated_docs"

class SubmittedWorksheet(BaseModel):
    worksheet_id: int
    submitted_output: Dict[str, List[Dict[str, Any]]]   # {"math": [...], "english": [...]}
    parent_feedback: str = ""

@app.get("/health")
def health():
    try:
        return {"status": "ok"}
    except Exception:
        logger.exception("Health check failed")
        return JSONResponse(status_code=500, content={"status": "error"})

@app.post("/worksheet/create")
def create_worksheet( child_alias: str = Query(...),
    grade: int = Query(2),
    difficulty: str = Query("easy")
    ):
    db = SessionLocal()
    try:
        ws = generator.generate({"alias": child_alias, "grade": grade}, difficulty)
        worksheet_text = ws.get("worksheet", "")
        sectioned_questions = _parse_worksheet_sections(worksheet_text)
        questions = _deduplicate_questions(_flatten_sectioned_questions(sectioned_questions))
        grouped_questions = _group_worksheet_questions(questions)

        worksheet = Worksheet(
            child=child_alias,
            grade=grade,
            difficulty=difficulty,
            raw_output=json.dumps(ws),
            submitted_output='',
            score='',
            parent_feedback='',
            ai_feedback=''
        )

        db.add(worksheet)
        db.commit()
        db.refresh(worksheet)

        printable = format_printable_worksheet(
            grouped_questions.get("math", []),
            grouped_questions.get("english", [])
            )

        output_path = f"generated_docs/{child_alias}_worksheet_{worksheet.id}.docx"
        os.makedirs("generated_docs", exist_ok=True)

        generate_docx_from_printable(printable, output_path)

        return {
            "worksheet_id": worksheet.id,
            "printable": printable,
            "docx_url": f"http://localhost:8000/worksheet/docx/{worksheet.id}",
            "docx_filename": output_path
        }
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to create worksheet")
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        db.close()


@app.get("/worksheet/docx/{worksheet_id}")
def download_docx(worksheet_id: int):
    try:
        for filename in os.listdir("generated_docs"):
            if filename.endswith(f"worksheet_{worksheet_id}.docx"):
                file_path = os.path.join("generated_docs", filename)
                return FileResponse(
                    file_path,
                    media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    filename=filename
                )

        return {"error": "File not found"}
    except Exception:
        logger.exception("Failed to download worksheet docx")
        return JSONResponse(status_code=500, content={"error": "Unable to download worksheet file"})


@app.post("/worksheet/submit_worksheet")
async def submit_worksheet(payload: SubmittedWorksheet):
    db = SessionLocal()
    try:
        ws = db.query(Worksheet).filter(Worksheet.id == payload.worksheet_id).first()
        if not ws:
            return {"error": "Worksheet not found"}

        ws.submitted_output = json.dumps(payload.submitted_output)
        ws.parent_feedback = payload.parent_feedback

        worksheet_json = json.loads(ws.raw_output)
        answers_dict = {}

        for q in payload.submitted_output.get("math", []):
            answers_dict[q["id"]] = q["answer"]

        for q in payload.submitted_output.get("english", []):
            answers_dict[q["id"]] = q["answer"]

        evaluator = Evaluator()
        original_worksheet = json.loads(worksheet_json.get('worksheet'))
        submitted_worksheet = json.loads(ws.submitted_output)
        evaluation_result = evaluator.evaluate(original_worksheet, submitted_worksheet)

        ws.score = json.dumps({
            "math_score": evaluation_result["math_score"],
            "english_score": evaluation_result["english_score"]
        })

        ai_feedback_text = ai_feedback_agent.generate_feedback(
            child_alias=ws.child,
            evaluation=evaluation_result,
            submitted_output=payload.submitted_output
        )

        ws.ai_feedback = ai_feedback_text

        db.commit()
        db.refresh(ws)

        return {
            "status": "success",
            "worksheet_id": ws.id,
            "message": "Worksheet submitted and evaluated successfully",
            "evaluation": evaluation_result
        }
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to submit worksheet evaluation")
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        db.close()

# For future use: if we want to submit an image of a worksheet instead of structured answers
@app.post("/worksheet/submit_image")
async def submit_image(
    worksheet_id: int,
    parent_feedback: str = "",
    file: UploadFile = File(...)
):
    db = SessionLocal()
    try:
        ws = db.query(Worksheet).filter(Worksheet.id == worksheet_id).first()
        if not ws:
            return {"error": "Worksheet not found"}

        temp_path = f"temp_{worksheet_id}.jpg"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        ocr_text = ocr_agent.extract_text(temp_path)
        answers = parse_answers(ocr_text)

        import json
        worksheet_data = json.loads(ws.raw_output)

        evaluation = evaluator.evaluate(worksheet_data, answers)

        score_text = (
            f"Math: {evaluation['math_score']}/{evaluation['total_math']}, "
            f"English: {evaluation['english_score']}/{evaluation['total_english']}"
        )

        ai_feedback = ai_feedback_agent.generate_feedback(
            child_alias=ws.child,
            evaluation=evaluation,
            submitted_output=answers
        )

        ws.score = score_text
        ws.parent_feedback = parent_feedback
        ws.ai_feedback = ai_feedback
        db.commit()

        return {
            "worksheet_id": worksheet_id,
            "answers": answers,
            "evaluation": evaluation,
            "score": score_text,
            "parent_feedback": parent_feedback,
            "ai_feedback": ai_feedback
        }
    except Exception as exc:
        db.rollback()
        logger.exception("Failed to submit image worksheet")
        return JSONResponse(status_code=500, content={"error": str(exc)})
    finally:
        db.close()


@app.get("/dbstats/getChildren")
def get_children():
    try:
        aliases = DBStats.get_child_aliases()
        return {"children": aliases}
    except Exception:
        logger.exception("Failed to fetch child aliases")
        return JSONResponse(status_code=500, content={"error": "Unable to fetch children"})


@app.post("/dbstats/fetchChildHistory")
def fetch_child_history(payload: dict):
    try:
        child_alias = payload.get("child_alias")
        if not child_alias:
            return {"error": "child_alias is required"}

        history = DBStats.fetch_child_history(child_alias)
        return {"history": history}
    except Exception:
        logger.exception("Failed to fetch child history")
        return JSONResponse(status_code=500, content={"error": "Unable to fetch child history"})


@app.post("/dashboard")
def dashboard(payload: dict):
    try:
        child_alias = payload.get("child_alias")
        if not child_alias:
            return {"error": "child_alias is required"}

        history = DBStats.fetch_dashboard(child_alias)
        return {"history": history}
    except Exception:
        logger.exception("Failed to fetch dashboard data")
        return JSONResponse(status_code=500, content={"error": "Unable to fetch dashboard data"})