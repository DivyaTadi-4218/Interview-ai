import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/client";
import { useSpeechRecognition } from "../hooks/useSpeechRecognition";
import { useSpeechSynthesis } from "../hooks/useSpeechSynthesis";
import AIAvatar from "../components/AIAvatar";
import MicButton from "../components/MicButton";
import Waveform from "../components/Waveform";
import ProgressBar from "../components/ProgressBar";
import type { Question, StartInterviewResponse } from "../types";

type Phase = "ai_speaking" | "listening" | "processing" | "complete" | "error";

export default function InterviewLive() {
  const navigate = useNavigate();
  const [session, setSession] = useState<StartInterviewResponse | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [progress, setProgress] = useState({ current: 0, total: 8 });
  const [phase, setPhase] = useState<Phase>("ai_speaking");
  const [lastTranscript, setLastTranscript] = useState("");
  const [statusMessage, setStatusMessage] = useState("");
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const hasGreetedRef = useRef(false);

  const { speak, speaking } = useSpeechSynthesis();

  const handleFinalTranscript = async (transcript: string) => {
    setLastTranscript(transcript);
    setPhase("processing");
    setStatusMessage("Let me evaluate that answer…");
    if (timerRef.current) clearInterval(timerRef.current);

    try {
      const interviewId = session!.interview_id;
      const res: any = await api.submitVoiceAnswer(interviewId, transcript);
      setProgress(res.progress);

      if (res.interview_complete) {
        setPhase("ai_speaking");
        speak(res.acknowledgement, () => {
          setPhase("complete");
          setTimeout(() => navigate(`/interview/report?id=${interviewId}`), 800);
        });
        return;
      }

      setCurrentQuestion(res.next_question);
      setPhase("ai_speaking");
      const toSpeak = `${res.acknowledgement} ${res.next_question.text}`;
      speak(toSpeak, () => startListening());
    } catch (e: any) {
      setPhase("error");
      setStatusMessage("Something went wrong reaching the interview server. You can try answering again.");
    }
  };

  const {
    supported, listening, interimTranscript, permissionDenied, noSpeechDetected, start, stop,
  } = useSpeechRecognition({ onFinalResult: handleFinalTranscript });

  const startListening = () => {
    setLastTranscript("");
    setRecordingSeconds(0);
    setPhase("listening");
    setStatusMessage("Listening…");
    start();
    timerRef.current = setInterval(() => setRecordingSeconds((s) => s + 1), 1000);
  };

  useEffect(() => {
    if (!listening && timerRef.current) {
      clearInterval(timerRef.current);
    }
  }, [listening]);

  useEffect(() => {
    const raw = sessionStorage.getItem("interviewai_active_interview");
    if (!raw) {
      navigate("/interview/setup");
      return;
    }
    const parsed: StartInterviewResponse = JSON.parse(raw);
    setSession(parsed);
    setCurrentQuestion(parsed.first_question);
    setProgress({ current: 0, total: parsed.total_planned_questions });

    if (!hasGreetedRef.current) {
      hasGreetedRef.current = true;
      setPhase("ai_speaking");
      speak(`${parsed.greeting} ${parsed.first_question.text}`, () => startListening());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (noSpeechDetected && phase === "listening") {
      setStatusMessage("I'm listening. Please answer when you're ready.");
    }
  }, [noSpeechDetected, phase]);

  const handleEndInterview = async () => {
    stop();
    if (session) {
      try {
        await fetch(
          `${(import.meta as any).env.VITE_API_URL || "http://localhost:8000"}/interviews/${session.interview_id}/complete`,
          { method: "POST" }
        );
      } catch {
        // ignore — user is leaving anyway
      }
      navigate(`/interview/report?id=${session.interview_id}`);
    } else {
      navigate("/dashboard");
    }
  };

  if (!supported) {
    return (
      <div className="max-w-lg mx-auto px-6 py-16 text-center">
        <p className="text-lg mb-2">🎙️ Voice not supported</p>
        <p className="text-slate-400 text-sm">
          Your browser doesn't support the Web Speech API needed for the voice interview.
          Please try the latest Chrome or Edge on desktop.
        </p>
      </div>
    );
  }

  if (permissionDenied) {
    return (
      <div className="max-w-lg mx-auto px-6 py-16 text-center">
        <p className="text-lg mb-2">🔒 Microphone access is required for the voice interview.</p>
        <p className="text-slate-400 text-sm">
          Please allow microphone access in your browser's address-bar permissions, then refresh this page to try again.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <div className="mb-6">
        <ProgressBar current={progress.current} total={progress.total} />
      </div>

      <div className="glass rounded-2xl p-8 flex flex-col items-center gap-6">
        <AIAvatar speaking={phase === "ai_speaking" && speaking} />

        {currentQuestion && (
          <div className="text-center max-w-lg">
            <p className="text-xs uppercase tracking-wide text-slate-500 mb-2">
              {currentQuestion.topic ? `Topic: ${currentQuestion.topic}` : "Question"}
            </p>
            <p className="text-lg font-medium">{currentQuestion.text}</p>
          </div>
        )}

        <div className="h-px w-full bg-slate-800" />

        <div className="flex flex-col items-center gap-3">
          <MicButton listening={listening} disabled={phase !== "listening" && phase !== "ai_speaking"} onClick={() => {
            if (phase !== "listening") startListening();
          }} />
          <p className="text-sm text-slate-400 min-h-[1.25rem]">
            {phase === "ai_speaking" && "AI is speaking…"}
            {phase === "listening" && `${statusMessage} (${recordingSeconds}s)`}
            {phase === "processing" && statusMessage}
            {phase === "complete" && "Interview complete — building your report…"}
            {phase === "error" && statusMessage}
          </p>
          <Waveform active={listening} />
        </div>

        <div className="w-full">
          <p className="text-xs uppercase tracking-wide text-slate-500 mb-1">You said</p>
          <div className="min-h-[3rem] rounded-xl bg-slate-900/60 border border-slate-800 px-4 py-3 text-sm text-slate-300">
            {listening ? interimTranscript || "…" : lastTranscript || "Your answer will appear here as you speak."}
          </div>
        </div>
      </div>

      <div className="flex justify-center mt-6">
        <button
          onClick={handleEndInterview}
          className="text-sm px-4 py-2 rounded-lg border border-rose-800 text-rose-300 hover:bg-rose-950/40 transition-colors"
        >
          End Interview
        </button>
      </div>
    </div>
  );
}
