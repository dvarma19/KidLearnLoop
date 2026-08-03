from datetime import datetime
import json
import sqlite3
import pandas as pd

DB_PATH = "kidlearnloop.db"


def get_child_history(child: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            """
            SELECT child, raw_output, score, ai_feedback, parent_feedback, difficulty, created_at
            FROM worksheets
            WHERE child = ?
            ORDER BY created_at DESC
            LIMIT 3
            """,
            conn,
            params=[child]
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["child", "raw_output", "score", "ai_feedback", "parent_feedback", "difficulty", "created_at"])


def extract_weaknesses(history_df):
    try:
        weaknesses = []

        for _, row in history_df.iterrows():
            fb = str(row.get("ai_feedback", "")).lower()

            if "tone" in fb:
                weaknesses.append("Reading Tone")
            if "comprehension" in fb:
                weaknesses.append("Reading Comprehension")
            if "word problem" in fb:
                weaknesses.append("Math Word Problems")
            if "reasoning" in fb:
                weaknesses.append("Math Reasoning")

        return list(set(weaknesses))
    except Exception:
        return []


def collect_previous_questions(history_df):
    try:
        questions = []
        for raw in history_df["raw_output"].tolist():
            try:
                data = json.loads(raw)
                for q in data.get("math", []):
                    questions.append(q.get("question", ""))
                for q in data.get("english", []):
                    questions.append(q.get("question", ""))
            except Exception:
                pass
        return "\n".join([q for q in questions if q])
    except Exception:
        return ""


def build_adaptive_prompt(child_profile: dict, difficulty: str):
    try:
        session_id = datetime.now().isoformat()
        child_alias = child_profile.get("alias")
        grade = child_profile.get("grade")

        history_df = get_child_history(child_alias)
        weaknesses = extract_weaknesses(history_df)
        previous_questions = collect_previous_questions(history_df)

        weakness_text = ""
        if weaknesses:
            weakness_text = (
                "Focus more on the following weak areas:\n"
                + "\n".join([f"- {w}" for w in weaknesses])
                + "\nGive 2x weightage to these topics.\n"
            )

        prompt = f"""
You are KidLearnLoop, an adaptive learning agent.
Session ID: {session_id}
Child alias: {child_alias}
Grade: {grade}

Here is the complete history of worksheets for this child:
{history_df.to_string()}

Previously used questions (do NOT repeat any of these):
{previous_questions}

{weakness_text}

Now generate a NEW worksheet based on the difficulty level {difficulty}:
- 5 unique math questions
- 5 unique English questions
- Difficulty should adapt based on past performance
- Avoid repeated question formats
- Increase challenge gradually
- Include variety

IMPORTANT CONSTRAINTS:
- You MUST NOT repeat any question text, scenario, numbers, or structure.
- If any question resembles a previous one, regenerate a different question.
- Every time you generate a worksheet, the questions must be different,
  even if the child alias and grade are the same.
- Do NOT reuse any question text, scenario, or numbers from previous worksheets.
- Do NOT duplicate questions across sections.
- Do NOT include any extra commentary outside the JSON.

Make the questions appropriate for the Ontario school curriculum for grade {grade} level.
The questions should be tailored towards the gifted school preparation guide.
Each question must be open-ended and should not include answer options.

Output raw JSON only with no markdown code fences and no surrounding text.
Return ONLY valid JSON in this format:
{{
    "math": [
        {{"id": 1, "question": "...", "answer": "...", "explanation": "..."}},
        ...
    ],
    "english": [
        {{"id": 1, "question": "...", "answer": "...", "explanation": "..."}},
        ...
    ]
}}

Each question object must include the fields "id", "question", "answer", and "explanation". 
For Math questions the answer should always be numeric.
The explanation should briefly explain the reasoning or expected response.
"""
        return prompt
    except Exception:
        return ""
