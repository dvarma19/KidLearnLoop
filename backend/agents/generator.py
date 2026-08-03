from groq import Groq

from backend.agents.history_engine import build_adaptive_prompt


class WorksheetGenerator:
    def __init__(self, api_key, model_name="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key) if api_key else None
        self.model_name = model_name

    def generate(self, child_profile, difficulty):
        try:
            prompt = build_adaptive_prompt(child_profile, difficulty)

            if self.client is None:
                return {
                    "child": child_profile.get("alias", ""),
                    "difficulty": difficulty,
                    "worksheet": ""
                }

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=900
            )

            text = response.choices[0].message.content

            return {
                "child": child_profile.get("alias", ""),
                "difficulty": difficulty,
                "worksheet": text
            }
        except Exception:
            return {
                "child": child_profile.get("alias", ""),
                "difficulty": difficulty,
                "worksheet": ""
            }
