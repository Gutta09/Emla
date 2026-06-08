import { useCallback, useEffect, useRef, useState } from "react";
import type { LandmarkFrame, Landmark } from "../types";

// Holistic-style connections for skeleton drawing
const POSE_CONNECTIONS: [number, number][] = [
  [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
  [11, 23], [12, 24], [23, 24], [23, 25], [24, 26],
  [25, 27], [26, 28],
];
const HAND_CONNECTIONS: [number, number][] = [
  [0,1],[1,2],[2,3],[3,4],[0,5],[5,6],[6,7],[7,8],
  [0,9],[9,10],[10,11],[11,12],[0,13],[13,14],[14,15],[15,16],
  [0,17],[17,18],[18,19],[19,20],[5,9],[9,13],[13,17],
];

interface UseMediaPipeReturn {
  isReady: boolean;
  isDetecting: boolean;
  lastFrame: LandmarkFrame | null;
  startCamera: () => void;
  stopCamera: () => void;
}

export function useMediaPipe(
  videoRef: React.RefObject<HTMLVideoElement | null>,
  canvasRef: React.RefObject<HTMLCanvasElement | null>
): UseMediaPipeReturn {
  const [isReady, setIsReady] = useState(false);
  const [isDetecting, setIsDetecting] = useState(false);
  const [lastFrame, setLastFrame] = useState<LandmarkFrame | null>(null);

  const handLandmarkerRef = useRef<any>(null);
  const poseLandmarkerRef = useRef<any>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const rafRef = useRef<number | null>(null);
  const runningRef = useRef(false);

  useEffect(() => {
    let cancelled = false;

    async function init() {
      try {
        const vision = await import("@mediapipe/tasks-vision");
        const { FilesetResolver, HandLandmarker, PoseLandmarker } = vision;

        const filesetResolver = await FilesetResolver.forVisionTasks(
          "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.14/wasm"
        );

        const [handLandmarker, poseLandmarker] = await Promise.all([
          HandLandmarker.createFromOptions(filesetResolver, {
            baseOptions: {
              modelAssetPath:
                "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task",
              delegate: "GPU",
            },
            runningMode: "VIDEO",
            numHands: 2,
          }),
          PoseLandmarker.createFromOptions(filesetResolver, {
            baseOptions: {
              modelAssetPath:
                "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
              delegate: "GPU",
            },
            runningMode: "VIDEO",
            numPoses: 1,
          }),
        ]);

        if (!cancelled) {
          handLandmarkerRef.current = handLandmarker;
          poseLandmarkerRef.current = poseLandmarker;
          setIsReady(true);
        }
      } catch (err) {
        console.error("[useMediaPipe] init error:", err);
      }
    }

    init();
    return () => { cancelled = true; };
  }, []);

  const drawSkeleton = useCallback((frame: LandmarkFrame, width: number, height: number, ctx: CanvasRenderingContext2D) => {
    ctx.clearRect(0, 0, width, height);

    const toXY = (lm: Landmark) => ({ x: lm.x * width, y: lm.y * height });

    // Pose connections
    ctx.strokeStyle = "rgba(201,168,76,0.55)";
    ctx.lineWidth = 2;
    for (const [a, b] of POSE_CONNECTIONS) {
      if (frame.pose[a] && frame.pose[b]) {
        const p1 = toXY(frame.pose[a]);
        const p2 = toXY(frame.pose[b]);
        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.stroke();
      }
    }

    // Pose dots
    ctx.fillStyle = "rgba(201,168,76,0.8)";
    for (const lm of frame.pose) {
      const { x, y } = toXY(lm);
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
    }

    // Hands
    for (const [hand, color] of [[frame.left_hand, "rgba(212,135,78,0.9)"], [frame.right_hand, "rgba(255,255,255,0.8)"]] as [Landmark[] | null, string][]) {
      if (!hand) continue;
      ctx.strokeStyle = color;
      ctx.lineWidth = 1.5;
      for (const [a, b] of HAND_CONNECTIONS) {
        if (hand[a] && hand[b]) {
          const p1 = toXY(hand[a]);
          const p2 = toXY(hand[b]);
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.stroke();
        }
      }
      ctx.fillStyle = color;
      for (const lm of hand) {
        const { x, y } = toXY(lm);
        ctx.beginPath();
        ctx.arc(x, y, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }, []);

  const startCamera = useCallback(async () => {
    if (runningRef.current) return;
    runningRef.current = true;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480, facingMode: "user" } });
      streamRef.current = stream;

      const video = videoRef.current!;
      video.srcObject = stream;
      await video.play();
      setIsDetecting(true);

      const detect = async () => {
        if (!runningRef.current) return;
        const video = videoRef.current;
        const canvas = canvasRef.current;
        if (!video || !canvas || !handLandmarkerRef.current || !poseLandmarkerRef.current) {
          rafRef.current = requestAnimationFrame(detect);
          return;
        }

        const ts = performance.now();
        const handResult = handLandmarkerRef.current.detectForVideo(video, ts);
        const poseResult = poseLandmarkerRef.current.detectForVideo(video, ts);

        const pose: Landmark[] = poseResult.landmarks?.[0]?.map((lm: any) => ({ x: lm.x, y: lm.y, z: lm.z })) ?? [];
        let leftHand: Landmark[] | null = null;
        let rightHand: Landmark[] | null = null;

        for (let i = 0; i < (handResult.handednesses?.length ?? 0); i++) {
          const side = handResult.handednesses[i]?.[0]?.categoryName?.toLowerCase();
          const landmarks: Landmark[] = handResult.landmarks[i].map((lm: any) => ({ x: lm.x, y: lm.y, z: lm.z }));
          if (side === "left") leftHand = landmarks;
          else rightHand = landmarks;
        }

        if (pose.length > 0) {
          const frame: LandmarkFrame = { pose, left_hand: leftHand, right_hand: rightHand };
          setLastFrame(frame);

          const ctx = canvas.getContext("2d")!;
          canvas.width = video.videoWidth || 640;
          canvas.height = video.videoHeight || 480;
          drawSkeleton(frame, canvas.width, canvas.height, ctx);
        }

        rafRef.current = requestAnimationFrame(detect);
      };

      rafRef.current = requestAnimationFrame(detect);
    } catch (err) {
      console.error("[useMediaPipe] camera error:", err);
      runningRef.current = false;
    }
  }, [videoRef, canvasRef, drawSkeleton]);

  const stopCamera = useCallback(() => {
    runningRef.current = false;
    if (rafRef.current) cancelAnimationFrame(rafRef.current);
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop());
      streamRef.current = null;
    }
    setIsDetecting(false);
    setLastFrame(null);
    if (canvasRef.current) {
      const ctx = canvasRef.current.getContext("2d");
      ctx?.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    }
  }, [canvasRef]);

  useEffect(() => () => stopCamera(), [stopCamera]);

  return { isReady, isDetecting, lastFrame, startCamera, stopCamera };
}
