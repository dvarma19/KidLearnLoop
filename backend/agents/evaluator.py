from groq import Groq
import os


class Evaluator:
    """
    Evaluates math and English worksheet answers.
    Math uses exact numeric matching.
    English uses semantic similarity via LLM.
    """

    def __init__(self, api_key=None, english_threshold=0.6):
        # Dependency injection (testable, configurable)
        self.client = Groq(api_key=api_key or os.getenv("GROQ_API_KEY"))
        self.english_threshold = english_threshold

    # -----------------------------
    # Lookup Builders
    # -----------------------------
    def _build_lookups(self, submitted):
        """Build separate math and English lookup dictionaries."""
        math_lookup = {q["id"]: q["answer"] for q in submitted.get("math", [])}
        english_lookup = {q["id"]: q["answer"] for q in submitted.get("english", [])}
        return math_lookup, english_lookup

    # -----------------------------
    # Semantic Evaluator (LLM)
    # -----------------------------
    def _semantic_match(self, question, correct_answer, user_answer):
        """Returns a semantic correctness score between 0 and 1."""
        prompt = f"""
            You are an evaluator for children's English writing.

            Question: {question}

            Expected answer (may be open-ended): {correct_answer}

            Child's answer: {user_answer}

            Evaluate semantic correctness on a scale of 0 to 1:
            - 1.0 means fully correct and aligned with the question
            - 0.0 means completely incorrect or irrelevant

            Return ONLY a number.
            """

        response = self.client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0
        )

        try:
            return float(response.choices[0].message.content.strip())
        except:
            return 0.0

    # -----------------------------
    # Math Evaluation
    # -----------------------------
    def _evaluate_math(self, worksheet, math_lookup):
        results = []
        correct_count = 0

        for q in worksheet["math"]:
            qid = q["id"]
            correct = q["answer"].strip().lower()
            user = math_lookup.get(qid, "").strip().lower()

            is_correct = user == correct
            if is_correct:
                correct_count += 1

            results.append({
                "id": qid,
                "question": q["question"],
                "correct_answer": correct,
                "user_answer": user,
                "is_correct": is_correct
            })

        return correct_count, results

    # -----------------------------
    # English Evaluation
    # -----------------------------
    def _evaluate_english(self, worksheet, english_lookup):
        results = []
        correct_count = 0

        for q in worksheet["english"]:
            qid = q["id"]
            correct = q["answer"].strip().lower()
            user = english_lookup.get(qid, "").strip().lower()

            score = self._semantic_match(q["question"], correct, user)
            is_correct = score >= self.english_threshold

            if is_correct:
                correct_count += 1

            results.append({
                "id": qid,
                "question": q["question"],
                "correct_answer": correct,
                "user_answer": user,
                "semantic_score": score,
                "is_correct": is_correct
            })

        return correct_count, results

    # -----------------------------
    # Public API
    # -----------------------------
    def evaluate(self, generated_worksheet, submitted_worksheet):
        """Main entry point for evaluating a worksheet."""
        math_lookup, english_lookup = self._build_lookups(submitted_worksheet)

        math_correct, math_results = self._evaluate_math(generated_worksheet, math_lookup)
        english_correct, english_results = self._evaluate_english(generated_worksheet, english_lookup)

        return {
            "math_score": math_correct,
            "english_score": english_correct,
            "total_math": len(generated_worksheet["math"]),
            "total_english": len(generated_worksheet["english"]),
            "math_results": math_results,
            "english_results": english_results
        }
