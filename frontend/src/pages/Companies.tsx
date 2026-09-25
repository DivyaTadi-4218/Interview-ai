import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function Companies() {
  const [companies, setCompanies] = useState<string[]>([]);
  const [query, setQuery] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    api.getCompanies().then((d: any) => setCompanies(d.companies));
  }, []);

  const filtered = companies.filter((c) => c.toLowerCase().includes(query.toLowerCase()));

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-semibold mb-1">Company-Focused Practice</h1>
      <p className="text-slate-400 text-sm mb-6">
        Practice in the realistic style of these companies' interviews — not their real confidential questions.
      </p>

      <input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search companies…"
        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2.5 text-sm mb-6 focus:outline-none focus:ring-2 focus:ring-brand-500"
      />

      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
        {filtered.map((c) => (
          <button
            key={c}
            onClick={() => {
              sessionStorage.setItem("interviewai_preselect_company", c);
              navigate("/interview/setup");
            }}
            className="glass rounded-xl px-4 py-3 text-sm text-left hover:border-brand-500/60 hover:text-brand-200 transition-colors"
          >
            {c}
          </button>
        ))}
      </div>
    </div>
  );
}
