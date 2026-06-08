import type { SignInfo } from "../types";

interface SignCardProps {
  sign: SignInfo;
  onClick?: () => void;
}

export default function SignCard({ sign, onClick }: SignCardProps) {
  const isStatic = sign.type === "static";

  return (
    <div
      onClick={onClick}
      style={{
        background: "var(--dark2)",
        border: "1px solid var(--border)",
        borderRadius: "var(--radius-lg)",
        padding: "16px",
        cursor: onClick ? "pointer" : "default",
        transition: "border-color 0.15s, transform 0.1s",
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
      onMouseEnter={e => { if (onClick) { (e.currentTarget as HTMLElement).style.borderColor = "var(--gold)"; } }}
      onMouseLeave={e => { (e.currentTarget as HTMLElement).style.borderColor = "var(--border)"; }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{
          fontSize: 28,
          fontFamily: "Barlow Condensed, sans-serif",
          fontWeight: 700,
          color: "var(--gold2)",
          lineHeight: 1,
        }}>
          {sign.label}
        </div>
        <span className={`badge ${isStatic ? "badge-muted" : "badge-gold"}`} style={{ fontSize: 10 }}>
          {isStatic ? "Static" : "Dynamic"}
        </span>
      </div>

      {sign.description && (
        <div style={{ fontSize: 12, color: "var(--muted)", lineHeight: 1.4 }}>
          {sign.description}
        </div>
      )}

      {sign.handshape && (
        <div style={{ fontSize: 11, color: "var(--muted2)" }}>
          Handshape: <span style={{ color: "var(--text2)" }}>{sign.handshape}</span>
        </div>
      )}
    </div>
  );
}
