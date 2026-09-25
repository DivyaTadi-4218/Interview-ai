export interface Question {
  id: number;
  order_index: number;
  text: string;
  topic?: string;
  difficulty: string;
}

export interface StartInterviewResponse {
  interview_id: number;
  greeting: string;
  first_question: Question;
  total_planned_questions: number;
}

export interface VoiceAnswerResponse {
  acknowledgement: string;
  evaluation_summary: { overall_score: number; feedback?: string };
  next_question: Question | null;
  interview_complete: boolean;
  progress: { current: number; total: number };
}

export interface InterviewReport {
  interview_id: number;
  overall_score: number;
  technical_score: number;
  communication_score: number;
  strengths: string[];
  weak_areas: string[];
  questions_answered_well: { question: string; score: number; feedback?: string }[];
  questions_needing_improvement: { question: string; score: number; feedback?: string; suggested_answer?: string }[];
  topics_to_study: string[];
  roadmap: RoadmapDay[];
  recommended_practice_questions: string[];
}

export interface RoadmapDay {
  day: number;
  topic: string;
  explanation: string;
  key_concepts: string[];
  interview_questions: string[];
  quiz: { q: string; a: string }[];
  coding_practice: boolean;
}

export interface DashboardData {
  interviews_completed: number;
  average_performance: number;
  technical_score: number;
  communication_score: number;
  strongest_domains: string[];
  weakest_domains: string[];
  recent_interviews: { id: number; company: string; role: string; status: string; score: number; created_at: string }[];
  learning_progress: number;
  recommended_next_practice: string | null;
}

export interface InterviewSetup {
  company: string;
  role: string;
  domain: string;
  experience_level: string;
  interview_type: string;
  use_resume: boolean;
}
