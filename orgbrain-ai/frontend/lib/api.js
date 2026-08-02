// Central API client. Reads the backend URL from an env var so switching
// between local dev and a deployed backend (e.g. Render) is one line.
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function getApiBase() {
  return API_BASE;
}

function getToken() {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("orgbrain_token");
}

export function setToken(token) {
  localStorage.setItem("orgbrain_token", token);
}

export function clearSession() {
  localStorage.removeItem("orgbrain_token");
  localStorage.removeItem("orgbrain_role");
  localStorage.removeItem("orgbrain_name");
}

export function getSession() {
  if (typeof window === "undefined") return { token: null, role: null, name: null };
  return {
    token: localStorage.getItem("orgbrain_token"),
    role: localStorage.getItem("orgbrain_role"),
    name: localStorage.getItem("orgbrain_name"),
  };
}

async function request(path, { method = "GET", body, auth = true } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (auth) {
    const token = getToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;
  }
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const errJson = await res.json();
      detail = errJson.detail || detail;
    } catch (_) {}
    throw new Error(detail);
  }
  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/json")) return res.json();
  return null;
}

export const api = {
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password }, auth: false }),
  me: () => request("/auth/me"),
  registerUser: (payload) => request("/auth/register", { method: "POST", body: payload }),

  listDepartments: () => request("/admin/departments"),
  createDepartment: (payload) => request("/admin/departments", { method: "POST", body: payload }),
  listUsers: () => request("/admin/users"),
  deactivateUser: (id) => request(`/admin/users/${id}/deactivate`, { method: "PATCH" }),
  listInterviewsAdmin: () => request("/admin/interviews"),
  knowledgeGraph: () => request("/admin/knowledge-graph"),

  startInterview: (candidate_name, department_id) =>
    request("/interview/start", { method: "POST", body: { candidate_name, department_id } }),
  getInterview: (id) => request(`/interview/${id}`),
  getMessages: (id) => request(`/interview/${id}/messages`),
  submitAnswer: (id, answer) => request(`/interview/${id}/answer`, { method: "POST", body: { answer } }),

  twinChat: (department_id, question) =>
    request("/twin/chat", { method: "POST", body: { department_id, question } }),
  findExperts: (skill) => request(`/twin/experts?skill=${encodeURIComponent(skill)}`),

  searchSops: (department_id, q) => {
    const params = new URLSearchParams();
    if (department_id) params.set("department_id", department_id);
    if (q) params.set("q", q);
    return request(`/sop/search?${params.toString()}`);
  },
  sopPdfUrl: (sopId) => `${API_BASE}/sop/${sopId}/pdf`,

  analyticsOverview: () => request("/analytics/overview"),
  analyticsDepartment: (id) => request(`/analytics/department/${id}`),
};

// Downloads a protected PDF (needs the Authorization header, so it can't be a plain <a href>).
export async function downloadSopPdf(sopId, filename) {
  const token = getToken();
  const res = await fetch(`${API_BASE}/sop/${sopId}/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Could not download SOP PDF");
  const blob = await res.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${filename || "SOP"}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}
