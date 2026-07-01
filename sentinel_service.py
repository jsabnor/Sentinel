#!/usr/bin/env python3
"""
Sentinel - Cross-Platform Background Service
=============================================
Runs Sentinel as a background service on Windows, Linux, and macOS.
Used by systemd (Linux), launchd (macOS), and Task Scheduler (Windows).

On Windows, use sentinelw.pyw to avoid a console window.
On Linux/macOS, this script is called directly by the service manager.

Usage:
    python sentinel_service.py          Run in background
    python sentinel_service.py --debug  Show console output
"""

import logging
import sys
import threading
import time

from sentinel.config import load_config
from sentinel.core import SentinelAgent


def _setup_logging(debug=False):
    handlers = []
    if debug:
        handlers.append(logging.StreamHandler())
    handlers.append(
        logging.FileHandler("sentinel_service.log", encoding="utf-8")
    )
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=handlers,
    )


def main():
    debug = "--debug" in sys.argv
    _setup_logging(debug=debug)
    log = logging.getLogger("sentinel.service")

    log.info("Starting Sentinel service on %s...", sys.platform)

    try:
        config = load_config("config.yaml")
    except Exception as e:
        log.error("Failed to load config: %s", e)
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

    quit_key = voice_cfg.get("quit_key", "ctrl+alt+q")
    log.info("Service running (%s mode). %s to quit.", activation, quit_key)

    try:
        import keyboard as kb
        kb.add_hotkey(quit_key.replace(" ", "").lower(), lambda: setattr(agent, "running", False))
    except ImportError:
        log.info("keyboard library not available. Use SIGTERM to stop.")

    time.sleep(1.5)
    if agent.tts:
        try:
            agent.tts.say("Sentinel iniciado")
        except Exception:
            pass

    try:
        while agent.running:
            time.sleep(1)
    except KeyboardInterrupt:
        log.info("Received interrupt.")

    agent.stop()
    log.info("Sentinel service stopped.")


if __name__ == "__main__":
    main()
