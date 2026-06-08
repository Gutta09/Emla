import { useEffect, useState } from "react";
import SignCard from "../components/SignCard";
import type { SignInfo } from "../types";
import { API_BASE } from "../config";

export default function Dictionary() {
  const [signs, setSigns] = useState<SignInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | "static" | "dynamic">("all");
  const [selected, setSelected] = useState<SignInfo | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/vocabulary`)
      .then(r => r.json())
      .then(data => { setSigns(data.signs ?? []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const filtered = signs.filter(s => {
    const matchesQuery = s.label.toLowerCase().includes(query.toLowerCase()) || (s.description ?? "").toLowerCase().includes(query.toLowerCase());
    const matchesFilter = filter === "all" || s.type === filter;
    return matchesQuery && matchesFilter;
  });

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto" }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 28, marginBottom: 4 }}>Sign Dictionary</h1>
        <p style={{ fontSize: 13, color: "var(--muted)" }}>
          Browse all {signs.length} supported signs. Click a sign for details.
        </p>
      </div>

      {/* Search + filter */}
      <div style={{ display: "flex", gap: 12, marginBottom: 24, flexWrap: "wrap" }}>
        <input
          type="text"
          placeholder="Search signs…"
          value={query}
          onChange={e => setQuery(e.target.value)}
          style={{ flex: 1, minWidth: 200 }}
        />
        <div style={{ display: "flex", gap: 6 }}>
          {(["all", "static", "dynamic"] as const).map(f => (
            <button
              key={f}
              className={`btn ${filter === f ? "btn-primary" : "btn-ghost"}`}
              style={{ padding: "8px 14px", fontSize: 13, textTransform: "capitalize" }}
              onClick={() => setFilter(f)}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: "40px 0", color: "var(--muted)" }} className="animate-pulse">
          Loading vocabulary…
        </div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: "center", padding: "40px 0", color: "var(--muted)" }}>
          No signs match "{query}"
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
          {filtered.map(sign => (
            <SignCard key={sign.id} sign={sign} onClick={() => setSelected(sign)} />
          ))}
        </div>
      )}

      {/* Detail modal */}
      {selected && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.75)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
          onClick={() => setSelected(null)}
        >
          <div className="card animate-slide-up" style={{ width: 380, display: "flex", flexDirection: "column", gap: 16 }} onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <div style={{ fontSize: 48, fontFamily: "Barlow Condensed, sans-serif", fontWeight: 700, color: "var(--gold2)", lineHeight: 1 }}>
                  {selected.label}
                </div>
                <div style={{ fontSize: 12, color: "var(--muted)", marginTop: 4, textTransform: "capitalize" }}>
                  {selected.type} · {selected.category}
                </div>
              </div>
              <button className="btn btn-ghost" style={{ padding: "4px 10px", fontSize: 18 }} onClick={() => setSelected(null)}>×</button>
            </div>

            {selected.description && (
              <div>
                <div style={{ fontSize: 11, color: "var(--muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>How to sign</div>
                <p style={{ fontSize: 14, color: "var(--text2)", lineHeight: 1.6 }}>{selected.description}</p>
              </div>
            )}

            {selected.handshape && (
              <div style={{ display: "flex", gap: 16 }}>
                <div>
                  <div style={{ fontSize: 11, color: "var(--muted)", marginBottom: 4 }}>Handshape</div>
                  <span className="badge badge-gold">{selected.handshape}</span>
                </div>
              </div>
            )}

            <button
              className="btn btn-secondary"
              style={{ justifyContent: "center", marginTop: 4 }}
              onClick={() => setSelected(null)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
