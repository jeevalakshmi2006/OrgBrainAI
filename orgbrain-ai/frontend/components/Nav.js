"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { getSession, clearSession } from "../lib/api";

export default function Nav() {
  const router = useRouter();
  const pathname = usePathname();
  const { role, name } = typeof window !== "undefined" ? getSession() : { role: "", name: "" };

  const employeeLinks = [
    { href: "/dashboard", label: "Home" },
    { href: "/interview", label: "Interview Agent" },
    { href: "/twin-chat", label: "AI Twin" },
    { href: "/sop", label: "SOP" },
  ];
  const adminLinks = [{ href: "/dashboard", label: "Dashboard" }];

  const links = role === "admin" ? adminLinks : employeeLinks;

  function logout() {
    clearSession();
    router.push("/login");
  }

  return (
    <nav className="bg-navy text-white px-6 h-16 flex items-center justify-between shadow-md sticky top-0 z-20">
      <div className="flex items-center gap-8">
        <span className="font-bold text-lg tracking-wide flex items-center gap-2">
          <span className="w-8 h-8 rounded-md bg-steel flex items-center justify-center text-sm font-black">OB</span>
          OrgBrain AI
        </span>
        <div className="flex items-center gap-1">
          {links.map((l) => {
            const isActive = pathname === l.href;
            return (
              <Link
                key={l.href}
                href={l.href}
                className={`text-sm px-3 py-2 rounded-md transition-colors ${
                  isActive ? "bg-white/10 text-white font-semibold" : "text-gray-300 hover:text-white hover:bg-white/5"
                }`}
              >
                {l.label}
              </Link>
            );
          })}
        </div>
      </div>
      <div className="flex items-center gap-4 text-sm">
        <span className="text-gray-300">
          {name} <span className="text-steel font-medium capitalize">· {role}</span>
        </span>
        <button onClick={logout} className="border border-white/20 px-3 py-1.5 rounded-md hover:bg-white/10 transition-colors">
          Logout
        </button>
      </div>
    </nav>
  );
}
