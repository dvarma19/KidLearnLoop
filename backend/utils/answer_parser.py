import re


def parse_answers(ocr_text: str) -> dict:
    """Extract child answers from OCR text for a worksheet.

    The parser is intentionally tolerant of common OCR artifacts from printed
    worksheets and simple handwritten answers. It supports lines like:
    "1. 4", "2) 9", or "1 4" and returns a dictionary keyed by question id.
    """
    try:
        if not ocr_text:
            return {}

        answers = {}
        section_pattern = re.compile(r"^(math|english)\s*$", re.IGNORECASE)
        answer_pattern = re.compile(
            r"(?<!\w)(\d+)\s*[\.\):\-]?\s*(.+?)(?=(?:\s+\d+\s*[\.\):\-]?|$))",
            re.IGNORECASE,
        )

        for raw_line in ocr_text.splitlines():
            line = re.sub(r"\s+", " ", raw_line).strip()
            if not line or section_pattern.match(line):
                continue

            for match in answer_pattern.finditer(line):
                question_id = int(match.group(1))
                answer = match.group(2).strip()
                answer = re.sub(r"^[\-\*•]+", "", answer).strip()
                answer = answer.strip(" .,:;!?\"")
                if answer:
                    answers[question_id] = answer

        return answers
    except Exception:
        return {}
