import type { SessionEntry } from "../types";

interface ExportModalProps {
  sessions: SessionEntry[];
  onClose: () => void;
}

function formatSrtTime(ms: number): string {
  const h = Math.floor(ms / 3600000);
  const m = Math.floor((ms % 3600000) / 60000);
  const s = Math.floor((ms % 60000) / 1000);
  const ms2 = ms % 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")},${String(ms2).padStart(3, "0")}`;
}

function toSrt(sessions: SessionEntry[]): string {
  return sessions.map((s, i) => (
    `${i + 1}\n${formatSrtTime(s.start_ms)} --> ${formatSrtTime(s.end_ms)}\n${s.sentence}\n`
  )).join("\n");
}

function toTxt(sessions: SessionEntry[]): string {
  return sessions.map((s, i) => (
    `[${new Date(s.timestamp).toLocaleString()}]\n${s.sentence}\nSigns: ${s.signs.join(", ")}\n`
  )).join("\n---\n\n");
}

function downloadFile(content: string, filename: string, type: string) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export default function ExportModal({ sessions, onClose }: ExportModalProps) {
  return (
    <div
      style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
      onClick={onClose}
    >
      <div
        className="card animate-slide-up"
        style={{ width: 340, display: "flex", flexDirection: "column", gap: 16 }}
        onClick={e => e.stopPropagation()}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h3 style={{ fontSize: 18 }}>Export Captions</h3>
          <button className="btn btn-ghost" style={{ padding: "4px 10px", fontSize: 18, lineHeight: 1 }} onClick={onClose}>×</button>
        </div>

        <p style={{ fontSize: 13, color: "var(--muted)" }}>
          Export {sessions.length} session{sessions.length !== 1 ? "s" : ""} as a file.
        </p>

        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          <button
            className="btn btn-primary"
            style={{ justifyContent: "center" }}
            onClick={() => downloadFile(toSrt(sessions), "emla-captions.srt", "text/srt")}
          >
            Download .srt (Subtitles)
          </button>
          <button
            className="btn btn-secondary"
            style={{ justifyContent: "center" }}
            onClick={() => downloadFile(toTxt(sessions), "emla-captions.txt", "text/plain")}
          >
            Download .txt (Plain text)
          </button>
        </div>
      </div>
    </div>
  );
}
