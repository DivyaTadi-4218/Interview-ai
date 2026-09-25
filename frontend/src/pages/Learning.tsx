import { useEffect, useState } from "react";
import api from "../api/client";
import type { RoadmapDay } from "../types";

export default function Learning() {
  const [role, setRole] = useState("");
  const [domain, setDomain] = useState("");
  const [experience, setExperience] = useState("");
  const [roles, setRoles] = useState<string[]>([]);
  const [domains, setDomains] = useState<string[]>([]);
  const [experienceLevels, setExperienceLevels] = useState<string[]>([]);
  const [roadmap, setRoadmap] = useState<RoadmapDay[] | null>(null);
  const [openDay, setOpenDay] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getDomains().then((d: any) => {
      setRoles(d.roles);
      setDomains(d.domains);
      setExperienceLevels(d.experience_levels);
    });
  }, []);

  const generate = async () => {
    if (!role || !domain || !experience) return;
    setLoading(true);
    try {
      const userName = localStorage.getItem("interviewai_user") || "Guest";
      const res: any = await api.generateRoadmap({ role, domain, experience_level: experience }, userName);
      setRoadmap(res.days);
      setOpenDay(res.days[0]?.day ?? null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Prepare Before Interview</h1>
        <p className="text-slate-400 text-sm">Get a personalized day-by-day roadmap before you go live.</p>
      </div>

      <div className="glass rounded-2xl p-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
        <select value={role} onChange={(e) => setRole(e.target.value)} className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm">
          <option value="">Role…</option>
          {roles.map((r) => <option key={r} value={r}>{r}</option>)}
        </select>
        <select value={domain} onChange={(e) => setDomain(e.target.value)} className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm">
          <option value="">Domain…</option>
          {domains.map((d) => <option key={d} value={d}>{d}</option>)}
        </select>
        <select value={experience} onChange={(e) => setExperience(e.target.value)} className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm">
          <option value="">Experience…</option>
          {experienceLevels.map((e) => <option key={e} value={e}>{e}</option>)}
        </select>
        <button
          onClick={generate}
          disabled={!role || !domain || !experience || loading}
          className="sm:col-span-3 bg-brand-600 hover:bg-brand-500 disabled:opacity-40 rounded-xl py-3 text-sm font-medium"
        >
          {loading ? "Building your roadmap…" : "Generate Roadmap"}
        </button>
      </div>

      {roadmap && (
        <div className="space-y-3">
          {roadmap.map((d) => (
            <div key={d.day} className="glass rounded-2xl overflow-hidden">
              <button
                onClick={() => setOpenDay(openDay === d.day ? null : d.day)}
                className="w-full flex items-center justify-between px-5 py-4 text-left"
              >
                <span className="text-sm font-medium">Day {d.day}: {d.topic}</span>
                <span className="text-slate-500 text-xs">{openDay === d.day ? "▲" : "▼"}</span>
              </button>
              {openDay === d.day && (
                <div className="px-5 pb-5 text-sm text-slate-300 space-y-3">
                  <p>{d.explanation}</p>
                  <div>
                    <p className="text-xs uppercase text-slate-500 mb-1">Key concepts</p>
                    <ul className="list-disc list-inside space-y-0.5">
                      {d.key_concepts.map((c, i) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                  <div>
                    <p className="text-xs uppercase text-slate-500 mb-1">Practice questions</p>
                    <ul className="list-disc list-inside space-y-0.5">
                      {d.interview_questions.map((q, i) => <li key={i}>{q}</li>)}
                    </ul>
                  </div>
                  {d.quiz?.length > 0 && (
                    <div>
                      <p className="text-xs uppercase text-slate-500 mb-1">Mini quiz</p>
                      {d.quiz.map((q, i) => (
                        <p key={i} className="text-slate-400">Q: {q.q} — <span className="text-slate-300">{q.a}</span></p>
                      ))}
                    </div>
                  )}
                  {d.coding_practice && (
                    <p className="text-xs text-brand-300">Includes hands-on coding practice</p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
