from groq import Groq

from backend.agents.history_engine import get_child_history


class AIFeedbackAgent:
    def __init__(self, api_key, model_name="llama-3.3-70b-versatile"):
        self.client = Groq(api_key=api_key) if api_key else None
        self.model_name = model_name

    def generate_feedback(self, child_alias: str, evaluation: dict, submitted_output: dict):
        try:
            history_df = get_child_history(child_alias)

            previous_feedbacks = []
            for _, row in history_df.iterrows():
                fb = row.get("ai_feedback", "")
                if fb:
                    previous_feedbacks.append(fb.strip())

            history_summary = []
            for _, row in history_df.iterrows():
                history_summary.append({
                    "created_at": str(row["created_at"]),
                    "difficulty": row["difficulty"],
                    "score": row["score"],
                    "parent_feedback": row.get("parent_feedback", ""),
                    "ai_feedback": row.get("ai_feedback", ""),
                })

            prompt = f"""
            You are KidLearnLoop, an AI tutor analyzing a child's learning progress.

            Child alias: {child_alias}

            ### CURRENT WORKSHEET PERFORMANCE
            Math: {evaluation['math_score']} / {evaluation['total_math']}
            English: {evaluation['english_score']} / {evaluation['total_english']}

            Math details:
            {evaluation['math_results']}

            English details:
            {evaluation['english_results']}

            Submitted answers:
            {submitted_output}

            ### RECENT HISTORY (last 3 worksheets)
            {history_summary}

            ### PREVIOUS AI FEEDBACK (for reference)
            {previous_feedbacks}

            ### TASK
            Write a short, crisp, encouraging summary for the parent.

            Rules:
            - DO NOT repeat previous feedback verbatim.
            - If the child shows the SAME pattern of mistakes as before, you MAY highlight it again — but phrase it differently.
            - If the child shows NEW mistakes or NEW strengths, emphasize those.
            - Identify strengths, weaknesses, recurring patterns, and improvement/decline.
            - Suggest 1-2 concrete next steps.
            - Recommend the next difficulty level (easy / medium / hard).
            - Tone must be supportive, child-friendly, and concise (4-5 sentences).
            - DO NOT say hi, thank you and other small talks. Be precise and direct in your job of giving feedback.
            """

            if self.client is None:
                return "Feedback generation is unavailable at the moment."

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=350,
            )

            return response.choices[0].message.content
        except Exception:
            return "Feedback generation is unavailable at the moment."
    