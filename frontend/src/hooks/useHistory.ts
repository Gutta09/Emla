import { useCallback, useEffect, useState } from "react";
import type { SessionEntry } from "../types";
import { API_BASE } from "../config";

interface UseHistoryReturn {
  sessions: SessionEntry[];
  refresh: () => void;
  deleteSession: (id: string) => Promise<void>;
  clearAll: () => Promise<void>;
}

export function useHistory(): UseHistoryReturn {
  const [sessions, setSessions] = useState<SessionEntry[]>([]);

  const refresh = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/history`);
      const data = await res.json();
      setSessions(data.sessions ?? []);
    } catch {
      // backend may not be running yet
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const deleteSession = useCallback(async (id: string) => {
    await fetch(`${API_BASE}/history/${id}`, { method: "DELETE" });
    setSessions(prev => prev.filter(s => s.id !== id));
  }, []);

  const clearAll = useCallback(async () => {
    await fetch(`${API_BASE}/history`, { method: "DELETE" });
    setSessions([]);
  }, []);

  return { sessions, refresh, deleteSession, clearAll };
}
