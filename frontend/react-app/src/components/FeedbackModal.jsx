// frontend/react-app/src/components/FeedbackModal.jsx
import React from "react";

export default function FeedbackModal({ open, onClose, onSubmit }) {
  if (!open) return null;

  const [feedback, setFeedback] = React.useState("");

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Parent Feedback</h2>
        <textarea
          className="modal-textarea"
          placeholder="Optional feedback..."
          value={feedback}
          onChange={(e) => setFeedback(e.target.value)}
        />

        <div className="modal-actions">
          <button onClick={() => onSubmit(feedback)}>Submit</button>
          <button onClick={onClose}>Cancel</button>
        </div>
      </div>
    </div>
  );
}
