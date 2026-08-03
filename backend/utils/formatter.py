def format_printable_worksheet(math, english):
    try:
        printable = []

        printable.append("### Math Worksheet\n")
        for i, q in enumerate(math, start=1):
            printable.append(f"{i}. {q.get('question', '')}\n")
            printable.append("   Answer: __________________________\n\n")

        printable.append("\n### English Worksheet\n")
        for i, q in enumerate(english, start=1):
            printable.append(f"{i}. {q.get('question', '')}\n")
            printable.append("   Answer: __________________________\n\n")

        return "".join(printable)
    except Exception:
        return ""
