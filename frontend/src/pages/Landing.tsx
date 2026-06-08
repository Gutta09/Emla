import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={{
      minHeight: "100vh",
      background: "var(--black)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      padding: "40px 20px",
      position: "relative",
      overflow: "hidden",
    }}>
      {/* Background glow */}
      <div style={{
        position: "absolute",
        top: "20%",
        left: "50%",
        transform: "translateX(-50%)",
        width: 600,
        height: 600,
        background: "radial-gradient(circle, rgba(201,168,76,0.06) 0%, transparent 70%)",
        pointerEvents: "none",
      }} />

      <div style={{ textAlign: "center", maxWidth: 640, position: "relative", zIndex: 1 }} className="animate-fade-in">
        {/* Logo mark */}
        <div style={{ marginBottom: 24 }}>
          <div style={{
            display: "inline-flex",
            width: 64,
            height: 64,
            background: "linear-gradient(135deg, var(--gold), var(--amber))",
            borderRadius: 16,
            alignItems: "center",
            justifyContent: "center",
            fontSize: 28,
            fontFamily: "Barlow Condensed, sans-serif",
            fontWeight: 700,
            color: "var(--black)",
          }}>
            E
          </div>
        </div>

        <h1 style={{ fontSize: 64, color: "var(--text)", lineHeight: 1, marginBottom: 8 }}>EMLA</h1>
        <p style={{ fontSize: 20, color: "var(--gold)", fontFamily: "Barlow Condensed, sans-serif", marginBottom: 20, letterSpacing: "0.1em" }}>
          SIGN LANGUAGE RECOGNITION
        </p>
        <p style={{ fontSize: 16, color: "var(--muted)", lineHeight: 1.7, marginBottom: 40, maxWidth: 480, margin: "0 auto 40px" }}>
          Real-time ASL recognition powered by MediaPipe and deep learning.
          Translate signs to English, practice your alphabet, and bridge the communication gap.
        </p>

        <button
          className="btn btn-primary"
          style={{ fontSize: 16, padding: "14px 36px", borderRadius: 10 }}
          onClick={() => navigate("/app/recognize")}
        >
          Start Recognizing →
        </button>

        <div style={{ display: "flex", gap: 32, justifyContent: "center", marginTop: 60 }}>
          {[
            { label: "A-Z Fingerspelling", desc: "Static hand shapes" },
            { label: "100+ Word Signs", desc: "Dynamic ASL vocabulary" },
            { label: "Claude Translation", desc: "Natural English output" },
          ].map(f => (
            <div key={f.label} style={{ textAlign: "center" }}>
              <div style={{ fontSize: 14, color: "var(--gold)", fontWeight: 600, marginBottom: 4 }}>{f.label}</div>
              <div style={{ fontSize: 12, color: "var(--muted)" }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
