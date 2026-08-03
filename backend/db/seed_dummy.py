import sqlite3
import datetime
import json

conn = sqlite3.connect("kidlearnloop.db")
cur = conn.cursor()

# Drop old table if exists
cur.execute("DROP TABLE IF EXISTS worksheets")

# Recreate table matching your model.py
cur.execute("""
CREATE TABLE worksheets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child TEXT,
    difficulty TEXT,
    raw_output TEXT,
    created_at DATETIME,
    score TEXT,
    parent_feedback TEXT,
    ai_feedback TEXT
)
""")

# Dummy worksheet data
dummy_data = [
    {
        "child": "Jim",
        "difficulty": "Easy",
        "raw_output": json.dumps({"math": [], "english": []}),
        "created_at": datetime.datetime(2026, 7, 10, 10, 0).isoformat(),
        "submitted_output": json.dumps({"math": [], "english": []}),
        "submitted_at": datetime.datetime(2026, 7, 10, 10, 0).isoformat(),
        "score": "Math: 5/5, English: 3/5",
        "parent_feedback": "He was focused and enjoyed the math section.",
        "ai_feedback": "Strong arithmetic skills. Needs improvement in reading comprehension."
    },
    {
        "child": "Jim",
        "difficulty": "Medium",
        "raw_output": json.dumps({"math": [], "english": []}),
        "created_at": datetime.datetime(2026, 7, 11, 10, 0).isoformat(),
        "submitted_output": json.dumps({"math": [], "english": []}),
        "submitted_at": datetime.datetime(2026, 7, 11, 10, 0).isoformat(),
        "score": "Math: 4/5, English: 4/5",
        "parent_feedback": "He was confident today.",
        "ai_feedback": "Balanced performance. Shows progress in English tone recognition."
    },
    {
        "child": "Jim",
        "difficulty": "Hard",
        "raw_output": json.dumps({"math": [], "english": []}),
        "created_at": datetime.datetime(2026, 7, 12, 10, 0).isoformat(),
        "submitted_output": json.dumps({"math": [], "english": []}),
        "submitted_at": datetime.datetime(2026, 7, 12, 10, 0).isoformat(),
        "score": "Math: 3/5, English: 2/5",
        "parent_feedback": "He found the word problems challenging.",
        "ai_feedback": "Math reasoning needs reinforcement. English comprehension dropped slightly."
    },
    {
        "child": "Jim",
        "difficulty": "Easy",
        "raw_output": json.dumps({"math": [], "english": []}),
        "created_at": datetime.datetime(2026, 7, 13, 10, 0).isoformat(),
        "submitted_output": json.dumps({"math": [], "english": []}),
        "submitted_at": datetime.datetime(2026, 7, 13, 10, 0).isoformat(),
        "score": "Math: 4/5, English: 3/5",
        "parent_feedback": "He was tired but tried his best.",
        "ai_feedback": "Consistent math accuracy. English tone identification still weak."
    }
]

for record in dummy_data:
    cur.execute("""
        INSERT INTO worksheets (child, difficulty, raw_output, created_at, submitted_output, submitted_at, score, parent_feedback, ai_feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        record["child"],
        record["difficulty"],
        record["raw_output"],
        record["created_at"],
        record["submitted_output"],
        record["submitted_at"],
        record["score"],
        record["parent_feedback"],
        record["ai_feedback"]
    ))

conn.commit()
conn.close()

print("✅ Dummy data inserted successfully.")
