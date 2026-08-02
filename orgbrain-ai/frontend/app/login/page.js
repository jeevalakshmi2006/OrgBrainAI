"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, setToken } from "../../lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("admin@orgbrain.ai");
  const [password, setPassword] = useState("Admin@123");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await api.login(email, password);
      setToken(data.access_token);
      localStorage.setItem("orgbrain_role", data.role);
      localStorage.setItem("orgbrain_name", data.name);
      router.push("/dashboard");
    } catch (err) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-navy to-steel">
      <div className="card w-full max-w-sm">
        <h1 className="text-2xl font-bold text-navy mb-1">OrgBrain AI</h1>
        <p className="text-sm text-gray-500 mb-6">Organizational Knowledge Platform</p>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Email</label>
            <input className="input-field mt-1" value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700">Password</label>
            <input className="input-field mt-1" value={password} onChange={(e) => setPassword(e.target.value)} type="password" required />
          </div>
          {error && <p className="text-red-600 text-sm">{error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>
        <p className="text-xs text-gray-400 mt-6">
          Demo accounts (created by seed.py): admin@orgbrain.ai / Admin@123 (Admin),
          arun@orgbrain.ai / Arun@123 (Employee)
        </p>
      </div>
    </div>
  );
}
