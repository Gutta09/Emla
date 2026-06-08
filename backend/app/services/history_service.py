import json
import os
import uuid
from datetime import datetime, timezone

from app.schemas.api_schemas import SessionEntry

_sessions: list[SessionEntry] = []
_history_file = os.path.join(os.path.dirname(__file__), "..", "..", "session_history.json")


def _load_from_disk():
    if os.path.exists(_history_file):
        try:
            with open(_history_file) as f:
                data = json.load(f)
            _sessions.extend([SessionEntry(**s) for s in data])
        except Exception:
            pass


def _save_to_disk():
    try:
        with open(_history_file, "w") as f:
            json.dump([s.model_dump() for s in _sessions[-200:]], f, indent=2)
    except Exception:
        pass


_load_from_disk()


def add_session(signs: list[str], sentence: str, mode: str, start_ms: int, end_ms: int) -> SessionEntry:
    session = SessionEntry(
        id=str(uuid.uuid4()),
        timestamp=datetime.now(timezone.utc).isoformat(),
        start_ms=start_ms,
        end_ms=end_ms,
        signs=signs,
        sentence=sentence,
        mode=mode,
    )
    _sessions.append(session)
    _save_to_disk()
    return session


def get_all() -> list[SessionEntry]:
    return list(reversed(_sessions))


def delete_session(session_id: str) -> bool:
    for i, s in enumerate(_sessions):
        if s.id == session_id:
            _sessions.pop(i)
            _save_to_disk()
            return True
    return False


def clear_all():
    _sessions.clear()
    _save_to_disk()
