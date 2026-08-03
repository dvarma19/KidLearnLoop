// frontend/react-app/src/api.js
const API_BASE = "http://localhost:8000";

export async function createWorksheet({ alias, grade, difficulty }) {
  const params = new URLSearchParams({
    child_alias: alias,
    grade: grade,
    difficulty,
  });

  const res = await fetch(`${API_BASE}/worksheet/create?${params.toString()}`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error(`Failed to create worksheet: ${res.status}`);
  }

  return res.json();
}


export async function submitWorksheet(payload) {
  const res = await fetch(`${API_BASE}/worksheet/submit_worksheet`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    throw new Error(`Failed to submit worksheet: ${res.status}`);
  }

  return res.json();
}


// Fetch all child aliases
export async function getChildren() {
  const res = await fetch(`${API_BASE}/dbstats/getChildren`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch children: ${res.status}`);
  }

  return res.json();
}

// Fetch worksheet history for a specific child
export async function fetchChildHistory(child_alias) {
  const res = await fetch(`${API_BASE}/dbstats/fetchChildHistory`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ child_alias })
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch child history: ${res.status}`);
  }

  return res.json();
}


export async function fetchDashboard(child_alias) {
  const res = await fetch(`${API_BASE}/dashboard`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ child_alias })
  });

  if (!res.ok) {
    throw new Error(`Failed to fetch dashboard: ${res.status}`);
  }

  return res.json();
}
