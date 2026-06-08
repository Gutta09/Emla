import type { TopKItem } from "../types";

interface TopKPredictionsProps {
  top3: TopKItem[];
}

export default function TopKPredictions({ top3 }: TopKPredictionsProps) {
  if (!top3 || top3.length < 2) return null;
  const alternatives = top3.slice(1);

  return (
    <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
      <span style={{ fontSize: 12, color: "var(--muted)", paddingTop: 2 }}>Also:</span>
      {alternatives.map(item => (
        <div key={item.sign} style={{
          fontSize: 12,
          color: "var(--text2)",
          background: "var(--dark3)",
          border: "1px solid var(--border)",
          borderRadius: 6,
          padding: "2px 10px",
        }}>
          {item.sign} <span style={{ color: "var(--muted)" }}>{Math.round(item.confidence * 100)}%</span>
        </div>
      ))}
    </div>
  );
}
