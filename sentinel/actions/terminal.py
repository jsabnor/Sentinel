import logging
import subprocess
import sys

log = logging.getLogger("sentinel.actions.terminal")


class TerminalController:
    def __init__(self, sandbox_config: dict = None):
        self.sandbox_config = sandbox_config or {}
        self.max_timeout = self.sandbox_config.get("max_command_timeout", 60)
        self._last_output = ""

    def execute(self, command: str, timeout: int = 30) -> str:
        timeout = min(timeout, self.max_timeout)
        log.info("Executing: %s", command)

        is_launch = self._is_launch_command(command)
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

        try:
            if is_launch:
                return self._execute_launch(command)

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
                creationflags=creationflags,
            )
            output = result.stdout.strip()
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr.strip()}"
            if not output:
                output = f"Command completed with exit code {result.returncode}"

            self._last_output = output
            return output

        except subprocess.TimeoutExpired:
            return f"Command timed out after {timeout}s: {command}"
        except Exception as e:
            return f"Error executing command: {e}"

    def _is_launch_command(self, command: str) -> bool:
        cmd_lower = command.lower().strip()

        if "start " in cmd_lower and not any(x in cmd_lower for x in (
            "where ", "dir ", "if exist", "echo ", "cmd.exe", "type ",
            "find ", "findstr", "tasklist", "taskkill", "net ", "sc ",
        )):
            return True

        if ".exe" in cmd_lower and cmd_lower.endswith('.exe"'):
            return True

        if '"' in command and command.strip().endswith('.exe"'):
            return True

        return False

    def _execute_launch(self, command: str) -> str:
        try:
            cmd_stripped = command.strip()

            if "://" in cmd_stripped and not cmd_stripped.lower().startswith("start "):
                cmd_stripped = f'explorer "{cmd_stripped.strip(chr(34))}"'
            elif cmd_stripped.lower().startswith("start ") and "://" in cmd_stripped:
                url = cmd_stripped.split('"')[1] if '"' in cmd_stripped else ""
                if url:
                    cmd_stripped = f'explorer "{url}"'
                else:
                    pass
            elif cmd_stripped.lower().startswith("start "):
                pass
            elif cmd_stripped.startswith('"') and ".exe" in cmd_stripped.lower():
                cmd_stripped = f'start "" {cmd_stripped}'
            else:
                cmd_stripped = f'start "" {cmd_stripped}'

            creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0

            proc = subprocess.Popen(
                cmd_stripped,
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL,
                close_fds=True,
                creationflags=creationflags,
            )

            return f"Launched (PID {proc.pid}): {command[:80]}"

        except Exception as e:
            return f"Error launching: {e}"

    def get_last_output(self) -> str:
        return self._last_output or "No output available."
