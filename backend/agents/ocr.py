import easyocr


class OCRAgent:
    def __init__(self):
        try:
            self.reader = easyocr.Reader(["en"])
        except Exception:
            self.reader = None

    def extract_text(self, image_path: str):
        try:
            if self.reader is None:
                return ""
            result = self.reader.readtext(image_path, detail=0)
            return " ".join(result)
        except Exception:
            return ""
