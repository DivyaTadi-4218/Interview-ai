import { useRef, useState } from "react";
import api from "../api/client";

export default function Resume() {
  const [result, setResult] = useState<any>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setUploading(true);
    setError("");
    try {
      const userName = localStorage.getItem("interviewai_user") || "Guest";
      const res = await api.uploadResume(file, userName);
      setResult(res);
      localStorage.setItem("interviewai_resume_uploaded", "true");
    } catch (e: any) {
      setError("Could not read that PDF. Please try a different file.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-10 space-y-6">
      <div>
        <h1 className="text-2xl font-semibold">Resume-Based Interview</h1>
        <p className="text-slate-400 text-sm">
          Upload your resume so the AI can ask about your actual projects and experience — nothing is invented.
        </p>
      </div>

      <div
        onClick={() => inputRef.current?.click()}
        className="glass rounded-2xl p-10 text-center cursor-pointer border-2 border-dashed border-slate-700 hover:border-brand-500/60 transition-colors"
      >
        <p className="text-3xl mb-2">📄</p>
        <p className="text-sm text-slate-300">Click to upload your resume (PDF)</p>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </div>

      {uploading && <p className="text-sm text-slate-400 text-center">Analyzing your resume…</p>}
      {error && <p className="text-sm text-rose-400 text-center">{error}</p>}

      {result && (
        <div className="glass rounded-2xl p-6 space-y-4">
          <div>
            <h3 className="text-sm font-medium mb-2">Skills found</h3>
            <div className="flex flex-wrap gap-2">
              {result.skills.map((s: string) => (
                <span key={s} className="text-xs px-2.5 py-1 rounded-full bg-brand-600/20 text-brand-300">{s}</span>
              ))}
              {result.skills.length === 0 && <p className="text-xs text-slate-500">No recognizable skills extracted.</p>}
            </div>
          </div>
          {result.projects?.length > 0 && (
            <div>
              <h3 className="text-sm font-medium mb-2">Projects found</h3>
              <ul className="text-sm text-slate-300 list-disc list-inside space-y-1">
                {result.projects.map((p: any, i: number) => <li key={i}>{p.title}</li>)}
              </ul>
            </div>
          )}
          <p className="text-xs text-slate-500 pt-2">
            You can now enable "Personalize using my uploaded resume" when starting a new interview.
          </p>
        </div>
      )}
    </div>
  );
}
