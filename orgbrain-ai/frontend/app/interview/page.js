"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "../../components/Nav";
import { api, getSession } from "../../lib/api";

export default function InterviewStart() {
  const router = useRouter();
  const [departments, setDepartments] = useState([]);
  const [candidateName, setCandidateName] = useState("");
  const [departmentId, setDepartmentId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session.token) return router.replace("/login");
    if (session.role !== "employee") return router.replace("/dashboard");
    setCandidateName(session.name || "");
    api.listDepartments().then(setDepartments).catch((e) => setError(e.message));
  }, []);

  async function handleStart(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const interview = await api.startInterview(candidateName, departmentId);
      router.push(`/interview/${interview.id}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Nav />
      <main className="max-w-xl mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-navy">Knowledge Capture Interview</h1>
          <p className="text-gray-500 text-sm mt-1">
            A short, guided conversation — 5 to 6 questions, type or speak your answers.
            At the end, your responses are turned into a structured SOP automatically.
          </p>
        </div>

        <form onSubmit={handleStart} className="card space-y-5">
          <div>
            <label className="text-sm font-medium text-gray-700">Your Name</label>
            <input
              className="input-field mt-1"
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              placeholder="e.g. Arun Kumar"
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Department</label>
            <select className="input-field mt-1" value={departmentId} onChange={(e) => setDepartmentId(e.target.value)} required>
              <option value="">Select your department...</option>
              {departments.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Starting..." : "Begin Interview"}
          </button>
        </form>
      </main>
    </div>
  );
}
