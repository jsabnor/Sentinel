import json
import logging
import time
from datetime import datetime
from pathlib import Path

log = logging.getLogger("sentinel.sessions")

DEFAULT_SESSION_NAME = "default"
SESSIONS_DIR = Path(__file__).parent.parent / "sessions"


class SessionManager:
    def __init__(self):
        SESSIONS_DIR.mkdir(exist_ok=True)
        self._current_name = datetime.now().strftime("%Y%m%d-%H%M%S")
        self._started_at = datetime.now().isoformat()

    @property
    def current_name(self):
        return self._current_name

    @property
    def started_at(self):
        return self._started_at

    def start_new(self, name: str = None):
        name = name or DEFAULT_SESSION_NAME
        self._current_name = name
        self._started_at = datetime.now().isoformat()
        log.info("Session started: %s", name)

    def save(self, conversation_history: list[dict]):
        if not conversation_history:
            return

        path = self._session_path()
        data = {
            "name": self._current_name,
            "started_at": self._started_at,
            "saved_at": datetime.now().isoformat(),
            "message_count": len(conversation_history),
            "messages": conversation_history,
        }
        try:
            path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            log.info("Session saved: %s (%d messages)", self._current_name, len(conversation_history))
        except Exception as e:
            log.error("Failed to save session: %s", e)

    def load(self, name: str = None) -> list[dict] | None:
        name = name or self._current_name
        path = self._session_path(name)
        if not path.exists():
            return None

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            self._current_name = data.get("name", name)
            self._started_at = data.get("started_at", self._started_at)
            messages = data.get("messages", [])
            log.info("Session loaded: %s (%d messages)", self._current_name, len(messages))
            return messages
        except Exception as e:
            log.error("Failed to load session: %s", e)
            return None

    def list_sessions(self) -> list[dict]:
        sessions = []
        if not SESSIONS_DIR.is_dir():
            return sessions
        for f in sorted(SESSIONS_DIR.glob("*.json"), reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                sessions.append({
                    "name": data.get("name", f.stem),
                    "file": f.stem,
                    "started_at": data.get("started_at", ""),
                    "saved_at": data.get("saved_at", ""),
                    "messages": data.get("message_count", 0),
                })
            except Exception:
                pass
        return sessions

    def delete(self, name: str):
        path = self._session_path(name)
        if path.exists():
            path.unlink()
            log.info("Session deleted: %s", name)

    def _session_path(self, name: str = None) -> Path:
        name = name or self._current_name
        safe = "".join(c for c in name if c.isalnum() or c in "_-")
        return SESSIONS_DIR / f"{safe}.json"
