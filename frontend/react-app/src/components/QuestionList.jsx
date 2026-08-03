// frontend/react-app/src/components/QuestionList.jsx
import React from "react";

export default function QuestionList({ title, questions, answers, evaluation, onAnswerChange }) {
  // Build lookup: { id: true/false }
  const correctness = {};
  // if (title === "Math" && evaluation?.math_results) {
  //   evaluation.math_results.forEach(r => {
  //     correctness[r.id] = r.is_correct;
  //   });
  // }

  // if (title === "English" && evaluation?.english_results) {
  //   evaluation.english_results.forEach(r => {
  //     correctness[r.id] = r.is_correct;
  //   });
  // }

  evaluation.forEach(r => {
    correctness[r.id] = r.is_correct;
  });

  return (
    <div className="question-section">
      <h2>{title}</h2>

      {questions.map((q) => {
        const key = `${title.toLowerCase()}-${q.id}`;
        const isCorrect = correctness[q.id];

        const icon = isCorrect === true
          ? <span style={{ color: "green", marginLeft: "8px" }}>✓</span>
          : isCorrect === false
            ? <span style={{ color: "red", marginLeft: "8px" }}>✗</span>
            : null; // no icon before evaluation

        return (
          <div className="question-row" key={key}>
            <div className="question-text">
              <span className="question-number">{q.id}.</span>
              {q.question}
              <span className="answer-icon">{icon}</span>
            </div>

            {title === "Math" ? (
            <input
              id={key}
              name={key}
              className={`answer-input ${
                isCorrect === false ? "answer-wrong" :
                isCorrect === true ? "answer-correct" : ""
              }`}
              value={answers[key] || ""}
              onChange={(e) => onAnswerChange(q.id, e.target.value)}
            />
            ) : (
            <textarea
              id={key}
              name={key}
              className={`answer-textarea ${
                isCorrect === false ? "answer-wrong" :
                isCorrect === true ? "answer-correct" : ""
              }`}
              value={answers[key] || ""}
              onChange={(e) => onAnswerChange(q.id, e.target.value)}
            />
          )}

          </div>
        );
      })}
    </div>
  );
}
