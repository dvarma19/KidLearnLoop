import unittest

from backend.main import _deduplicate_questions, _group_worksheet_questions, _normalize_worksheet_payload, _parse_worksheet_text
from backend.utils.answer_parser import parse_answers


class WorksheetParsingTests(unittest.TestCase):
    def test_normalize_worksheet_payload_flattens_sections(self):
        payload = {
            "math": [
                {"id": 1, "q": "2 + 2", "answer": "4", "explanation": "Add the numbers"}
            ],
            "english": [
                {"id": 1, "q": "Write a sentence", "answer": "Sample", "explanation": "n/a"}
            ],
        }

        result = _normalize_worksheet_payload(payload)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["type"], "math")
        self.assertEqual(result[1]["type"], "english")
        self.assertEqual(result[0]["answer"], "4")
        self.assertEqual(result[0]["question"], "2 + 2")

    def test_parse_worksheet_text_handles_fenced_json(self):
        text = '''```\n{\n  "math": [\n    {"id": 1, "q": "2 + 2", "answer": "4", "explanation": "Add the numbers"}\n  ],\n  "english": [\n    {"id": 1, "q": "Write a sentence", "answer": "Sample", "explanation": "n/a"}\n  ]\n}\n```'''

        result = _parse_worksheet_text(text)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["type"], "math")
        self.assertEqual(result[0]["answer"], "4")
        self.assertEqual(result[1]["type"], "english")

    def test_parse_worksheet_text_handles_groq_response_with_stray_backtick_and_trailing_comma(self):
        text = '''`\n{\n  "math": [\n    {"id": 1, "question": "A bookshelf has 5 shelves, and each shelf can hold 8 books. If the bookshelf is currently empty, how many books can be placed on it in total?", "answer": "40", "explanation": "To find the total number of books the bookshelf can hold, multiply the number of shelves by the number of books each shelf can hold."},\n    {"id": 2, "question": "A pencil is 15 cm long. If it is divided into 5 parts, how long is each part?", "answer": "3", "explanation": "To find the length of each part, divide the total length of the pencil by the number of parts it is divided into."},\n    {"id": 3, "question": "A basket contains 18 apples. If 6 apples are taken out, what fraction of the apples remains?", "answer": "2/3", "explanation": "To find the fraction of apples remaining, subtract the number of apples taken out from the total and divide by the total number of apples."},\n    {"id": 4, "question": "A water tank can hold 240 liters of water. If 120 liters of water are already in the tank, what percentage of the tank is filled?", "answer": "50%", "explanation": "To find the percentage of the tank filled, divide the amount of water in the tank by the total capacity and multiply by 100."},\n    {"id": 5, "question": "A toy car track is 12 meters long. If it is extended by 1/4 of its length, how long is the new track?", "answer": "15", "explanation": "To find the new length of the track, calculate 1/4 of the original length and add it to the original length."},\n    ],\n  "english": [\n    {"id": 1, "question": "What is the main idea of a story about a character who learns a valuable lesson?", "answer": "The main idea is the lesson or message the character learns.", "explanation": "The main idea of a story is often the central message or theme that the author wants to convey."},\n    {"id": 2, "question": "How does the use of descriptive language help the reader visualize a setting?", "answer": "It helps the reader create a mental image of the setting.", "explanation": "Descriptive language provides details about the setting, such as what it looks, sounds, and feels like, which helps the reader imagine it."},\n    {"id": 3, "question": "What is the purpose of using transitions in a paragraph?", "answer": "To connect ideas and make the text flow smoothly.", "explanation": "Transitions help to link ideas between sentences and paragraphs, making the text easier to follow and understand."},\n    {"id": 4, "question": "How can you determine the tone of a piece of writing?", "answer": "By analyzing the words and phrases the author uses.", "explanation": "The tone of a piece of writing is the author's attitude or feeling towards the subject, which can be determined by the language and tone used."},\n    {"id": 5, "question": "What is the difference between a simile and a metaphor?", "answer": "A simile compares two things using 'like' or 'as,' while a metaphor states that one thing is another.", "explanation": "Similes and metaphors are both literary devices used to make comparisons, but they are used in different ways to create different effects."]\n  }\n}\n```'''

        result = _parse_worksheet_text(text)

        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]["type"], "math")
        self.assertEqual(result[5]["type"], "english")

    def test_group_worksheet_questions_splits_sections(self):
        questions = [
            {"type": "math", "id": 1, "q": "2 + 2", "answer": "4", "explanation": "Add"},
            {"type": "english", "id": 1, "q": "Write a sentence", "answer": "Sample", "explanation": "n/a"},
        ]

        grouped = _group_worksheet_questions(questions)

        self.assertEqual(len(grouped["math"]), 1)
        self.assertEqual(len(grouped["english"]), 1)
        self.assertEqual(grouped["math"][0]["answer"], "4")

    def test_deduplicate_questions_removes_repeats(self):
        questions = [
            {"type": "math", "id": 1, "q": "2 + 2", "answer": "4", "explanation": "Add"},
            {"type": "math", "id": 2, "q": "2 + 2", "answer": "4", "explanation": "Add"},
            {"type": "english", "id": 1, "q": "Write a sentence", "answer": "Sample", "explanation": "n/a"},
        ]

        deduped = _deduplicate_questions(questions)

        self.assertEqual(len(deduped), 2)
        self.assertEqual(deduped[0]["question"], "2 + 2")

    def test_parse_worksheet_text_handles_groq_fenced_response(self):
        text = '''`\n{\n  "math": [\n    {"id": 1, "question": "A bookshelf has 5 shelves, and each shelf can hold 8 books. If the bookshelf is currently empty, how many books can be placed on it in total?", "answer": "40", "explanation": "To find the total number of books the bookshelf can hold, multiply the number of shelves by the number of books each shelf can hold."},\n    {"id": 2, "question": "A pencil is 15 cm long. If it is divided into 5 parts, how long is each part?", "answer": "3", "explanation": "To find the length of each part, divide the total length of the pencil by the number of parts it is divided into."},\n    {"id": 3, "question": "A basket contains 18 apples. If 6 apples are taken out, what fraction of the apples remains?", "answer": "2/3", "explanation": "To find the fraction of apples remaining, subtract the number of apples taken out from the total and divide by the total number of apples."},\n    {"id": 4, "question": "A water tank can hold 240 liters of water. If 120 liters of water are already in the tank, what percentage of the tank is filled?", "answer": "50%", "explanation": "To find the percentage of the tank filled, divide the amount of water in the tank by the total capacity and multiply by 100."},\n    {"id": 5, "question": "A toy car track is 12 meters long. If it is extended by 1/4 of its length, how long is the new track?", "answer": "15", "explanation": "To find the new length of the track, calculate 1/4 of the original length and add it to the original length."},\n    ],\n  "english": [\n    {"id": 1, "question": "What is the main idea of a story about a character who learns a valuable lesson?", "answer": "The main idea is the lesson or message the character learns.", "explanation": "The main idea of a story is often the central message or theme that the author wants to convey."},\n    {"id": 2, "question": "How does the use of descriptive language help the reader visualize a setting?", "answer": "It helps the reader create a mental image of the setting.", "explanation": "Descriptive language provides details about the setting, such as what it looks, sounds, and feels like, which helps the reader imagine it."},\n    {"id": 3, "question": "What is the purpose of using transitions in a paragraph?", "answer": "To connect ideas and make the text flow smoothly.", "explanation": "Transitions help to link ideas between sentences and paragraphs, making the text easier to follow and understand."},\n    {"id": 4, "question": "How can you determine the tone of a piece of writing?", "answer": "By analyzing the words and phrases the author uses.", "explanation": "The tone of a piece of writing is the author's attitude or feeling towards the subject, which can be determined by the language and tone used."},\n    {"id": 5, "question": "What is the difference between a simile and a metaphor?", "answer": "A simile compares two things using 'like' or 'as,' while a metaphor states that one thing is another.", "explanation": "Similes and metaphors are both literary devices used to make comparisons, but they are used in different ways to create different effects."]\n  }\n}\n```'''

        result = _parse_worksheet_text(text)

        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]["type"], "math")
        self.assertEqual(result[5]["type"], "english")

    def test_parse_answers_extracts_child_written_numbers_and_words(self):
        ocr_text = """Math
1. 4
2. 9
3. 2
English
1. cat
2. dog
"""

        result = parse_answers(ocr_text)

        self.assertEqual(result[1], "4")
        self.assertEqual(result[2], "9")
        self.assertEqual(result[3], "2")
        self.assertEqual(result[4], "cat")
        self.assertEqual(result[5], "dog")


if __name__ == "__main__":
    unittest.main()
