import { useState } from "react";
import { API_BASE } from "../config";
import type { LandmarkFrame, RecognizeMode } from "../types";

interface FeedbackPanelProps {
  mode: RecognizeMode;
  modelGuess: string;
  confidence: number;
  frameBuffer: LandmarkFrame[];
}

export default function FeedbackPanel({ mode, modelGuess, confidence, frameBuffer }: FeedbackPanelProps) {
  const [label, setLabel] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "done" | "error">("idle");

  const handleSubmit = async () => {
    const trimmed = label.trim().toUpperCase();
    if (!trimmed || frameBuffer.length === 0) return;

    setStatus("sending");

    // Build sequence from frame buffer
    // For word mode: flatten each frame into a flat float array (pose + hands)
    // For fingerspell: use just the last frame's hands
    const sequence = frameBuffer.map(frame => {
      const pose = frame.pose.flatMap(l => [l.x, l.y, l.z]);
      const left = frame.left_hand ? frame.left_hand.flatMap(l => [l.x, l.y, l.z]) : new Array(63).fill(0);
      const right = frame.right_hand ? frame.right_hand.flatMap(l => [l.x, l.y, l.z]) : new Array(63).fill(0);
      return [...pose, ...left, ...right];
    });

    try {
      const res = await fetch(`${API_BASE}/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          label: trimmed,
          mode,
          sequence,
          confidence,
          model_guess: modelGuess,
        }),
      });
      if (!res.ok) throw new Error("failed");
      setStatus("done");
      setLabel("");
      setTimeout(() => setStatus("idle"), 2000);
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 2000);
    }
  };

  if (status === "done") {
    return (
      <div className="animate-fade-in" style={{
        background: "rgba(61,220,132,0.08)",
        border: "1px solid rgba(61,220,132,0.2)",
        borderRadius: "var(--radius)",
        padding: "10px 14px",
        fontSize: 13,
        color: "var(--green)",
      }}>
        ✓ Saved! This will help improve the model.
      </div>
    );
  }

  return (
    <div style={{
      background: "rgba(201,168,76,0.05)",
      border: "1px solid rgba(201,168,76,0.15)",
      borderRadius: "var(--radius)",
      padding: "12px 14px",
    }}>
      <div style={{ fontSize: 12, color: "var(--gold)", fontWeight: 600, marginBottom: 8 }}>
        Model isn't sure — what sign is this?
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <input
          type="text"
          placeholder="Type sign name (e.g. HELLO)"
          value={label}
          onChange={e => setLabel(e.target.value)}
          onKeyDown={e => e.key === "Enter" && handleSubmit()}
          style={{ flex: 1, fontSize: 13, padding: "7px 10px", textTransform: "uppercase" }}
          disabled={status === "sending"}
        />
        <button
          className="btn btn-primary"
          style={{ padding: "7px 14px", fontSize: 13 }}
          onClick={handleSubmit}
          disabled={!label.trim() || status === "sending"}
        >
          {status === "sending" ? "…" : "Teach"}
        </button>
      </div>
      {status === "error" && (
        <div style={{ fontSize: 11, color: "var(--red)", marginTop: 6 }}>Failed to save — check backend connection.</div>
      )}
      <div style={{ fontSize: 11, color: "var(--muted2)", marginTop: 6 }}>
        Your corrections are saved locally and used to retrain the model.
      </div>
    </div>
  );
}
