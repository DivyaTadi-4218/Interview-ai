const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export const api = {
  getCompanies: () => request<{ companies: string[] }>("/companies"),
  getDomains: () =>
    request<{ domains: string[]; roles: string[]; experience_levels: string[]; interview_types: string[] }>(
      "/domains"
    ),
  startInterview: (payload: Record<string, unknown>) =>
    request("/interviews/start", { method: "POST", body: JSON.stringify(payload) }),
  submitVoiceAnswer: (interviewId: number, transcript: string) =>
    request(`/interviews/${interviewId}/voice-answer`, {
      method: "POST",
      body: JSON.stringify({ transcript }),
    }),
  getReport: (interviewId: number) => request<any>(`/interviews/${interviewId}/report`),
  getHistory: (userName: string) => request(`/interviews/history?user_name=${encodeURIComponent(userName)}`),
  getDashboard: (userName: string) => request<any>(`/dashboard?user_name=${encodeURIComponent(userName)}`),
  uploadResume: async (file: File, userName: string) => {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE_URL}/resume/upload?user_name=${encodeURIComponent(userName)}`, {
      method: "POST",
      body: form,
    });
    if (!res.ok) throw new Error(await res.text());
    return res.json();
  },
  generateRoadmap: (payload: Record<string, unknown>, userName: string) =>
    request(`/learning/roadmap?user_name=${encodeURIComponent(userName)}`, {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  reviewCode: (language: string, code: string) =>
    request("/coding/review", { method: "POST", body: JSON.stringify({ language, code }) }),
  reviewSql: (question: string, query: string) =>
    request("/sql/review", { method: "POST", body: JSON.stringify({ question, query }) }),
};

export default api;
