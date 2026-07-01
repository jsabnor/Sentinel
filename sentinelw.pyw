"""
Sentinel - Background Mode (no console)
========================================
Double-click or run: pythonw sentinelw.pyw

Shows a status indicator top-right. Hold F9 to speak, release to send.
Press Ctrl+Alt+Q to quit. Voice responses play through speakers.
"""

import logging
import os
import sys
import threading
import time

if sys.executable.endswith("pythonw.exe"):
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")

from sentinel.config import load_config
from sentinel.core import SentinelAgent


def _setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler("sentinel_service.log", encoding="utf-8"),
        ],
    )


def _pump_messages():
    try:
        import ctypes
        user32 = ctypes.windll.user32
        msg = ctypes.create_string_buffer(256)
        while user32.PeekMessageA(ctypes.byref(msg), 0, 0, 0, 1):
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageA(ctypes.byref(msg))
    except Exception:
        pass


def main():
    _setup_logging()
    log = logging.getLogger("sentinel.background")

    try:
        config = load_config("config.yaml")
    except Exception as e:
        log.error("Config error: %s", e)
        sys.exit(1)

    voice_cfg = config.get("voice", {})
    activation = voice_cfg.get("activation", "pushtotalk")

    agent = SentinelAgent(config, voice_enabled=True)

    def run():
        try:
            if activation == "wakeword":
                agent._run_wakeword()
            elif activation == "always":
                agent._run_always()
            else:
                agent._run_pushtotalk()
        except Exception as e:
            log.error("Agent error: %s", e)
        finally:
            agent.stop()

    agent_thread = threading.Thread(target=run, daemon=True)
    agent_thread.start()
    time.sleep(1)

    try:
        import keyboard as kb
        kb.add_hotkey("ctrl+alt+q", lambda: setattr(agent, "running", False))
    except ImportError:
        log.info("keyboard not available for quit hotkey.")

    if agent.tts:
        try:
            agent.tts.say("Sentinel iniciado")
        except Exception:
            pass

    log.info("Sentinel running in background (%s mode).", activation)

    try:
        while agent.running:
            _pump_messages()
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    agent.stop()
    log.info("Sentinel stopped.")


if __name__ == "__main__":
    main()
