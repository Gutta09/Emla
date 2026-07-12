import { useCallback, useEffect, useRef, useState } from "react";
import type { LandmarkFrame, Prediction, RecognizeMode } from "../types";
import { useWebSocket } from "./useWebSocket";
import { SEQUENCE_LENGTH } from "../config";

interface UseRecognitionReturn {
  connected: boolean;
  modelsLoaded: string[];
  vocabularySize: number;
  prediction: Prediction | null;
  sentence: string[];
  mode: RecognizeMode;
  frameBuffer: LandmarkFrame[];
  setMode: (m: RecognizeMode) => void;
  onFrame: (frame: LandmarkFrame) => void;
  clearSentence: () => void;
}

export function useRecognition(): UseRecognitionReturn {
  const { connected, modelsLoaded, vocabularySize, prediction, committedWord, sendLandmarks, sendClear, sendModeChange } = useWebSocket();

  const [sentence, setSentence] = useState<string[]>([]);
  const [mode, setModeState] = useState<RecognizeMode>("fingerspell");
  const [frameBuffer, setFrameBuffer] = useState<LandmarkFrame[]>([]);
  const frameIdRef = useRef(0);
  const frameThrottleRef = useRef(0);
  const frameBufferRef = useRef<LandmarkFrame[]>([]);

  useEffect(() => {
    if (committedWord && committedWord.sign !== "?" && committedWord.sign !== "—") {
      setSentence(prev => [...prev, committedWord.sign]);
    }
  }, [committedWord]);

  const setMode = useCallback((m: RecognizeMode) => {
    setModeState(m);
    sendModeChange(m);
    setSentence([]);
    frameBufferRef.current = [];
    setFrameBuffer([]);
  }, [sendModeChange]);

  const onFrame = useCallback((frame: LandmarkFrame) => {
    frameThrottleRef.current++;
    if (frameThrottleRef.current % 2 !== 0) return;
    frameIdRef.current++;

    // Keep a rolling buffer of recent frames for feedback submission
    frameBufferRef.current = [...frameBufferRef.current.slice(-(SEQUENCE_LENGTH - 1)), frame];
    setFrameBuffer([...frameBufferRef.current]);

    sendLandmarks(frame, mode, frameIdRef.current);
  }, [sendLandmarks, mode]);

  const clearSentence = useCallback(() => {
    setSentence([]);
    sendClear();
  }, [sendClear]);

  return { connected, modelsLoaded, vocabularySize, prediction, sentence, mode, frameBuffer, setMode, onFrame, clearSentence };
}
