"""Audio cues for accessibility feedback."""

import ctypes
import logging
import sys
import threading

log = logging.getLogger("sentinel.ui.sounds")

_user32 = ctypes.windll.user32 if sys.platform == "win32" else None

MB_OK = 0x00
MB_ICONASTERISK = 0x40
MB_ICONHAND = 0x10


def _beep(icon_type=MB_OK):
    if _user32:
        try:
            _user32.MessageBeep(icon_type)
        except Exception as e:
            log.debug("Beep error: %s", e)


def play_listen_start():
    threading.Thread(target=lambda: _beep(MB_ICONASTERISK), daemon=True).start()


def play_task_done():
    def _chime():
        _beep(MB_ICONASTERISK)
        import time
        time.sleep(0.1)
        _beep(MB_ICONASTERISK)
    threading.Thread(target=_chime, daemon=True).start()


def play_error():
    threading.Thread(target=lambda: _beep(MB_ICONHAND), daemon=True).start()
