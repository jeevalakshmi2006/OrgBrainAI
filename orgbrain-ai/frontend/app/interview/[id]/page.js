"use client";
import { useEffect, useState, useRef, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Nav from "../../../components/Nav";
import SpeechTextInput from "../../../components/SpeechTextInput";
import { api, getSession } from "../../../lib/api";

export default function InterviewSession() {
  const { id } = useParams();
  const router = useRouter();
  const [messages, setMessages] = useState([]);
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("in_progress");
  const [completeness, setCompleteness] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [sop, setSop] = useState(null);
  const bottomRef = useRef(null);

  const refresh = useCallback(async () => {
    const [msgs, interview] = await Promise.all([api.getMessages(id), api.getInterview(id)]);
    setMessages(msgs);
    setStatus(interview.status);
    setCompleteness(interview.completeness_score);
  }, [id]);

  useEffect(() => {
    const session = getSession();
    if (!session.token) return router.replace("/login");
    if (session.role !== "employee") return router.replace("/dashboard");
    refresh().catch((e) => setError(e.message));
  }, [id, refresh]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function submitAnswer(e) {
    e.preventDefault();
    if (!answer.trim()) return;
    setLoading(true);
    setError("");
    try {
      const result = await api.submitAnswer(id, answer);
      setAnswer("");
      if (result.finished) {
        await refresh();
        setSop(result.sop);
      } else {
        await refresh();
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const questionsAsked = messages.filter((m) => m.role === "ai").length;

  return (
    <div>
      <Nav />
      <main className="max-w-3xl mx-auto p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-xl font-bold text-navy">Interview in Progress</h1>
            <p className="text-xs text-gray-400">Question {Math.max(questionsAsked, 1)} · at least 6 questions</p>
          </div>
          <span className="text-sm px-3 py-1 rounded-full bg-steel/10 text-steel font-medium">
            Knowledge Completeness: {completeness.toFixed(0)}%
          </span>
        </div>

        <div className="card h-[52vh] overflow-y-auto flex flex-col gap-3 mb-4">
          {messages.map((m, i) => (
            <div key={i} className={`max-w-[80%] px-4 py-3 rounded-lg text-sm leading-relaxed ${
              m.role === "ai" ? "bg-navy text-white self-start" : "bg-gray-100 text-gray-800 self-end"
            }`}>
              {m.content}
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {error && <p className="text-red-600 text-sm mb-2">{error}</p>}

        {status === "in_progress" && (
          <SpeechTextInput
            value={answer}
            onChange={setAnswer}
            onSubmit={submitAnswer}
            disabled={loading}
            placeholder="Type your answer, or tap the mic to speak..."
          />
        )}

        {status === "completed" && (
          <div className="card bg-green-50 border-green-200 text-center">
            <p className="text-green-800 font-medium mb-1">✅ Interview complete — thank you!</p>
            <p className="text-sm text-green-700 mb-4">
              Your knowledge has been captured and turned into a structured SOP for your department.
            </p>
            <a href="/sop" className="btn-primary inline-block">View it in the SOP Library</a>
          </div>
        )}

        {sop && (
          <div className="card mt-4">
            <h3 className="font-semibold text-navy mb-2">📋 Generated SOP: {sop.title}</h3>
            <p className="text-sm text-gray-600 mb-1"><strong>Purpose:</strong> {sop.purpose}</p>
            <p className="text-sm text-gray-600 whitespace-pre-line"><strong>Procedure:</strong> {sop.procedure}</p>
          </div>
        )}
      </main>
    </div>
  );
}
