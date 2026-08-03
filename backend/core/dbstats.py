import sqlite3
import json

DB_PATH = "kidlearnloop.db"

class DBStats:
    @staticmethod
    def get_child_aliases():
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT child FROM worksheets ORDER BY child ASC")
            rows = cursor.fetchall()
            conn.close()
            return [r[0] for r in rows]
        except Exception:
            return []

    @staticmethod
    def fetch_child_history(child_alias):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, difficulty, created_at, score, ai_feedback
                FROM worksheets
                WHERE child = ?
                ORDER BY created_at DESC
            """, (child_alias,))

            rows = cursor.fetchall()
            conn.close()

            history = []
            for r in rows:
                history.append({
                    "worksheet_id": r[0],
                    "difficulty": r[1],
                    "created_at": r[2],
                    "score": r[3],
                    "ai_feedback": r[4],
                })

            return history
        except Exception:
            return []

    @staticmethod
    def fetch_dashboard(child_alias):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, created_at, difficulty, score, ai_feedback
                FROM worksheets
                WHERE child = ?
                ORDER BY created_at ASC
            """, (child_alias,))

            rows = cursor.fetchall()
            conn.close()

            history = []
            for r in rows:
                raw_score = r[3] or ""

                math_score = None
                english_score = None

                try:
                    score_json = json.loads(raw_score)
                    math_score = score_json.get("math_score")
                    english_score = score_json.get("english_score")
                except Exception:
                    pass

                history.append({
                    "worksheet_id": r[0],
                    "created_at": r[1],
                    "difficulty": r[2],
                    "score_raw": raw_score,
                    "math_score": math_score,
                    "english_score": english_score,
                    "ai_feedback": r[4],
                })

            return history
        except Exception:
            return []
