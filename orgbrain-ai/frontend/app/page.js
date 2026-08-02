"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { getSession } from "../lib/api";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const { token } = getSession();
    router.replace(token ? "/dashboard" : "/login");
  }, []);
  return (
    <div className="min-h-screen flex items-center justify-center">
      <p className="text-gray-500">Loading OrgBrain AI...</p>
    </div>
  );
}
