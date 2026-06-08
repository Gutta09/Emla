import { useState } from "react";
import { useHistory } from "../hooks/useHistory";
import ExportModal from "../components/ExportModal";
import type { SessionEntry } from "../types";
import { useSpeech } from "../hooks/useSpeech";

export default function History() {
  const { sessions, deleteSession, clearAll, refresh } = useHistory();
  const { speak } = useSpeech();
  const [showExport, setShowExport] = useState(false);
  const [confirmClear, setConfirmClear] = useState(false);

  const handleReplay = (s: SessionEntry) => speak(s.sentence);

  return (
    <div style={{ maxWidth: 800, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 28 }}>Session History</h1>
          <p style={{ fontSize: 13, color: "var(--muted)", marginTop: 2 }}>
            {sessions.length} session{sessions.length !== 1 ? "s" : ""} recorded
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn btn-ghost" style={{ fontSize: 13, padding: "8px 14px" }} onClick={refresh}>
            ↺ Refresh
          </button>
          {sessions.length > 0 && (
            <>
              <button className="btn btn-secondary" style={{ fontSize: 13, padding: "8px 14px" }} onClick={() => setShowExport(true)}>
                ↓ Export
              </button>
              {confirmClear ? (
                <>
                  <button className="btn btn-danger" style={{ fontSize: 13, padding: "8px 14px" }} onClick={() => { clearAll(); setConfirmClear(false); }}>
                    Confirm Clear
                  </button>
                  <button className="btn btn-ghost" style={{ fontSize: 13, padding: "8px 14px" }} onClick={() => setConfirmClear(false)}>
                    Cancel
                  </button>
                </>
              ) : (
                <button className="btn btn-ghost" style={{ fontSize: 13, padding: "8px 14px", color: "var(--muted)" }} onClick={() => setConfirmClear(true)}>
                  Clear All
                </button>
              )}
            </>
          )}
        </div>
      </div>

      {sessions.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 0", color: "var(--muted)" }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>—</div>
          <div>No sessions yet. Go to Recognize and translate some signs!</div>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {sessions.map(s => (
            <div key={s.id} className="card" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ fontSize: 16, color: "var(--text)", lineHeight: 1.4, flex: 1 }}>
                  {s.sentence}
                </div>
                <div style={{ display: "flex", gap: 6, marginLeft: 12 }}>
                  <button className="btn btn-ghost" style={{ fontSize: 12, padding: "4px 10px" }} onClick={() => handleReplay(s)}>
                    ▶ Speak
                  </button>
                  <button className="btn btn-ghost" style={{ fontSize: 12, padding: "4px 10px", color: "var(--muted)" }} onClick={() => deleteSession(s.id)}>
                    ×
                  </button>
                </div>
              </div>

              <div style={{ display: "flex", flexWrap: "wrap", gap: 4 }}>
                {s.signs.map((sign, i) => (
                  <span key={i} style={{
                    fontSize: 11,
                    background: "var(--dark3)",
                    border: "1px solid var(--border)",
                    borderRadius: 4,
                    padding: "2px 6px",
                    color: "var(--text2)",
                  }}>
                    {sign}
                  </span>
                ))}
              </div>

              <div style={{ fontSize: 11, color: "var(--muted2)", display: "flex", gap: 12 }}>
                <span>{new Date(s.timestamp).toLocaleString()}</span>
                <span className="badge badge-muted" style={{ fontSize: 10 }}>{s.mode}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showExport && <ExportModal sessions={sessions} onClose={() => setShowExport(false)} />}
    </div>
  );
}
