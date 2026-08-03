// frontend/react-app/src/utils/parsePrintable.js

export function parsePrintable(printable) {
  const lines = printable.split("\n");

  let currentSection = null;
  const math = [];
  const english = [];

  for (let line of lines) {
    line = line.trim();

    if (line.startsWith("### Math")) {
      currentSection = "math";
      continue;
    }
    if (line.startsWith("### English")) {
      currentSection = "english";
      continue;
    }

    // Match: "1. Question text"
    const match = line.match(/^(\d+)\.\s+(.*)/);
    if (match) {
      const id = parseInt(match[1], 10);
      const question = match[2].trim();

      if (currentSection === "math") {
        math.push({ id, question });
      } else if (currentSection === "english") {
        english.push({ id, question });
      }
    }
  }

  return { math, english };
}
