import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import type { DashboardData } from "../types";

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="glass rounded-2xl p-5">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className="text-2xl font-semibold">{value}</p>
    </div>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const userName = localStorage.getItem("interviewai_user") || "Guest";
    api.getDashboard(userName).then(setData).catch(() => setData(null));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Your Dashboard</h1>
          <p className="text-slate-400 text-sm">Track your interview practice over time.</p>
        </div>
        <button onClick={() => navigate("/interview/setup")} className="bg-brand-600 hover:bg-brand-500 rounded-xl px-5 py-2.5 text-sm font-medium">
          🎤 New Interview
        </button>
      </div>

      {!data || data.interviews_completed === 0 ? (
        <div className="glass rounded-2xl p-10 text-center">
          <p className="text-slate-300 mb-2">No completed interviews yet.</p>
          <p className="text-slate-500 text-sm">Start your first voice mock interview to see your stats here.</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard label="Interviews Completed" value={data.interviews_completed} />
            <StatCard label="Average Performance" value={`${data.average_performance}/10`} />
            <StatCard label="Technical Score" value={`${data.technical_score}/10`} />
            <StatCard label="Communication Score" value={`${data.communication_score}/10`} />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="glass rounded-2xl p-5">
              <h3 className="text-sm font-medium text-emerald-400 mb-2">Strongest domains</h3>
              <ul className="text-sm text-slate-300 list-disc list-inside">
                {data.strongest_domains.map((d) => <li key={d}>{d}</li>)}
              </ul>
            </div>
            <div className="glass rounded-2xl p-5">
              <h3 className="text-sm font-medium text-amber-400 mb-2">Weakest domains</h3>
              <ul className="text-sm text-slate-300 list-disc list-inside">
                {data.weakest_domains.map((d) => <li key={d}>{d}</li>)}
              </ul>
            </div>
          </div>

          <div className="glass rounded-2xl p-5">
            <h3 className="text-sm font-medium mb-3">Recent interviews</h3>
            <div className="space-y-2">
              {data.recent_interviews.map((iv) => (
                <div key={iv.id} className="flex items-center justify-between text-sm border-b border-slate-800/60 pb-2 last:border-0">
                  <span>{iv.company} — {iv.role}</span>
                  <span className="text-slate-500">{iv.status} · {iv.score}/10</span>
                </div>
              ))}
            </div>
          </div>

          <div className="glass rounded-2xl p-5 flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Learning progress</p>
              <p className="text-xs text-slate-500">{data.learning_progress}% of your roadmap complete</p>
            </div>
            {data.recommended_next_practice && (
              <button onClick={() => navigate("/learning")} className="text-sm px-4 py-2 rounded-lg border border-brand-700 text-brand-300 hover:bg-brand-950/40">
                Practice {data.recommended_next_practice} →
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
