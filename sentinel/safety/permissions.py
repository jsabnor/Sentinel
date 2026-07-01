import fnmatch
import logging
import re

log = logging.getLogger("sentinel.safety.permissions")


class PermissionManager:
    def __init__(self, safety_config: dict = None):
        config = safety_config or {}
        self._default_mode = config.get("default_mode", "ask")
        self._permissions = config.get("permissions", {})
        self._high_risk_patterns = config.get("high_risk_patterns", [])

    @property
    def default_mode(self) -> str:
        return self._default_mode

    def set_default_mode(self, mode: str):
        if mode in ("ask", "auto", "deny"):
            self._default_mode = mode
            log.info("Default permission mode set to: %s", mode)

    def set_mode_for(self, action_type: str, mode: str):
        if mode not in ("ask", "auto", "deny"):
            return
        perm = self._permissions.get(action_type)
        if isinstance(perm, dict):
            perm["mode"] = mode
        else:
            self._permissions[action_type] = {"mode": mode}
        log.info("Permission for %s set to: %s", action_type, mode)

    def get_mode(self, action_type: str) -> str:
        perm = self._permissions.get(action_type, {})
        if isinstance(perm, dict):
            return perm.get("mode", self._default_mode)
        return self._default_mode

    def needs_approval(self, action_type: str, detail: str = "") -> bool:
        mode = self.get_mode(action_type)
        if mode == "auto":
            return False
        return True

    def is_blocked(self, action_type: str, detail: str = "") -> bool:
        mode = self.get_mode(action_type)
        if mode == "deny":
            return True

        perm = self._permissions.get(action_type, {})
        if not isinstance(perm, dict):
            return False

        if action_type == "terminal":
            blocked = perm.get("blocked_commands", [])
            for pattern in blocked:
                if fnmatch.fnmatch(detail.lower(), pattern.lower()):
                    log.warning("Blocked terminal command: %s (matched: %s)", detail, pattern)
                    return True

        elif action_type == "files":
            blocked = perm.get("blocked_paths", [])
            for pattern in blocked:
                if fnmatch.fnmatch(detail.lower(), pattern.lower()):
                    log.warning("Blocked file path: %s (matched: %s)", detail, pattern)
                    return True

        elif action_type == "processes":
            blocked = perm.get("blocked_processes", [])
            for pattern in blocked:
                if fnmatch.fnmatch(detail.lower(), pattern.lower()):
                    log.warning("Blocked process: %s (matched: %s)", detail, pattern)
                    return True

        if self._high_risk_patterns:
            detail_lower = detail.lower()
            for pattern in self._high_risk_patterns:
                if re.search(rf"\b{re.escape(pattern.lower())}\b", detail_lower):
                    log.warning("High-risk pattern detected: %s in '%s'", pattern, detail)
                    return True

        return False
