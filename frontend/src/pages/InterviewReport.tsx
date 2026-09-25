import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import api from "../api/client";
import type { InterviewReport as ReportType } from "../types";

export default function InterviewReport() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const id = params.get("id");
  const [report, setReport] = useState<ReportType | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    api.getReport(Number(id)).then(setReport).catch((e) => setError(e.message));
  }, [id]);

  if (error) {
    return <div className="max-w-2xl mx-auto px-6 py-16 text-center text-rose-400">{error}</div>;
  }
  if (!report) {
    return <div className="max-w-2xl mx-auto px-6 py-16 text-center text-slate-400">Building your report…</div>;
  }

  const scoreData = [
    { name: "Overall", score: report.overall_score },
    { name: "Technical", score: report.technical_score },
    { name: "Communication", score: report.communication_score },
  ];

  return (
    <div className="max-w-3xl mx-auto px-6 py-10 space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">Interview Report</h1>
        <p className="text-slate-400 text-sm">A detailed breakdown of your performance and what to study next.</p>
      </div>

      <div className="glass rounded-2xl p-6">
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={scoreData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} />
            <YAxis domain={[0, 10]} stroke="#94a3b8" fontSize={12} />
            <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
            <Bar dataKey="score" fill="#6366f1" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="glass rounded-2xl p-5">
          <h3 className="text-sm font-medium text-emerald-400 mb-2">Strengths</h3>
          <ul className="text-sm text-slate-300 space-y-1 list-disc list-inside">
            {report.strengths.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
        <div className="glass rounded-2xl p-5">
          <h3 className="text-sm font-medium text-amber-400 mb-2">Weak areas</h3>
          <ul className="text-sm text-slate-300 space-y-1 list-disc list-inside">
            {report.weak_areas.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </div>
      </div>

      <div className="glass rounded-2xl p-5">
        <h3 className="text-sm font-medium mb-3">Questions that need improvement</h3>
        <div className="space-y-4">
          {report.questions_needing_improvement.map((q, i) => (
            <div key={i} className="border-l-2 border-amber-500/50 pl-4">
              <p className="text-sm font-medium">{q.question}</p>
              <p className="text-xs text-slate-400 mt-1">Score: {q.score}/10 — {q.feedback}</p>
              {q.suggested_answer && (
                <p className="text-xs text-emerald-300 mt-1">Model answer: {q.suggested_answer}</p>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="glass rounded-2xl p-5">
        <h3 className="text-sm font-medium mb-3">Personalized learning roadmap</h3>
        <div className="space-y-3">
          {report.roadmap.map((d) => (
            <div key={d.day} className="flex gap-3">
              <div className="h-7 w-7 shrink-0 rounded-full bg-brand-600/30 text-brand-300 text-xs flex items-center justify-center">
                {d.day}
              </div>
              <div>
                <p className="text-sm font-medium">{d.topic}</p>
                <p className="text-xs text-slate-400">{d.explanation}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="glass rounded-2xl p-5">
        <h3 className="text-sm font-medium mb-2">Recommended practice questions</h3>
        <ul className="text-sm text-slate-300 space-y-1 list-disc list-inside">
          {report.recommended_practice_questions.map((q, i) => <li key={i}>{q}</li>)}
        </ul>
      </div>

      <div className="flex gap-3">
        <button onClick={() => navigate("/interview/setup")} className="flex-1 bg-brand-600 hover:bg-brand-500 rounded-xl py-3 text-sm font-medium">
          Start another interview
        </button>
        <button onClick={() => navigate("/dashboard")} className="flex-1 border border-slate-700 hover:bg-slate-800 rounded-xl py-3 text-sm font-medium">
          Go to dashboard
        </button>
      </div>
    </div>
  );
}
