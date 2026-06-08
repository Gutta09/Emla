interface SettingsPanelProps {
  threshold: number;
  onThresholdChange: (v: number) => void;
  ttsEnabled: boolean;
  onTtsChange: (v: boolean) => void;
}

export default function SettingsPanel({ threshold, onThresholdChange, ttsEnabled, onTtsChange }: SettingsPanelProps) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      <div>
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8, fontSize: 13 }}>
          <label style={{ color: "var(--text2)" }}>Confidence threshold</label>
          <span style={{ color: "var(--gold)" }}>{Math.round(threshold * 100)}%</span>
        </div>
        <input
          type="range"
          min={0.4}
          max={0.95}
          step={0.05}
          value={threshold}
          onChange={e => onThresholdChange(parseFloat(e.target.value))}
          style={{ width: "100%", accentColor: "var(--gold)" }}
        />
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--muted)", marginTop: 4 }}>
          <span>More guesses</span>
          <span>More precise</span>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span style={{ fontSize: 13, color: "var(--text2)" }}>Text-to-speech</span>
        <button
          onClick={() => onTtsChange(!ttsEnabled)}
          style={{
            width: 40,
            height: 22,
            borderRadius: 11,
            background: ttsEnabled ? "var(--gold)" : "var(--dark4)",
            border: "1px solid var(--border2)",
            position: "relative",
            cursor: "pointer",
            transition: "background 0.2s",
          }}
        >
          <span style={{
            position: "absolute",
            top: 2,
            left: ttsEnabled ? 20 : 2,
            width: 16,
            height: 16,
            borderRadius: "50%",
            background: ttsEnabled ? "var(--black)" : "var(--muted)",
            transition: "left 0.2s",
          }} />
        </button>
      </div>
    </div>
  );
}
