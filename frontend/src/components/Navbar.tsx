import { NavLink } from "react-router-dom";

const links = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/companies", label: "Companies" },
  { to: "/interview/setup", label: "New Interview" },
  { to: "/learning", label: "Learning" },
  { to: "/resume", label: "Resume" },
  { to: "/history", label: "History" },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-30 glass border-b border-slate-800/60">
      <div className="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2 font-semibold text-lg">
          <span className="text-brand-400">◆</span>
          <span>InterviewAI</span>
        </div>
        <nav className="hidden md:flex gap-1">
          {links.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-lg text-sm transition-colors ${
                  isActive ? "bg-brand-600/20 text-brand-300" : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
                }`
              }
            >
              {l.label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
