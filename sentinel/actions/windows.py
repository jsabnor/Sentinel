import logging

try:
    import pygetwindow as gw
    HAS_PYGETWINDOW = True
except ImportError:
    HAS_PYGETWINDOW = False

log = logging.getLogger("sentinel.actions.windows")


class WindowController:
    def __init__(self):
        if not HAS_PYGETWINDOW:
            log.warning("pygetwindow not installed. Window management limited.")

    def list_windows(self) -> str:
        if not HAS_PYGETWINDOW:
            return "pygetwindow not installed."

        try:
            windows = gw.getAllWindows()
            lines = []
            for w in windows:
                if w.title.strip():
                    status = []
                    if w.isMinimized:
                        status.append("minimized")
                    if w.isMaximized:
                        status.append("maximized")
                    if w.isActive:
                        status.append("ACTIVE")
                    s = ", ".join(status) if status else "normal"
                    lines.append(f"  [{s}] {w.title}")

            if not lines:
                return "No windows found."
            return f"Windows ({len(lines)}):\n" + "\n".join(lines)
        except Exception as e:
            return f"Error listing windows: {e}"

    def focus(self, title: str) -> str:
        if not HAS_PYGETWINDOW:
            return "pygetwindow not installed."

        try:
            windows = gw.getWindowsWithTitle(title)
            if not windows:
                return f"No window found matching '{title}'."

            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            return f"Focused window: {win.title}."
        except Exception as e:
            return f"Error focusing window: {e}"

    def minimize(self, title: str) -> str:
        if not HAS_PYGETWINDOW:
            return "pygetwindow not installed."

        try:
            windows = gw.getWindowsWithTitle(title)
            if not windows:
                return f"No window found matching '{title}'."

            win = windows[0]
            win.minimize()
            return f"Minimized window: {win.title}."
        except Exception as e:
            return f"Error minimizing window: {e}"

    def maximize(self, title: str) -> str:
        if not HAS_PYGETWINDOW:
            return "pygetwindow not installed."

        try:
            windows = gw.getWindowsWithTitle(title)
            if not windows:
                return f"No window found matching '{title}'."

            win = windows[0]
            win.maximize()
            return f"Maximized window: {win.title}."
        except Exception as e:
            return f"Error maximizing window: {e}"

    def close(self, title: str) -> str:
        if not HAS_PYGETWINDOW:
            return "pygetwindow not installed."

        try:
            windows = gw.getWindowsWithTitle(title)
            if not windows:
                return f"No window found matching '{title}'."

            win = windows[0]
            win.close()
            return f"Closed window: {win.title}."
        except Exception as e:
            return f"Error closing window: {e}"
