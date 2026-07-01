import fnmatch
import logging
from pathlib import Path

log = logging.getLogger("sentinel.safety.sandbox")


class Sandbox:
    def __init__(self, sandbox_config: dict = None):
        config = sandbox_config or {}
        self.enabled = config.get("enabled", False)
        self.allowed_paths = config.get("allowed_paths", [])
        self.allowed_commands = config.get("allowed_commands", [])

    def is_command_allowed(self, command: str) -> bool:
        if not self.enabled:
            return True

        if not self.allowed_commands:
            return True

        for pattern in self.allowed_commands:
            if fnmatch.fnmatch(command, pattern):
                return True

        log.warning("Command blocked by sandbox: %s", command)
        return False

    def is_path_allowed(self, path: str) -> bool:
        if not self.enabled:
            return True

        if not self.allowed_paths:
            return True

        try:
            resolved = str(Path(path).resolve())
        except Exception:
            resolved = path

        for pattern in self.allowed_paths:
            try:
                allowed = str(Path(pattern).resolve())
            except Exception:
                allowed = pattern
            if resolved.startswith(allowed):
                return True

        log.warning("Path blocked by sandbox: %s", path)
        return False
