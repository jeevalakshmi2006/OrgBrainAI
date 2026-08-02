"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "../../components/Nav";
import { api, getSession, downloadSopPdf } from "../../lib/api";
import AdminDashboard from "./AdminDashboard";
import EmployeeIntro from "./EmployeeIntro";

export default function Dashboard() {
  const router = useRouter();
  const [role, setRole] = useState(null);
  const [name, setName] = useState("");

  useEffect(() => {
    const session = getSession();
    if (!session.token) {
      router.replace("/login");
      return;
    }
    setRole(session.role);
    setName(session.name);
  }, []);

  if (!role) return null;

  return (
    <div>
      <Nav />
      {role === "admin" ? <AdminDashboard /> : <EmployeeIntro name={name} />}
    </div>
  );
}
