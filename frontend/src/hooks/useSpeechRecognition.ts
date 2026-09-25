import { useCallback, useEffect, useRef, useState } from "react";

// Minimal ambient typing for the (non-standard) Web Speech API so this
// compiles without extra @types packages.
type SpeechRecognitionResultEvent = any;

interface UseSpeechRecognitionOptions {
  onFinalResult: (transcript: string) => void;
  silenceTimeoutMs?: number;
}

export function useSpeechRecognition({ onFinalResult, silenceTimeoutMs = 2200 }: UseSpeechRecognitionOptions) {
  const [supported, setSupported] = useState(true);
  const [listening, setListening] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState("");
  const [permissionDenied, setPermissionDenied] = useState(false);
  const [noSpeechDetected, setNoSpeechDetected] = useState(false);

  const recognitionRef = useRef<any>(null);
  const silenceTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const finalTranscriptRef = useRef("");

  useEffect(() => {
    const SpeechRecognitionCtor =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) {
      setSupported(false);
      return;
    }
    const recognition = new SpeechRecognitionCtor();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "en-US";

    recognition.onresult = (event: SpeechRecognitionResultEvent) => {
      setNoSpeechDetected(false);
      let interim = "";
      let final = finalTranscriptRef.current;
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcriptPiece + " ";
        } else {
          interim += transcriptPiece;
        }
      }
      finalTranscriptRef.current = final;
      setInterimTranscript(final + interim);

      if (silenceTimer.current) clearTimeout(silenceTimer.current);
      silenceTimer.current = setTimeout(() => {
        recognition.stop();
      }, silenceTimeoutMs);
    };

    recognition.onerror = (event: any) => {
      if (event.error === "not-allowed" || event.error === "permission-denied") {
        setPermissionDenied(true);
      }
      if (event.error === "no-speech") {
        setNoSpeechDetected(true);
      }
    };

    recognition.onend = () => {
      setListening(false);
      if (silenceTimer.current) clearTimeout(silenceTimer.current);
      const finalText = finalTranscriptRef.current.trim();
      if (finalText) {
        onFinalResult(finalText);
      } else {
        setNoSpeechDetected(true);
      }
      finalTranscriptRef.current = "";
    };

    recognitionRef.current = recognition;
    return () => {
      recognition.onresult = null;
      recognition.onerror = null;
      recognition.onend = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [silenceTimeoutMs]);

  const start = useCallback(() => {
    if (!recognitionRef.current) return;
    setNoSpeechDetected(false);
    setInterimTranscript("");
    finalTranscriptRef.current = "";
    try {
      recognitionRef.current.start();
      setListening(true);
    } catch {
      // already started — ignore
    }
  }, []);

  const stop = useCallback(() => {
    recognitionRef.current?.stop();
  }, []);

  return { supported, listening, interimTranscript, permissionDenied, noSpeechDetected, start, stop };
}
