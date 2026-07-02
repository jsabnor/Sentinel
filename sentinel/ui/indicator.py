import logging
import threading
import tkinter as tk

log = logging.getLogger("sentinel.ui.indicator")

_LABELS = {
    "es": {
        "sleep":      "En espera",
        "listening":  "Escuchando",
        "processing": "Procesando",
        "speaking":   "Respondiendo",
    },
    "en": {
        "sleep":      "Waiting",
        "listening":  "Listening",
        "processing": "Processing",
        "speaking":   "Speaking",
    },
}

STATES = {
    "hidden":     {"color": "#232323", "alpha": 0.18},
    "listening":  {"color": "#ff2222", "alpha": 0.92},
    "processing": {"color": "#ffaa00", "alpha": 0.92},
    "speaking":   {"color": "#00aaff", "alpha": 0.85},
    "sleep":      {"color": "#555555", "alpha": 0.25},
}


class StatusIndicator:
    def __init__(self, language: str = "es", size: int = 18,
                 margin_x: int = 10, margin_y: int = 10):
        self._size = size
        self._margin_x = margin_x
        self._margin_y = margin_y
        self._labels = _LABELS.get(language, _LABELS["en"])
        self._state = "hidden"
        self._running = False
        self._window = None
        self._canvas = None
        self._circle = None
        self._status_text = None
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._tk_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        self.set_state("hidden")
        if self._window:
            try:
                self._window.after(0, self._window.destroy)
            except Exception:
                pass

    def set_state(self, state: str):
        if state not in STATES:
            state = "hidden"
        self._state = state

    def set_tokens(self, label: str):
        if label != getattr(self, "_tokens_label", ""):
            self._tokens_flash = 8
        self._tokens_label = label

    @property
    def state(self):
        return self._state

    def _tk_loop(self):
        try:
            self._window = tk.Tk()
            self._window.title("Sentinel")
            self._window.overrideredirect(True)
            self._window.attributes("-topmost", True)
            self._window.configure(bg="black")
            self._window.wm_attributes("-transparentcolor", "black")

            radio = self._size / 2
            pad = 6
            w = int(radio * 2 + 160 + pad * 3)
            h = int(radio * 2 + pad * 2)

            self._canvas = tk.Canvas(
                self._window, width=w, height=h,
                bg="black", highlightthickness=0, bd=0,
            )
            self._canvas.pack()

            cx = pad + radio
            cy = pad + radio

            self._circle = self._canvas.create_oval(
                pad, pad, pad + int(radio * 2), pad + int(radio * 2),
                fill=STATES["sleep"]["color"], outline="",
            )

            self._status_text = self._canvas.create_text(
                pad + radio * 2 + 10, cy,
                text="", fill="#888888",
                font=("Segoe UI", 10, "bold"),
                anchor="w",
            )

            self._tokens_text = self._canvas.create_text(
                pad + radio * 2 + 115, cy,
                text="", fill="#00cc44",
                font=("Segoe UI", 9, "bold"),
                anchor="e",
            )

            self._position_window()

        except Exception as e:
            log.debug("Indicator window not available: %s", e)
            return

        last_state = None
        pulse_phase = 0

        while self._running:
            try:
                current_state = self._state

                if current_state != last_state:
                    info = STATES.get(current_state, STATES["sleep"])
                    color = info["color"]
                    alpha = info["alpha"]
                    label = self._labels.get(current_state, "")

                    if current_state == "hidden":
                        self._canvas.itemconfig(self._circle, fill="#232323")
                        self._canvas.itemconfig(self._status_text, text="", fill="#555555")
                        self._canvas.itemconfig(self._tokens_text, text="")
                        self._window.attributes("-alpha", 0.18)
                    elif current_state == "listening":
                        self._canvas.itemconfig(self._circle, fill=color)
                        self._canvas.itemconfig(self._status_text, text="REC " + label, fill=color)
                        self._window.attributes("-alpha", alpha)
                    else:
                        self._canvas.itemconfig(self._circle, fill=color)
                        self._canvas.itemconfig(self._status_text, text=label, fill=color)
                        self._window.attributes("-alpha", alpha)

                    last_state = current_state

                tokens_label = getattr(self, "_tokens_label", "")
                flash = getattr(self, "_tokens_flash", 0)
                if flash > 0:
                    self._tokens_flash = flash - 1
                    color = "#ff2222" if flash > 3 else "#00cc44"
                else:
                    color = "#00cc44"
                self._canvas.itemconfig(self._tokens_text, text=tokens_label, fill=color)

                if current_state == "listening":
                    import math
                    pulse_phase = (pulse_phase + 0.1) % (2 * math.pi)
                    pulse = (math.sin(pulse_phase) + 1) / 2
                    self._window.attributes("-alpha", 0.65 + pulse * 0.3)

                elif current_state == "processing":
                    import math
                    pulse_phase = (pulse_phase + 0.08) % (2 * math.pi)
                    pulse = (math.sin(pulse_phase * 2) + 1) / 2
                    self._window.attributes("-alpha", 0.6 + pulse * 0.3)

                self._window.update()
                self._window.after(40)

            except Exception:
                break

    def _position_window(self):
        if not self._window:
            return
        screen_w = self._window.winfo_screenwidth()
        radio = self._size / 2
        w = int(radio * 2 + 160 + 18)
        h = int(radio * 2 + 12)
        x = screen_w - w - self._margin_x
        y = self._margin_y
        self._window.geometry(f"{w}x{h}+{x}+{y}")
