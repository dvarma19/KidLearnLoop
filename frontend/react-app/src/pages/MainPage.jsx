import React, { useState } from "react";
import WorksheetForm from "../components/WorksheetForm";
import ViewHistory from "../components/ViewHistory";
import Dashboard from "../components/Dashboard";

export default function MainPage() {
  const [activeTab, setActiveTab] = useState("generate");

  const renderContent = () => {
    switch (activeTab) {
      case "generate":
        return <WorksheetForm />;
      case "history":
        return <ViewHistory />;
      case "dashboard":
        return <Dashboard />;
      default:
        return <WorksheetForm />;
    }
  };

  return (
    <div className="main-layout">
      {/* LEFT PANE */}
      <div className="left-pane">
        <div
          className={`tab ${activeTab === "generate" ? "active" : ""}`}
          onClick={() => setActiveTab("generate")}
        >
          <span className="nav-icon">✏️</span>
          <span>Generate Worksheet</span>
        </div>

        <div
          className={`tab ${activeTab === "history" ? "active" : ""}`}
          onClick={() => setActiveTab("history")}
        >
          <span className="nav-icon">🕘</span>
          <span>View History</span>
        </div>

        <div
          className={`tab ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
        >
          <span className="nav-icon">📊</span>
          <span>Dashboard</span>
        </div>
      </div>

      {/* RIGHT CONTENT */}
      <div className="content-pane">
        {renderContent()}
      </div>
    </div>
  );
}
