import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function History() {
  const [interviews, setInterviews] = useState<any[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const userName = localStorage.getItem("interviewai_user") || "Guest";
    api.getHistory(userName).then((d: any) => setInterviews(d.interviews));
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-semibold mb-1">Interview History</h1>
      <p className="text-slate-400 text-sm mb-6">Revisit past interviews and their reports.</p>

      {interviews.length === 0 ? (
        <div className="glass rounded-2xl p-10 text-center text-slate-400 text-sm">
          No interviews yet — start your first one from the dashboard.
        </div>
      ) : (
        <div className="space-y-2">
          {interviews.map((iv) => (
            <button
              key={iv.id}
              onClick={() => navigate(`/interview/report?id=${iv.id}`)}
              className="w-full glass rounded-xl px-5 py-4 flex items-center justify-between text-left hover:border-brand-500/60"
            >
              <div>
                <p className="text-sm font-medium">{iv.company} — {iv.role}</p>
                <p className="text-xs text-slate-500">{iv.domain} · {iv.interview_type}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-slate-300">{iv.score}/10</p>
                <p className="text-xs text-slate-500">{iv.status}</p>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
