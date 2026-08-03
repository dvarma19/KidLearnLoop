from backend.agents.local_generator import WorksheetGenerator


class DummyTokenizer:
    def __call__(self, prompt, return_tensors=None):
        return {}

    def decode(self, outputs, skip_special_tokens=True):
        return '[{"id": 1, "q": "2 + 2", "options": ["3", "4", "5", "6"]}]'


class DummyModel:
    def generate(self, **kwargs):
        return [0]


def test_generate_parses_structured_questions():
    generator = WorksheetGenerator.__new__(WorksheetGenerator)
    generator.model_name = "test"
    generator.tokenizer = DummyTokenizer()
    generator.model = DummyModel()
    generator.is_seq2seq = True

    result = generator.generate({"alias": "Jim", "grade": "2"}, "easy")

    assert result["child"] == "Jim"
    assert result["difficulty"] == "easy"
    assert result["questions"][0]["id"] == 1
    assert result["questions"][0]["options"][1] == "4"
