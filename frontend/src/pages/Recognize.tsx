import { useState, useCallback } from "react";
import WebcamCanvas from "../components/WebcamCanvas";
import PredictionBadge from "../components/PredictionBadge";
import TopKPredictions from "../components/TopKPredictions";
import SentenceBuilder from "../components/SentenceBuilder";
import SettingsPanel from "../components/SettingsPanel";
import FeedbackPanel from "../components/FeedbackPanel";
import { useRecognition } from "../hooks/useRecognition";
import type { LandmarkFrame, RecognizeMode } from "../types";
import { DEFAULT_CONFIDENCE_THRESHOLD } from "../config";

export default function Recognize() {
  const [active, setActive] = useState(true);
  const [threshold, setThreshold] = useState(DEFAULT_CONFIDENCE_THRESHOLD);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  const { connected, modelsLoaded, vocabularySize, prediction, sentence, mode, frameBuffer, setMode, onFrame, clearSentence } = useRecognition();

  const handleFrame = useCallback((frame: LandmarkFrame) => {
    onFrame(frame);
  }, [onFrame]);

  const modeButtons: { value: RecognizeMode; label: string }[] = [
    { value: "word", label: "Word Signs" },
    { value: "fingerspell", label: "Fingerspell" },
  ];

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28 }}>Sign Recognition</h1>
          <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 2 }}>
            {modelsLoaded.length > 0
              ? `${vocabularySize} signs loaded: ${modelsLoaded.join(", ")}`
              : connected ? "Loading models…" : "Backend disconnected"}
          </p>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          {/* Connection status */}
          <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: connected ? "var(--green)" : "var(--red)" }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: connected ? "var(--green)" : "var(--red)" }} />
            {connected ? "Connected" : "Offline"}
          </div>
          <button
            className="btn btn-ghost"
            style={{ padding: "8px 14px", fontSize: 13 }}
            onClick={() => setActive(a => !a)}
          >
            {active ? "⏸ Pause" : "▶ Resume"}
          </button>
          <button
            className={`btn ${showSettings ? "btn-secondary" : "btn-ghost"}`}
            style={{ padding: "8px 14px", fontSize: 13 }}
            onClick={() => setShowSettings(s => !s)}
          >
            ⚙ Settings
          </button>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 380px", gap: 20, alignItems: "start" }}>
        {/* Left: Camera */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Mode selector */}
          <div style={{ display: "flex", gap: 8 }}>
            {modeButtons.map(({ value, label }) => (
              <button
                key={value}
                className={`btn ${mode === value ? "btn-primary" : "btn-ghost"}`}
                style={{ fontSize: 13, padding: "8px 16px" }}
                onClick={() => setMode(value)}
              >
                {label}
              </button>
            ))}
          </div>

          <WebcamCanvas onFrame={handleFrame} active={active} />

          {showSettings && (
            <div className="card animate-fade-in">
              <h3 style={{ fontSize: 15, marginBottom: 16 }}>Settings</h3>
              <SettingsPanel
                threshold={threshold}
                onThresholdChange={setThreshold}
                ttsEnabled={ttsEnabled}
                onTtsChange={setTtsEnabled}
              />
            </div>
          )}
        </div>

        {/* Right: Prediction + Sentence */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Prediction panel */}
          <div className="card">
            <div style={{ fontSize: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 16 }}>
              Current Prediction
            </div>
            <PredictionBadge prediction={prediction} isConnected={connected} />
            {prediction && (prediction as any).hint && (
              <div style={{ marginTop: 10, fontSize: 12, color: "var(--amber)", background: "rgba(212,135,78,0.08)", borderRadius: 6, padding: "6px 10px" }}>
                ⚠ {(prediction as any).hint}
              </div>
            )}
            {prediction && !prediction.uncertain && (
              <div style={{ marginTop: 12 }}>
                <TopKPredictions top3={prediction.top3} />
              </div>
            )}
          </div>

          {/* Teach the model when it's unsure */}
          {prediction && prediction.uncertain && prediction.sign !== "—" && frameBuffer.length > 0 && (
            <FeedbackPanel
              mode={mode}
              modelGuess={prediction.sign}
              confidence={prediction.confidence}
              frameBuffer={frameBuffer}
            />
          )}

          {/* Sentence builder */}
          <div className="card">
            <SentenceBuilder words={sentence} mode={mode} onClear={clearSentence} />
          </div>

          {/* Tips */}
          <div style={{
            background: "rgba(201,168,76,0.05)",
            border: "1px solid rgba(201,168,76,0.15)",
            borderRadius: "var(--radius)",
            padding: "12px 14px",
            fontSize: 12,
            color: "var(--muted)",
            lineHeight: 1.6,
          }}>
            <strong style={{ color: "var(--gold)", display: "block", marginBottom: 4 }}>Tips</strong>
            Hold each sign for ~1 second for best accuracy.
            Stay still between signs — the system uses the pause to commit a word.
            {mode === "fingerspell" ? " Fingerspell one letter at a time." : " Sign complete words with clear movement."}
          </div>
        </div>
      </div>
    </div>
  );
}
