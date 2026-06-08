import { useEffect, useRef } from "react";
import { useMediaPipe } from "../hooks/useMediaPipe";
import type { LandmarkFrame } from "../types";

interface WebcamCanvasProps {
  onFrame?: (frame: LandmarkFrame) => void;
  active: boolean;
}

export default function WebcamCanvas({ onFrame, active }: WebcamCanvasProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const { isReady, isDetecting, lastFrame, startCamera, stopCamera } = useMediaPipe(videoRef, canvasRef);

  useEffect(() => {
    if (active && isReady) {
      startCamera();
    } else if (!active) {
      stopCamera();
    }
  }, [active, isReady, startCamera, stopCamera]);

  useEffect(() => {
    if (lastFrame && onFrame) {
      onFrame(lastFrame);
    }
  }, [lastFrame, onFrame]);

  return (
    <div style={{ position: "relative", width: "100%", aspectRatio: "4/3", background: "var(--dark3)", borderRadius: "var(--radius-lg)", overflow: "hidden" }}>
      <video
        ref={videoRef}
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", transform: "scaleX(-1)" }}
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", transform: "scaleX(-1)" }}
      />

      {/* Status overlay */}
      <div style={{ position: "absolute", top: 12, left: 12, display: "flex", flexDirection: "column", gap: 6 }}>
        {!isReady && (
          <div style={{
            background: "rgba(8,8,8,0.8)",
            border: "1px solid var(--border)",
            borderRadius: 6,
            padding: "4px 10px",
            fontSize: 12,
            color: "var(--amber)",
          }} className="animate-pulse">
            Loading MediaPipe…
          </div>
        )}
        {isDetecting && (
          <div style={{
            background: "rgba(8,8,8,0.8)",
            border: "1px solid rgba(61,220,132,0.3)",
            borderRadius: 6,
            padding: "4px 10px",
            fontSize: 12,
            color: "var(--green)",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "var(--green)", display: "inline-block" }} className="animate-pulse" />
            Detecting
          </div>
        )}
      </div>

      {/* Start prompt */}
      {active && !isDetecting && isReady && (
        <div style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "var(--muted)",
          fontSize: 14,
          background: "rgba(8,8,8,0.5)",
        }}>
          Starting camera…
        </div>
      )}
    </div>
  );
}
