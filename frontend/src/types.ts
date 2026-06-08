export interface Landmark {
  x: number;
  y: number;
  z: number;
}

export interface LandmarkFrame {
  pose: Landmark[];
  left_hand: Landmark[] | null;
  right_hand: Landmark[] | null;
}

export interface TopKItem {
  sign: string;
  confidence: number;
}

export interface Prediction {
  type: "prediction";
  frame_id: number;
  sign: string;
  confidence: number;
  mode: string;
  top3: TopKItem[];
  uncertain: boolean;
}

export interface WordCommitted {
  type: "word_committed";
  sign: string;
  confidence: number;
}

export interface ReadyMessage {
  type: "ready";
  vocabulary_size: number;
  models_loaded: string[];
}

export type WsMessage = Prediction | WordCommitted | ReadyMessage | { type: "error"; message: string };

export interface SignInfo {
  id: string;
  label: string;
  category: string;
  type: "static" | "dynamic";
  description?: string;
  handshape?: string;
}

export interface SessionEntry {
  id: string;
  timestamp: string;
  start_ms: number;
  end_ms: number;
  signs: string[];
  sentence: string;
  mode: string;
}

export type RecognizeMode = "word" | "fingerspell";
export type AppMode = "recognize" | "practice" | "dictionary" | "history";
