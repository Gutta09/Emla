import { NavLink, Outlet } from "react-router-dom";

const NAV = [
  { to: "/app/recognize", label: "Recognize", icon: "◉" },
  { to: "/app/practice", label: "Practice", icon: "⊕" },
  { to: "/app/dictionary", label: "Dictionary", icon: "⊞" },
  { to: "/app/history", label: "History", icon: "≡" },
];

export default function AppShell() {
  return (
    <div style={{ display: "flex", height: "100vh", background: "var(--black)" }}>
      {/* Sidebar */}
      <nav style={{
        width: 200,
        background: "var(--dark)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
        padding: "24px 0",
        flexShrink: 0,
      }}>
        {/* Logo */}
        <div style={{ padding: "0 20px 24px", borderBottom: "1px solid var(--border)", marginBottom: 12 }}>
          <div style={{ fontSize: 24, fontFamily: "Barlow Condensed, sans-serif", fontWeight: 700, color: "var(--gold)" }}>
            EMLA
          </div>
          <div style={{ fontSize: 10, color: "var(--muted)", letterSpacing: "0.1em", textTransform: "uppercase" }}>
            ASL Recognition
          </div>
        </div>

        {/* Nav links */}
        <div style={{ display: "flex", flexDirection: "column", gap: 2, padding: "0 8px" }}>
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: 12,
                padding: "10px 12px",
                borderRadius: "var(--radius)",
                fontSize: 14,
                fontWeight: isActive ? 600 : 400,
                color: isActive ? "var(--gold)" : "var(--muted)",
                background: isActive ? "rgba(201,168,76,0.1)" : "transparent",
                textDecoration: "none",
                transition: "all 0.15s",
              })}
            >
              <span style={{ fontSize: 16 }}>{icon}</span>
              {label}
            </NavLink>
          ))}
        </div>

        {/* Bottom info */}
        <div style={{ marginTop: "auto", padding: "16px 20px", borderTop: "1px solid var(--border)" }}>
          <div style={{ fontSize: 11, color: "var(--muted2)" }}>American Sign Language</div>
          <div style={{ fontSize: 10, color: "var(--muted2)", marginTop: 2 }}>MediaPipe + Transformer</div>
        </div>
      </nav>

      {/* Main content */}
      <main style={{ flex: 1, overflow: "auto", padding: 24 }}>
        <Outlet />
      </main>
    </div>
  );
}
