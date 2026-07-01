import base64
import io
import logging
import time
from pathlib import Path

try:
    import pyautogui
    HAS_PYAUTOGUI = True
except ImportError:
    HAS_PYAUTOGUI = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

log = logging.getLogger("sentinel.actions.desktop")


class DesktopController:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.mouse_speed = self.config.get("mouse_speed", 0.3)
        self.pause = self.config.get("pause_between_actions", 0.1)
        self.screenshot_quality = self.config.get("screenshot_quality", 80)

        if not HAS_PYAUTOGUI:
            log.warning("pyautogui not installed. Desktop control limited.")
        else:
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = self.pause

    def screenshot(self, save: bool = True) -> str:
        if not HAS_PYAUTOGUI or not HAS_PIL:
            return "Desktop control dependencies not installed (pyautogui, pillow)."

        try:
            img = pyautogui.screenshot()
            if save:
                path = Path("sentinel_screenshots")
                path.mkdir(exist_ok=True)
                timestamp = int(time.time())
                filepath = path / f"screenshot_{timestamp}.png"
                img.save(filepath, quality=self.screenshot_quality)
                return f"Screenshot saved to {filepath}. Resolution: {img.size}"

            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            return f"Screenshot taken. Resolution: {img.size}. Base64 length: {len(img_str)}"
        except Exception as e:
            return f"Error taking screenshot: {e}"

    def click(self, x: int, y: int, button: str = "left"):
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            pyautogui.click(x, y, button=button)
            return f"Clicked {button} at ({x}, {y})."
        except Exception as e:
            return f"Error clicking: {e}"

    def type_text(self, text: str, interval: float = 0.05):
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            pyautogui.typewrite(text, interval=interval)
            return f"Typed {len(text)} characters."
        except Exception as e:
            return f"Error typing: {e}"

    def move_mouse(self, x: int, y: int):
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            pyautogui.moveTo(x, y, duration=self.mouse_speed)
            return f"Moved mouse to ({x}, {y})."
        except Exception as e:
            return f"Error moving mouse: {e}"

    def press_key(self, key: str):
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            pyautogui.press(key)
            return f"Pressed key: {key}."
        except Exception as e:
            return f"Error pressing key: {e}"

    def hotkey(self, keys: list[str]):
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            pyautogui.hotkey(*keys)
            return f"Pressed hotkey: {'+'.join(keys)}."
        except Exception as e:
            return f"Error pressing hotkey: {e}"

    def scroll(self, amount: int):
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            pyautogui.scroll(amount)
            direction = "up" if amount > 0 else "down"
            return f"Scrolled {direction} {abs(amount)} clicks."
        except Exception as e:
            return f"Error scrolling: {e}"

    def get_position(self) -> str:
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            x, y = pyautogui.position()
            return f"Mouse at ({x}, {y})."
        except Exception as e:
            return f"Error getting position: {e}"

    def get_screen_size(self) -> str:
        if not HAS_PYAUTOGUI:
            return "pyautogui not installed."

        try:
            w, h = pyautogui.size()
            return f"Screen resolution: {w}x{h}."
        except Exception as e:
            return f"Error getting screen size: {e}"
