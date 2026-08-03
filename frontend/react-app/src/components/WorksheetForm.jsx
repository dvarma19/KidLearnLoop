// frontend/react-app/src/components/WorksheetForm.jsx
import React, { useState } from "react";
import { createWorksheet, submitWorksheet } from "../api";
import QuestionList from "./QuestionList";
import { parsePrintable } from "../utils/parsePrintable";
import FeedbackModal from "./FeedbackModal";

export default function WorksheetForm() {
  const [alias, setAlias] = useState("Kiddo");
  const [grade, setGrade] = useState(2);
  const [difficulty, setDifficulty] = useState("easy");

  const [accordionOpen, setAccordionOpen] = useState(true);
  const [feedbackOpen, setFeedbackOpen] = useState(false);
  const [validationError, setValidationError] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const [worksheetId, setWorksheetId] = useState(null);
  const [mathQuestions, setMathQuestions] = useState([]);
  const [englishQuestions, setEnglishQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [evaluation, setEvaluation] = useState(null);


  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // -----------------------------
  // Generate Worksheet
  // -----------------------------
  const handleGenerate = async () => {
    setLoading(true);
    setError("");

    try {
      const data = await createWorksheet({ alias, grade, difficulty });

      setWorksheetId(data.worksheet_id);

      // Parse printable text into structured questions
      const { math, english } = parsePrintable(data.printable);

      setMathQuestions(math);
      setEnglishQuestions(english);

      setAnswers({});

      // Auto-collapse accordion
      setAccordionOpen(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // -----------------------------
  // Validation
  // -----------------------------
  const allAnswersFilled = () => {
    const mathFilled = mathQuestions.every(
      (q) => answers[`math-${q.id}`] && answers[`math-${q.id}`].trim() !== ""
    );

    const englishFilled = englishQuestions.every(
      (q) => answers[`english-${q.id}`] && answers[`english-${q.id}`].trim() !== ""
    );

    return mathFilled && englishFilled;
  };

  // -----------------------------
  // Answer Change
  // -----------------------------
  const handleAnswerChange = (questionKey, value) => {
    setAnswers((prev) => ({
      ...prev,
      [questionKey]: value,
    }));
  };

  // -----------------------------
  // Submit Answers (opens modal)
  // -----------------------------
  const handleSubmit = () => {
    if (submitted) return;  // ignore further clicks

    if (!allAnswersFilled()) {
      setValidationError("Please answer all questions before submitting.");
      return;
    }

    setValidationError("");
    setFeedbackOpen(true);
  };


  return (
    <div className="worksheet-container">
      <h1><span className="hero-icon">📘</span> KidLearnLoop Worksheet</h1>

      {/* Accordion */}
      <div className="accordion">
        <div
          className="accordion-header"
          onClick={() => setAccordionOpen(!accordionOpen)}
        >
          <span className="accordion-icon">
            {accordionOpen ? "▲" : "▼"}
          </span>
        </div>

        {accordionOpen && (
          <div className="accordion-body">
            <div className="controls-panel">
              <div className="field">
                <label><span className="label-icon">👤</span> Child</label>
                <input
                  type="text"
                  value={alias}
                  onChange={(e) => setAlias(e.target.value)}
                />
              </div>

              <div className="field">
                <label><span className="label-icon">🎓</span> Grade</label>
                <input
                  type="number"
                  value={grade}
                  onChange={(e) =>
                    setGrade(parseInt(e.target.value || "0", 10))
                  }
                />
              </div>

              <div className="field">
                <label><span className="label-icon">⚙️</span> Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <option value="easy">easy</option>
                  <option value="medium">medium</option>
                  <option value="hard">hard</option>
                </select>
              </div>

              <button onClick={handleGenerate} disabled={loading}>
                {loading ? "Generating..." : "Generate Worksheet"}
              </button>
            </div>
          </div>
        )}
      </div>

      {error && <p className="error">{error}</p>}

      {/* Questions */}
      {worksheetId && (
        <div className="questions-panel">
          <QuestionList
            title="Math"
            questions={mathQuestions}
            answers={answers}
            evaluation={evaluation?.math_results || []}
            onAnswerChange={(id, val) => handleAnswerChange(`math-${id}`, val)}
          />

          <QuestionList
            title="English"
            questions={englishQuestions}
            answers={answers}
            evaluation={evaluation?.english_results || []}
            onAnswerChange={(id, val) => handleAnswerChange(`english-${id}`, val)}
          />

          <div className="submit-row">
            <button className="submitted-btn" onClick={handleSubmit} disabled={submitted}>
              {submitted ? "Worksheet Submitted" : "Submit Answers"}
            </button>

          </div>

          {validationError && (
            <p className="error" style={{ marginTop: "10px" }}>
              {validationError}
            </p>
          )}
        </div>
      )}

      {/* Feedback Modal */}
    <FeedbackModal
      open={feedbackOpen}
      onClose={() => setFeedbackOpen(false)}
      onSubmit={async (feedback) => {
        setFeedbackOpen(false);

        const payload = {
          worksheet_id: worksheetId,
          submitted_output: {
            math: mathQuestions.map((q) => ({
              id: q.id,
              question: q.question,
              answer: answers[`math-${q.id}`] || "",
            })),
            english: englishQuestions.map((q) => ({
              id: q.id,
              question: q.question,
              answer: answers[`english-${q.id}`] || "",
            })),
          },
          parent_feedback: feedback,
        };

        const res = await submitWorksheet(payload);
        setEvaluation(res.evaluation);
        // mark as submitted
        setSubmitted(true);

        alert("Worksheet submitted!");
      }}
    />

    </div>
  );
}
