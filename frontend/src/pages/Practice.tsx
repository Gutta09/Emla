import { useState, useCallback, useEffect, useRef } from "react";
import WebcamCanvas from "../components/WebcamCanvas";
import ConfidenceBar from "../components/ConfidenceBar";
import { useRecognition } from "../hooks/useRecognition";
import type { LandmarkFrame } from "../types";
import { API_BASE } from "../config";
import type { SignInfo } from "../types";

const CONFIRM_FRAMES = 5;

export default function Practice() {
  const [signs, setSigns] = useState<SignInfo[]>([]);
  const [target, setTarget] = useState<SignInfo | null>(null);
  const [status, setStatus] = useState<"idle" | "correct" | "wrong">("idle");
  const [score, setScore] = useState({ correct: 0, total: 0 });
  const confirmCount = useRef(0);

  const { connected, prediction, onFrame, setMode } = useRecognition();

  useEffect(() => {
    setMode("fingerspell");
    fetch(`${API_BASE}/vocabulary`).then(r => r.json()).then(data => {
      const list: SignInfo[] = data.signs ?? [];
      setSigns(list);
      pickRandom(list);
    }).catch(() => {});
  }, [setMode]);

  const pickRandom = (list?: SignInfo[]) => {
    const pool = list ?? signs;
    if (!pool.length) return;
    const next = pool[Math.floor(Math.random() * pool.length)];
    setTarget(next);
    setStatus("idle");
    confirmCount.current = 0;
  };

  useEffect(() => {
    if (!prediction || !target || status !== "idle") return;
    const match = prediction.sign?.toUpperCase() === target.label.toUpperCase();
    if (match && !prediction.uncertain) {
      confirmCount.current++;
      if (confirmCount.current >= CONFIRM_FRAMES) {
        setStatus("correct");
        setScore(s => ({ correct: s.correct + 1, total: s.total + 1 }));
        setTimeout(() => pickRandom(), 1500);
      }
    } else {
      confirmCount.current = 0;
    }
  }, [prediction, target, status]);

  const handleSkip = () => {
    setScore(s => ({ ...s, total: s.total + 1 }));
    pickRandom();
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28 }}>Practice Mode</h1>
          <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 2 }}>
            Sign the target and hold it — get {CONFIRM_FRAMES} consecutive correct predictions to advance.
          </p>
        </div>
        <div style={{
          display: "flex",
          gap: 16,
          fontSize: 14,
          color: "var(--muted)",
        }}>
          <span>Correct: <strong style={{ color: "var(--green)" }}>{score.correct}</strong></span>
          <span>Total: <strong style={{ color: "var(--text)" }}>{score.total}</strong></span>
          {score.total > 0 && (
            <span>Accuracy: <strong style={{ color: "var(--gold)" }}>
              {Math.round(score.correct / score.total * 100)}%
            </strong></span>
          )}
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 300px", gap: 20 }}>
        <WebcamCanvas onFrame={onFrame} active={true} />

        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Target sign */}
          <div className="card" style={{ textAlign: "center" }}>
            <div style={{ fontSize: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 12 }}>
              Sign This
            </div>
            {target ? (
              <>
                <div style={{
                  fontSize: 72,
                  fontFamily: "Barlow Condensed, sans-serif",
                  fontWeight: 700,
                  color: status === "correct" ? "var(--green)" : status === "wrong" ? "var(--red)" : "var(--gold2)",
                  lineHeight: 1,
                  transition: "color 0.3s",
                }}>
                  {target.label}
                </div>
                {target.description && (
                  <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 8, lineHeight: 1.4 }}>
                    {target.description}
                  </div>
                )}
                <div style={{ marginTop: 12 }}>
                  {status === "correct" && (
                    <div className="badge badge-green animate-fade-in" style={{ fontSize: 14 }}>✓ Correct!</div>
                  )}
                </div>
              </>
            ) : (
              <div style={{ color: "var(--muted)", fontSize: 14 }}>Loading vocabulary…</div>
            )}
          </div>

          {/* Current detection */}
          {prediction && (
            <div className="card">
              <div style={{ fontSize: 12, color: "var(--muted)", marginBottom: 10 }}>Detecting</div>
              <div style={{ fontSize: 32, fontFamily: "Barlow Condensed, sans-serif", fontWeight: 700, color: prediction.uncertain ? "var(--muted)" : "var(--text)", marginBottom: 10 }}>
                {prediction.uncertain ? "?" : prediction.sign}
              </div>
              <ConfidenceBar value={prediction.confidence} uncertain={prediction.uncertain} />
              {!prediction.uncertain && target && prediction.sign === target.label && (
                <div style={{ marginTop: 8, fontSize: 12, color: "var(--green)" }}>
                  Match! Hold steady… {confirmCount.current}/{CONFIRM_FRAMES}
                </div>
              )}
            </div>
          )}

          <div style={{ display: "flex", gap: 8 }}>
            <button className="btn btn-ghost" style={{ flex: 1, justifyContent: "center" }} onClick={handleSkip}>
              Skip
            </button>
            <button className="btn btn-secondary" style={{ flex: 1, justifyContent: "center" }} onClick={() => pickRandom()}>
              New Sign
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
