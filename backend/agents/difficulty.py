class DifficultyAdapter:
    def adapt(self, score, difficulty):
        try:
            if score == 0:
                return "easy"
            if score < 2:
                return difficulty
            return "medium" if difficulty == "easy" else "hard"
        except Exception:
            return "easy"
