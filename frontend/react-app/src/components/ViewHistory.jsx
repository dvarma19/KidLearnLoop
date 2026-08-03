import React, { useEffect, useState } from "react";
import { getChildren, fetchChildHistory } from "../api";

export default function ViewHistory() {
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState("");
  const [history, setHistory] = useState([]);

  // Load child aliases
  useEffect(() => {
    getChildren()
      .then((data) => {
        setChildren(data.children || []);
        if (data.children?.length > 0) {
          setSelectedChild(data.children[0]);
        }
      })
      .catch((err) => console.error(err));
  }, []);

  // Load history when child changes
  useEffect(() => {
    if (!selectedChild) return;

    fetchChildHistory(selectedChild)
      .then((data) => {
        setHistory(data.history || []);
      })
      .catch((err) => console.error(err));
  }, [selectedChild]);

  return (
    <div className="view-history">
      <div className="header-row">
        <h2>View History</h2>

        <div className="child-selector">
          <label><span className="label-icon">👤</span> Child:</label>
          <select
            value={selectedChild}
            onChange={(e) => setSelectedChild(e.target.value)}
            style={{ minWidth: "160px" }}
          >
            {children.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      <table className="history-table">
        <thead>
          <tr>
            <th>Worksheet ID</th>
            <th>Difficulty</th>
            <th>Created At</th>
            <th>Score</th>
            <th>AI Feedback</th>
          </tr>
        </thead>

        <tbody>
          {history.map((h) => {
            const created = new Date(h.created_at).toLocaleString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric",
              hour: "2-digit",
              minute: "2-digit"
            });

            return (
              <tr key={h.worksheet_id}>
                <td>{h.worksheet_id}</td>
                <td>{h.difficulty}</td>

                {/* Friendly date format */}
                <td>{created}</td>

                {/* Score formatted nicely */}
                <td className="score-cell">
                  <div>Math: {h.math_score ?? 0}</div>
                  <div>English: {h.english_score ?? 0}</div>
                </td>

                {/* AI Feedback */}
                <td className="feedback-cell">
                  {h.ai_feedback || "No feedback"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
