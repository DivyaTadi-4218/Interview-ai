interface MicButtonProps {
  listening: boolean;
  disabled?: boolean;
  onClick?: () => void;
}

export default function MicButton({ listening, disabled, onClick }: MicButtonProps) {
  return (
    <div className="relative flex items-center justify-center h-28 w-28">
      {listening && (
        <>
          <span className="absolute inline-flex h-full w-full rounded-full bg-brand-500/40 animate-pulseRing" />
          <span className="absolute inline-flex h-full w-full rounded-full bg-brand-500/30 animate-pulseRing" style={{ animationDelay: "0.4s" }} />
        </>
      )}
      <button
        onClick={onClick}
        disabled={disabled}
        aria-label={listening ? "Listening" : "Microphone"}
        className={`relative z-10 h-20 w-20 rounded-full flex items-center justify-center text-3xl shadow-lg transition-all
          ${listening ? "bg-brand-600 scale-105" : "bg-slate-800 hover:bg-slate-700"}
          ${disabled ? "opacity-40 cursor-not-allowed" : "cursor-pointer"}`}
      >
        🎤
      </button>
    </div>
  );
}
