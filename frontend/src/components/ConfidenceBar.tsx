interface ConfidenceBarProps {
  value: number;  // 0–1
  uncertain?: boolean;
}

export default function ConfidenceBar({ value, uncertain }: ConfidenceBarProps) {
  const pct = Math.round(value * 100);
  const color = uncertain ? "var(--muted)" : value > 0.8 ? "var(--green)" : value > 0.6 ? "var(--gold)" : "var(--amber)";

  return (
    <div style={{ width: "100%" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4, fontSize: 12, color: "var(--muted)" }}>
        <span>Confidence</span>
        <span style={{ color }}>{pct}%</span>
      </div>
      <div style={{ height: 4, background: "var(--dark3)", borderRadius: 2, overflow: "hidden" }}>
        <div style={{
          height: "100%",
          width: `${pct}%`,
          background: color,
          borderRadius: 2,
          transition: "width 0.15s ease, background 0.15s ease",
        }} />
      </div>
    </div>
  );
}
