"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "../../components/Nav";
import { api, getSession, downloadSopPdf } from "../../lib/api";

export default function SopSearch() {
  const router = useRouter();
  const [departments, setDepartments] = useState([]);
  const [departmentId, setDepartmentId] = useState("");
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [error, setError] = useState("");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    const session = getSession();
    if (!session.token) return router.replace("/login");
    api.listDepartments().then(setDepartments).catch((e) => setError(e.message));
    search();
  }, []);

  async function search() {
    try {
      const res = await api.searchSops(departmentId || undefined, q || undefined);
      setResults(res);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDownload() {
    if (!selected) return;
    setDownloading(true);
    try {
      await downloadSopPdf(selected.id, selected.title);
    } catch (e) {
      setError(e.message);
    } finally {
      setDownloading(false);
    }
  }

  return (
    <div>
      <Nav />
      <main className="max-w-5xl mx-auto p-6">
        <h1 className="text-xl font-bold text-navy mb-1">SOP Library</h1>
        <p className="text-sm text-gray-500 mb-6">
          Structured, step-by-step procedures generated from real employee interviews.
        </p>

        <div className="flex gap-2 mb-6">
          <input className="input-field" placeholder="Search SOP titles..." value={q} onChange={(e) => setQ(e.target.value)} />
          <select className="input-field w-56" value={departmentId} onChange={(e) => setDepartmentId(e.target.value)}>
            <option value="">All departments</option>
            {departments.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
          <button onClick={search} className="btn-primary whitespace-nowrap">Search</button>
        </div>

        {error && <p className="text-red-600 text-sm mb-2">{error}</p>}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-3">
            {results.length === 0 && <p className="text-gray-400 text-sm">No SOPs found yet — completed interviews publish here automatically.</p>}
            {results.map((s) => (
              <button
                key={s.id}
                onClick={() => setSelected(s)}
                className={`card w-full text-left hover:shadow-md transition-shadow ${selected?.id === s.id ? "ring-2 ring-steel" : ""}`}
              >
                <h3 className="font-semibold text-navy">{s.title}</h3>
                <p className="text-sm text-gray-500 line-clamp-2">{s.purpose}</p>
              </button>
            ))}
          </div>

          {selected && (
            <div className="card">
              <div className="flex items-start justify-between mb-3">
                <h2 className="font-bold text-navy text-lg">{selected.title}</h2>
                <button onClick={handleDownload} disabled={downloading} className="text-steel text-sm font-medium hover:underline whitespace-nowrap disabled:opacity-50">
                  {downloading ? "Downloading..." : "⬇ Download PDF"}
                </button>
              </div>
              {[
                ["Purpose", selected.purpose],
                ["Prerequisites", selected.prerequisites],
                ["Procedure", selected.procedure],
                ["Validation", selected.validation],
                ["Escalation", selected.escalation],
                ["Risk Mitigation", selected.risk_mitigation],
              ].map(([label, value]) => (
                <div key={label} className="mb-3">
                  <p className="text-xs font-semibold text-steel uppercase tracking-wide">{label}</p>
                  <p className="text-sm text-gray-700 whitespace-pre-line">{value || "—"}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
