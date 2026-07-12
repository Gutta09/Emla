import { useState } from "react";
import { API_BASE } from "../config";
import type { RecognizeMode } from "../types";
import { useSpeech } from "../hooks/useSpeech";

interface SentenceBuilderProps {
  words: string[];
  mode: RecognizeMode;
  onClear: () => void;
}

export default function SentenceBuilder({ words, mode, onClear }: SentenceBuilderProps) {
  const { speak, isSpeaking, stop } = useSpeech();
  const [translating, setTranslating] = useState(false);
  const [translatedSentence, setTranslatedSentence] = useState("");

  const handleTranslate = async () => {
    if (!words.length) return;
    setTranslating(true);
    setTranslatedSentence("");
    try {
      const res = await fetch(`${API_BASE}/translate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ signs: words }),
      });
      const data = await res.json();
      setTranslatedSentence(data.sentence ?? "");
      speak(data.sentence);
    } catch {
      setTranslatedSentence("Translation failed — check backend connection.");
    } finally {
      setTranslating(false);
    }
  };

  const handleClear = () => {
    onClear();
    setTranslatedSentence("");
    stop();
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 12, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em" }}>
          Sentence Builder
        </span>
        <span style={{ fontSize: 12, color: "var(--muted)" }}>{words.length} sign{words.length !== 1 ? "s" : ""}</span>
      </div>

      <div style={{
        minHeight: 48,
        background: "var(--dark3)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius)",
        padding: "10px 14px",
        display: "flex",
        flexWrap: "wrap",
        gap: 6,
        alignItems: "center",
      }}>
        {words.length === 0 ? (
          <span style={{ fontSize: 13, color: "var(--muted2)" }}>Sign and hold — recognized signs appear here automatically…</span>
        ) : (
          words.map((w, i) => (
            <span key={i} className="badge badge-gold" style={{ fontSize: 13, textTransform: "none", fontWeight: 500 }}>
              {w.replace(/_/g, " ")}
            </span>
          ))
        )}
      </div>

      {translatedSentence && (
        <div className="animate-fade-in" style={{
          background: "rgba(201,168,76,0.07)",
          border: "1px solid rgba(201,168,76,0.2)",
          borderRadius: "var(--radius)",
          padding: "12px 14px",
          fontSize: 15,
          color: "var(--text)",
          lineHeight: 1.5,
        }}>
          <span style={{ fontSize: 11, color: "var(--gold)", textTransform: "uppercase", letterSpacing: "0.08em", display: "block", marginBottom: 4 }}>
            Translation
          </span>
          {translatedSentence}
        </div>
      )}

      <div style={{ display: "flex", gap: 8 }}>
        <button
          className="btn btn-primary"
          onClick={handleTranslate}
          disabled={words.length === 0 || translating}
          style={{ flex: 1, justifyContent: "center", opacity: words.length === 0 ? 0.4 : 1 }}
        >
          {translating ? "Translating…" : isSpeaking ? "Speaking…" : "Translate & Speak"}
        </button>
        {isSpeaking && (
          <button className="btn btn-secondary" onClick={stop} style={{ padding: "10px 14px" }}>
            ■
          </button>
        )}
        <button
          className="btn btn-ghost"
          onClick={handleClear}
          disabled={words.length === 0}
          style={{ padding: "10px 14px", opacity: words.length === 0 ? 0.4 : 1 }}
        >
          Clear
        </button>
      </div>
    </div>
  );
}
