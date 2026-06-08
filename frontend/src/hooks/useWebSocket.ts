import { useCallback, useEffect, useRef, useState } from "react";
import type { LandmarkFrame, Prediction, WordCommitted, WsMessage } from "../types";
import { WS_URL } from "../config";

interface UseWebSocketReturn {
  connected: boolean;
  modelsLoaded: string[];
  vocabularySize: number;
  prediction: Prediction | null;
  committedWord: WordCommitted | null;
  sendLandmarks: (frame: LandmarkFrame, mode: string, frameId: number) => void;
  sendClear: () => void;
  sendModeChange: (mode: string) => void;
}

export function useWebSocket(): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const retryDelay = useRef(500);

  const [connected, setConnected] = useState(false);
  const [modelsLoaded, setModelsLoaded] = useState<string[]>([]);
  const [vocabularySize, setVocabularySize] = useState(0);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [committedWord, setCommittedWord] = useState<WordCommitted | null>(null);

  const connect = useCallback(() => {
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const url = `${protocol}://${window.location.host}${WS_URL}`;
    const ws = new WebSocket(url);

    ws.onopen = () => {
      setConnected(true);
      retryDelay.current = 500;
    };

    ws.onclose = () => {
      setConnected(false);
      wsRef.current = null;
      retryRef.current = setTimeout(() => {
        retryDelay.current = Math.min(retryDelay.current * 2, 8000);
        connect();
      }, retryDelay.current);
    };

    ws.onerror = () => ws.close();

    ws.onmessage = (event) => {
      try {
        const msg: WsMessage = JSON.parse(event.data);
        if (msg.type === "ready") {
          setModelsLoaded(msg.models_loaded);
          setVocabularySize(msg.vocabulary_size);
        } else if (msg.type === "prediction") {
          setPrediction(msg as Prediction);
        } else if (msg.type === "word_committed") {
          setCommittedWord(msg as WordCommitted);
          setTimeout(() => setCommittedWord(null), 100);
        }
      } catch {
        // malformed message — ignore
      }
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    return () => {
      retryRef.current && clearTimeout(retryRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const sendLandmarks = useCallback((frame: LandmarkFrame, mode: string, frameId: number) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: "landmarks",
        frame_id: frameId,
        mode,
        payload: {
          pose: frame.pose,
          left_hand: frame.left_hand,
          right_hand: frame.right_hand,
        },
      }));
    }
  }, []);

  const sendClear = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "clear" }));
    }
  }, []);

  const sendModeChange = useCallback((mode: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "mode_change", mode }));
    }
  }, []);

  return { connected, modelsLoaded, vocabularySize, prediction, committedWord, sendLandmarks, sendClear, sendModeChange };
}
