interface AIAvatarProps {
  speaking: boolean;
}

export default function AIAvatar({ speaking }: AIAvatarProps) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative h-24 w-24">
        {speaking && (
          <span className="absolute inset-0 rounded-full bg-emerald-500/30 animate-pulseRing" />
        )}
        <div
          className={`relative h-24 w-24 rounded-full flex items-center justify-center text-4xl border-2 transition-colors
            ${speaking ? "bg-emerald-600/20 border-emerald-400" : "bg-slate-800 border-slate-700"}`}
        >
          🤖
        </div>
      </div>
      <div className="flex items-center gap-2 text-sm">
        <span className={`h-2 w-2 rounded-full ${speaking ? "bg-emerald-400" : "bg-slate-600"}`} />
        <span className={speaking ? "text-emerald-300" : "text-slate-500"}>
          {speaking ? "Speaking…" : "AI Interviewer"}
        </span>
      </div>
    </div>
  );
}
