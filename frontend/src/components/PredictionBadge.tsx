import ConfidenceBar from "./ConfidenceBar";
import type { Prediction } from "../types";

interface PredictionBadgeProps {
  prediction: Prediction | null;
  isConnected: boolean;
}

export default function PredictionBadge({ prediction, isConnected }: PredictionBadgeProps) {
  if (!isConnected) {
    return (
      <div style={{ textAlign: "center", padding: "24px 0" }}>
        <div style={{ fontSize: 13, color: "var(--muted)" }} className="animate-pulse">
          Connecting to backend…
        </div>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div style={{ textAlign: "center", padding: "24px 0" }}>
        <div style={{ fontSize: 13, color: "var(--muted)" }}>
          Start signing to see predictions
        </div>
      </div>
    );
  }

  const { sign, confidence, uncertain } = prediction;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div style={{ textAlign: "center" }}>
        <div
          className="animate-fade-in"
          style={{
            fontSize: uncertain ? 48 : 56,
            fontFamily: "Barlow Condensed, sans-serif",
            fontWeight: 700,
            letterSpacing: "0.04em",
            color: uncertain ? "var(--muted)" : "var(--gold2)",
            lineHeight: 1,
            transition: "color 0.2s",
          }}
        >
          {uncertain ? "?" : sign}
        </div>
        {!uncertain && (
          <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4, letterSpacing: "0.08em", textTransform: "uppercase" }}>
            {prediction.mode === "fingerspell" ? "Letter" : "Sign"}
          </div>
        )}
      </div>
      <ConfidenceBar value={confidence} uncertain={uncertain} />
    </div>
  );
}
