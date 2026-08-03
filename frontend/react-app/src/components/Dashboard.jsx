import React, { useEffect, useState } from "react";
import { getChildren, fetchDashboard } from "../api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";


export default function Dashboard() {
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState("");
  const [history, setHistory] = useState([]);

  // Calendar state
  const today = new Date();
  const [month, setMonth] = useState(today.getMonth());
  const [year, setYear] = useState(today.getFullYear());
  const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];


  // Load children
  useEffect(() => {
    getChildren().then((data) => {
      setChildren(data.children || []);
      if (data.children?.length > 0) {
        setSelectedChild(data.children[0]);
      }
    });
  }, []);

  // Load dashboard data
  useEffect(() => {
    if (!selectedChild) return;

    fetchDashboard(selectedChild).then((data) => {
      setHistory(data.history || []);
    });
  }, [selectedChild]);

  // Calendar helpers
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const firstDay = new Date(year, month, 1).getDay();

  const worksheetDates = history.map((h) => h.created_at.split(" ")[0]);

  const goPrevMonth = () => {
    if (month === 0) {
      setMonth(11);
      setYear(year - 1);
    } else {
      setMonth(month - 1);
    }
  };

  const goNextMonth = () => {
    if (month === 11) {
      setMonth(0);
      setYear(year + 1);
    } else {
      setMonth(month + 1);
    }
  };

  // ============================
  // SCORE SUMMARY CALCULATIONS
  // ============================

  const latest = history.length > 0 ? history[history.length - 1] : null;

  const avgMath =
    history.length > 0
      ? (history.reduce((sum, h) => sum + (h.math_score || 0), 0) / history.length).toFixed(1)
      : 0;

  const avgEnglish =
    history.length > 0
      ? (history.reduce((sum, h) => sum + (h.english_score || 0), 0) / history.length).toFixed(1)
      : 0;

  const lastThree = history.slice(-3);
  const difficultyTrend = lastThree.map((h) => h.difficulty).join(" → ");

  // ============================
  // CHART DATA (for Recharts)
  // ============================

  const chartData = history.map((h) => {
    const dateOnly = h.created_at.split(" ")[0];
    return {
      date: dateOnly,
      math: h.math_score,
      english: h.english_score,
    };
  });

  return (
  <div className="dashboard-container">

    {/* Header */}
    <div className="dashboard-header">
      <h2>Dashboard</h2>

      <div className="child-selector">
        <label><span className="label-icon">👤</span> Child:</label>
        <select
          value={selectedChild}
          onChange={(e) => setSelectedChild(e.target.value)}
        >
          {children.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>
    </div>

    {/* Score Cards */}
    <div className="score-grid">
      <div className="score-card pastel-blue">
        <div className="score-title"><span className="score-icon">🧮</span> Latest Math</div>
        <div className="score-value">{latest ? latest.math_score : "-"}</div>
      </div>

      <div className="score-card pastel-orange">
        <div className="score-title"><span className="score-icon">📘</span> Latest English</div>
        <div className="score-value">{latest ? latest.english_score : "-"}</div>
      </div>

      <div className="score-card pastel-green">
        <div className="score-title"><span className="score-icon">📈</span> Avg Math</div>
        <div className="score-value">{avgMath}</div>
      </div>

      <div className="score-card pastel-purple">
        <div className="score-title"><span className="score-icon">📚</span> Avg English</div>
        <div className="score-value">{avgEnglish}</div>
      </div>

      <div className="score-card pastel-gold trophy-card">
        <div className="score-title"><span className="score-icon">🏅</span> Difficulty Trend</div>
        <div className="score-value">{difficultyTrend || "-"}</div>
        <div className="trophy-icon">🏆</div>
      </div>
    </div>

    {/* Main Grid */}
    <div className="dashboard-main-grid">

      {/* Calendar */}
      <div className="calendar-wrapper">
        <div className="calendar-header">
          <button onClick={goPrevMonth}>◀</button>
          <h3>{year} {monthNames[month]}</h3>
          <button onClick={goNextMonth}>▶</button>
        </div>

        <div className="calendar-grid">
          {[...Array(firstDay)].map((_, i) => (
            <div key={`empty-${i}`} className="calendar-cell empty"></div>
          ))}

          {[...Array(daysInMonth)].map((_, i) => {
            const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(i + 1).padStart(2, "0")}`;
            const attempted = worksheetDates.includes(dateStr);

            return (
              <div key={i} className={`calendar-cell ${attempted ? "attempted" : ""}`}>
                {i + 1}
              </div>
            );
          })}
        </div>
      </div>

      {/* Chart */}
      <div className="chart-wrapper">
        <h3>Progress Over Time</h3>
        <div className="chart-placeholder">
          <ResponsiveContainer width="100%" height={280}>
              <LineChart
                data={chartData}
                margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#5b6c8c" />

                <XAxis
                  dataKey="date"
                  stroke="#dbe7ff"
                  tick={{ fontSize: 12, fill: "#dbe7ff" }}
                  tickLine={{ stroke: "#7c8fb4" }}
                  axisLine={{ stroke: "#7c8fb4" }}
                />

                <YAxis
                  stroke="#dbe7ff"
                  tick={{ fontSize: 12, fill: "#dbe7ff" }}
                  tickLine={{ stroke: "#7c8fb4" }}
                  axisLine={{ stroke: "#7c8fb4" }}
                  domain={[0, "dataMax + 1"]}
                />

                <Tooltip
                  contentStyle={{
                    background: "#0f172a",
                    borderRadius: "10px",
                    border: "1px solid #7c8fb4",
                    fontSize: "12px",
                    color: "#eff5ff"
                  }}
                  labelStyle={{ color: "#eff5ff" }}
                  itemStyle={{ color: "#eff5ff" }}
                />

                <Legend
                  wrapperStyle={{
                    paddingTop: "10px",
                    fontSize: "14px",
                    color: "#eff5ff"
                  }}
                  formatter={(value) => <span style={{ color: "#eff5ff" }}>{value}</span>}
                />

                <Line
                  type="monotone"
                  dataKey="math"
                  stroke="#7aa7ff"
                  strokeWidth={3}
                  dot={{ r: 5, fill: "#7aa7ff" }}
                  activeDot={{ r: 7 }}
                  name="Math Score"
                />

                <Line
                  type="monotone"
                  dataKey="english"
                  stroke="#f7a8a1"
                  strokeWidth={3}
                  dot={{ r: 5, fill: "#f7a8a1" }}
                  activeDot={{ r: 7 }}
                  name="English Score"
                />
              </LineChart>
          </ResponsiveContainer>

        </div>
      </div>

    </div>

    {/* Achievements */}
    {/* <div className="achievements-section">
      <h3>Achievements</h3>
      <div className="trophy-placeholder">
        Trophy icons / badges go here
      </div>
    </div> */}

  </div>
);

}
