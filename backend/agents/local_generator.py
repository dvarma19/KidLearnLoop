# import json
# import os
# import re
# from typing import Any, Dict, List

# from groq import Groq


# class WorksheetGenerator:
#     def __init__(self, model_name="google/flan-t5-base", api_key=None):
#         self.model_name = model_name
#         self.api_key = api_key or os.getenv("GROQ_API_KEY")
#         self.client = Groq(api_key=self.api_key) if self.api_key else None

#     def _parse_questions(self, text: str) -> List[Dict[str, Any]]:
#         cleaned = (text or "").strip()
#         if not cleaned:
#             return []

#         cleaned = cleaned.replace("```json", "").replace("```", "").strip()
#         if cleaned.lower().startswith("json"):
#             cleaned = cleaned[4:].strip()

#         try:
#             parsed = json.loads(cleaned)
#         except json.JSONDecodeError:
#             match = re.search(r"\[(.*?)\]", cleaned, re.S)
#             if match:
#                 try:
#                     parsed = json.loads(match.group(0))
#                 except json.JSONDecodeError:
#                     parsed = []
#             else:
#                 parsed = []

#         if isinstance(parsed, dict):
#             parsed = parsed.get("questions", [])
#         if not isinstance(parsed, list):
#             parsed = []

#         if parsed:
#             return parsed

#         lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
#         questions = []
#         for index, line in enumerate(lines, start=1):
#             if re.match(r"^\d+[.)]\s*", line):
#                 content = re.sub(r"^\d+[.)]\s*", "", line).strip()
#                 if content:
#                     questions.append({"id": index, "q": content})
#             elif line.lower().startswith("question"):
#                 questions.append({"id": index, "q": line.split(":", 1)[-1].strip()})

#         return questions

#     def generate(self, child_profile, difficulty):
#         if not self.client:
#             return {
#                 "child": child_profile["alias"],
#                 "difficulty": difficulty,
#                 "questions": [],
#                 "raw_output": "Missing GROQ API key",
#             }

#         prompt = (
#             f"Generate a {difficulty} math worksheet for a child named "
#             f"{child_profile['alias']} who is in grade {child_profile.get('grade', '2')}.\n"
#             f"Make the worksheet aligned to the Ontario curriculum, with a strong focus on the Halton Region District School Board learning expectations.\n"
#             f"Create exactly 3 open-ended math questions with no answer options.\n"
#             f"Return ONLY a JSON array with exactly 3 objects. Each object must have exactly two keys: id and q.\n"
#             f"Do not include markdown, explanations, or any other text."
#         )

#         response = self.client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[
#                 {"role": "system", "content": "You write short structured JSON arrays for educational worksheets."},
#                 {"role": "user", "content": prompt},
#             ],
#             temperature=0.2,
#             max_tokens=400,
#         )
#         text = response.choices[0].message.content
#         questions = self._parse_questions(text)

#         return {
#             "child": child_profile["alias"],
#             "difficulty": difficulty,
#             "questions": questions,
#             "raw_output": text,
#         }
