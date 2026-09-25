interface WaveformProps {
  active: boolean;
  color?: string;
}

export default function Waveform({ active, color = "bg-brand-400" }: WaveformProps) {
  const bars = [0, 1, 2, 3, 4, 5, 6];
  return (
    <div className="flex items-end gap-1 h-8">
      {bars.map((i) => (
        <span
          key={i}
          className={`w-1.5 rounded-full ${color} ${active ? "animate-wave" : ""}`}
          style={{
            height: active ? "100%" : "20%",
            animationDelay: `${i * 0.08}s`,
            opacity: active ? 1 : 0.3,
          }}
        />
      ))}
    </div>
  );
}
