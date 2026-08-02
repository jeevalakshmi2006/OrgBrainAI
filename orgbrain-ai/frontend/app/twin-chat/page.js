"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Nav from "../../components/Nav";
import { api, getSession } from "../../lib/api";

export default function TwinChat() {
  const router = useRouter();
  const [departments, setDepartments] = useState([]);
  const [departmentId, setDepartmentId] = useState("");
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    const { token } = getSession();
    if (!token) return router.replace("/login");
    api.listDepartments().then((d) => {
      setDepartments(d);
      if (d.length) setDepartmentId(d[0].id);
    }).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  async function ask(e) {
    e.preventDefault();
    if (!question.trim() || !departmentId) return;
    const q = question;
    setChat((c) => [...c, { role: "user", text: q }]);
    setQuestion("");
    setLoading(true);
    setError("");
    try {
      const res = await api.twinChat(departmentId, q);
      setChat((c) => [...c, { role: "twin", text: res.answer, confidence: res.confidence, sources: res.sources }]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <Nav active="/twin-chat" />
      <main className="max-w-3xl mx-auto p-6">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-xl font-bold text-navy">Department AI Twin</h1>
          <select className="input-field w-56" value={departmentId} onChange={(e) => setDepartmentId(e.target.value)}>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </div>
        <p className="text-xs text-gray-400 mb-4">
          Powered by Retrieval-Augmented Generation (RAG): your question is matched against the
          department's approved SOPs stored in a vector database, and the AI answers using only
          that retrieved text — not general knowledge.
        </p>

        <div className="card h-[55vh] overflow-y-auto flex flex-col gap-3 mb-4">
          {chat.length === 0 && (
            <p className="text-gray-400 text-sm">
              Ask something like "How do we recover from deployment failures?" — answers are grounded
              in approved organizational knowledge, with sources shown below each response.
            </p>
          )}
          {chat.map((m, i) => (
            <div key={i} className={`max-w-[85%] px-4 py-2 rounded-lg text-sm ${
              m.role === "twin" ? "bg-navy text-white self-start" : "bg-gray-100 text-gray-800 self-end"
            }`}>
              <p>{m.text}</p>
              {m.role === "twin" && (
                <div className="mt-2 pt-2 border-t border-white/20 text-xs text-gray-300">
                  Confidence: {(m.confidence * 100).toFixed(0)}%
                  {m.sources?.length > 0 && (
                    <span> · Sources: {m.sources.map((s) => s.type).join(", ")}</span>
                  )}
                </div>
              )}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {error && <p className="text-red-600 text-sm mb-2">{error}</p>}

        <form onSubmit={ask} className="flex gap-2">
          <input
            className="input-field"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask the Twin a question..."
            disabled={loading}
          />
          <button type="submit" disabled={loading} className="btn-primary whitespace-nowrap">
            {loading ? "Thinking..." : "Ask"}
          </button>
        </form>
      </main>
    </div>
  );
}
