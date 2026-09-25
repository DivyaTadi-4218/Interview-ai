import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";

export default function InterviewSetup() {
  const navigate = useNavigate();
  const [companies, setCompanies] = useState<string[]>([]);
  const [domains, setDomains] = useState<string[]>([]);
  const [roles, setRoles] = useState<string[]>([]);
  const [experienceLevels, setExperienceLevels] = useState<string[]>([]);
  const [interviewTypes, setInterviewTypes] = useState<string[]>([]);
  const [hasResume, setHasResume] = useState(false);

  const [company, setCompany] = useState("");
  const [domain, setDomain] = useState("");
  const [role, setRole] = useState("");
  const [experience, setExperience] = useState("");
  const [interviewType, setInterviewType] = useState("");
  const [useResume, setUseResume] = useState(false);
  const [starting, setStarting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.getCompanies().then((d: any) => setCompanies(d.companies));
    api.getDomains().then((d: any) => {
      setDomains(d.domains);
      setRoles(d.roles);
      setExperienceLevels(d.experience_levels);
      setInterviewTypes(d.interview_types);
    });
    setHasResume(!!localStorage.getItem("interviewai_resume_uploaded"));
    const preselect = sessionStorage.getItem("interviewai_preselect_company");
    if (preselect) {
      setCompany(preselect);
      sessionStorage.removeItem("interviewai_preselect_company");
    }
  }, []);

  const canStart = company && domain && role && experience && interviewType && !starting;

  const handleStart = async () => {
    setStarting(true);
    setError("");
    try {
      const userName = localStorage.getItem("interviewai_user") || "Guest";
      const res: any = await api.startInterview({
        company, role, domain, experience_level: experience,
        interview_type: interviewType, user_name: userName, use_resume: useResume,
      });
      sessionStorage.setItem("interviewai_active_interview", JSON.stringify(res));
      navigate("/interview/live");
    } catch (e: any) {
      setError(e.message || "Could not start the interview. Is the backend running?");
      setStarting(false);
    }
  };

  const Select = ({
    label, value, onChange, options,
  }: { label: string; value: string; onChange: (v: string) => void; options: string[] }) => (
    <div>
      <label className="block text-sm text-slate-400 mb-1.5">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        <option value="">Select {label.toLowerCase()}…</option>
        {options.map((o) => (
          <option key={o} value={o}>{o}</option>
        ))}
      </select>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-semibold mb-1">Set up your mock interview</h1>
      <p className="text-slate-400 text-sm mb-8">
        Company-Focused Practice — realistic practice questions in a company's typical style, not real confidential questions.
      </p>

      <div className="glass rounded-2xl p-6 space-y-5">
        <Select label="Company" value={company} onChange={setCompany} options={companies} />
        <div className="grid grid-cols-2 gap-4">
          <Select label="Domain" value={domain} onChange={setDomain} options={domains} />
          <Select label="Role" value={role} onChange={setRole} options={roles} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <Select label="Experience level" value={experience} onChange={setExperience} options={experienceLevels} />
          <Select label="Interview type" value={interviewType} onChange={setInterviewType} options={interviewTypes} />
        </div>

        {hasResume && (
          <label className="flex items-center gap-2 text-sm text-slate-300 pt-1">
            <input type="checkbox" checked={useResume} onChange={(e) => setUseResume(e.target.checked)}
              className="rounded border-slate-600 bg-slate-900 text-brand-500 focus:ring-brand-500" />
            Personalize using my uploaded resume
          </label>
        )}
        {!hasResume && (
          <p className="text-xs text-slate-500">
            No resume uploaded yet — you can upload one from the Resume page for personalized project questions.
          </p>
        )}

        {error && <p className="text-sm text-rose-400">{error}</p>}

        <button
          onClick={handleStart}
          disabled={!canStart}
          className="w-full mt-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-40 disabled:cursor-not-allowed
            text-white font-medium rounded-xl py-3 transition-colors"
        >
          {starting ? "Starting…" : "🎤 Start Voice Interview"}
        </button>
      </div>
    </div>
  );
}
