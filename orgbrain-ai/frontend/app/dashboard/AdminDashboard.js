"use client";
import { useEffect, useState } from "react";
import { api, downloadSopPdf } from "../../lib/api";
import KnowledgeGraph from "../../components/KnowledgeGraph";

export default function AdminDashboard() {
  const [overview, setOverview] = useState(null);
  const [interviews, setInterviews] = useState([]);
  const [graph, setGraph] = useState(null);
  const [error, setError] = useState("");
  const [downloadingId, setDownloadingId] = useState(null);
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [showUserForm, setShowUserForm] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", password: "", department_id: "" });
  const [message, setMessage] = useState("");

  function loadAll() {
    Promise.all([api.analyticsOverview(), api.listInterviewsAdmin(), api.knowledgeGraph(), api.listUsers(), api.listDepartments()])
      .then(([ov, iv, gr, us, dp]) => {
        setOverview(ov);
        setInterviews(iv);
        setGraph(gr);
        setUsers(us);
        setDepartments(dp);
      })
      .catch((e) => setError(e.message));
  }

  useEffect(() => { loadAll(); }, []);

  async function createEmployee(e) {
    e.preventDefault();
    setError(""); setMessage("");
    try {
      await api.registerUser({ ...form, role: "employee", department_id: form.department_id || null });
      setMessage(`Employee account created for ${form.email}.`);
      setForm({ name: "", email: "", password: "", department_id: "" });
      loadAll();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDownload(sopId, title) {
    setDownloadingId(sopId);
    try {
      await downloadSopPdf(sopId, title);
    } catch (e) {
      setError(e.message);
    } finally {
      setDownloadingId(null);
    }
  }

  const cards = overview
    ? [
        { label: "Total Interviews", value: overview.total_interviews, icon: "🎙️" },
        { label: "Completed Interviews", value: overview.completed_interviews, icon: "✅" },
        { label: "Avg. Knowledge Completeness", value: `${overview.avg_completeness_score}%`, icon: "📊" },
        { label: "SOPs Published", value: overview.total_sops_published, icon: "📋" },
        { label: "AI Twin Queries", value: overview.total_twin_queries, icon: "💬" },
        { label: "Departments", value: overview.departments_covered, icon: "🏢" },
      ]
    : [];

  return (
    <main className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-navy">Administrator Dashboard</h1>
        <p className="text-gray-500 text-sm">
          Organization-wide overview of knowledge captured, interviews conducted, and how
          departments relate to one another.
        </p>
      </div>

      {error && <p className="text-red-600 text-sm mb-4">{error}</p>}

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        {cards.map((c) => (
          <div key={c.label} className="card">
            <p className="text-xl mb-1">{c.icon}</p>
            <p className="text-2xl font-bold text-navy">{c.value}</p>
            <p className="text-xs text-gray-500 mt-1">{c.label}</p>
          </div>
        ))}
      </div>

      <section className="mb-8">
        <h2 className="font-semibold text-navy mb-1">Organizational Knowledge Graph</h2>
        <p className="text-sm text-gray-500 mb-3">
          Each node is a department, sized by how many SOPs have been captured from it.
          Connections show departments that share overlapping skills or knowledge areas.
        </p>
        <div className="card">
          {graph ? <KnowledgeGraph nodes={graph.nodes} edges={graph.edges} /> : <p className="text-gray-400 text-sm">Loading graph...</p>}
        </div>
      </section>

      <section>
        <h2 className="font-semibold text-navy mb-3">Interviews Conducted</h2>
        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2 pr-4">Employee</th>
                <th className="pr-4">Department</th>
                <th className="pr-4">Status</th>
                <th className="pr-4">Completeness</th>
                <th className="pr-4">Date</th>
                <th>SOP</th>
              </tr>
            </thead>
            <tbody>
              {interviews.length === 0 && (
                <tr><td colSpan={6} className="py-6 text-gray-400 text-center">No interviews yet.</td></tr>
              )}
              {interviews.map((iv) => (
                <tr key={iv.id} className="border-b last:border-0">
                  <td className="py-3 pr-4 font-medium text-gray-800">{iv.candidate_name}</td>
                  <td className="pr-4 text-gray-600">{iv.department_name}</td>
                  <td className="pr-4">
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      iv.status === "completed" ? "bg-green-100 text-green-700" : "bg-amber-100 text-amber-700"
                    }`}>
                      {iv.status}
                    </span>
                  </td>
                  <td className="pr-4 text-gray-600">{iv.completeness_score.toFixed(0)}%</td>
                  <td className="pr-4 text-gray-500 text-xs">{new Date(iv.created_at).toLocaleDateString()}</td>
                  <td>
                    {iv.sop_id ? (
                      <button
                        onClick={() => handleDownload(iv.sop_id, `${iv.candidate_name}_SOP`)}
                        disabled={downloadingId === iv.sop_id}
                        className="text-steel text-xs font-medium hover:underline disabled:opacity-50"
                      >
                        {downloadingId === iv.sop_id ? "Downloading..." : "⬇ Download PDF"}
                      </button>
                    ) : (
                      <span className="text-xs text-gray-400">Not yet generated</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="mt-8">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-semibold text-navy">Employee Accounts</h2>
          <button onClick={() => setShowUserForm((s) => !s)} className="text-steel text-sm font-medium hover:underline">
            {showUserForm ? "Close" : "+ Add Employee"}
          </button>
        </div>

        {message && <p className="text-green-600 text-sm mb-3">{message}</p>}

        {showUserForm && (
          <form onSubmit={createEmployee} className="card grid grid-cols-1 md:grid-cols-4 gap-3 items-end mb-4">
            <input className="input-field" placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
            <input className="input-field" placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
            <input className="input-field" placeholder="Temporary password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
            <select className="input-field" value={form.department_id} onChange={(e) => setForm({ ...form, department_id: e.target.value })} required>
              <option value="">Department...</option>
              {departments.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
            <button type="submit" className="btn-primary md:col-span-4">Create Employee Account</button>
          </form>
        )}

        <div className="card overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500 border-b">
                <th className="py-2 pr-4">Name</th><th className="pr-4">Email</th><th>Status</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id} className="border-b last:border-0">
                  <td className="py-2 pr-4">{u.name}</td>
                  <td className="pr-4 text-gray-600">{u.email}</td>
                  <td className="text-gray-600">{u.is_active ? "Active" : "Deactivated"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
