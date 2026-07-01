import logging
import threading
import time

import numpy as np

log = logging.getLogger("sentinel.voice.wakeword")

try:
    import sounddevice as sd
    HAS_SD = True
except ImportError:
    HAS_SD = False

try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False


class WakeWordDetector:
    def __init__(self, voice_config: dict = None):
        self.config = voice_config or {}
        wake_words = self.config.get("wake_words", ["sentinel"])
        self.wake_words = [w.lower() for w in wake_words]
        self.is_awake = not wake_words
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self._last_awake_time = 0

        stt_config = self.config.get("stt", {})
        self.language = stt_config.get("language", "es")
        self._model_name = self.config.get("wakeword_model", "tiny")
        self._model = None

        self._input_device = self._resolve_device(
            self.config.get("input_device")
        )
        self._output_device = self._resolve_device(
            self.config.get("output_device")
        )

        if self._input_device is not None or self._output_device is not None:
            try:
                sd.default.device = [self._input_device, self._output_device]
            except Exception:
                pass

        self.sample_rate = self._detect_sample_rate()

        if not HAS_SD or not HAS_WHISPER:
            log.warning("sounddevice/whisper not installed. Wake word disabled.")
            self.is_awake = True

    def _get_model(self):
        if self._model is None and HAS_WHISPER:
            try:
                self._model = whisper.load_model(self._model_name)
                log.info("Wakeword model loaded: whisper-%s", self._model_name)
            except Exception as e:
                log.error("Failed to load wakeword model: %s", e)
        return self._model

    def start(self):
        if not self.wake_words or self.is_awake:
            return

        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        log.info("Wake word detection started (whisper-%s). Listening for: %s", self._model_name, self.wake_words)

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def sleep(self):
        with self._lock:
            self.is_awake = False
        log.info("Sleeping. Waiting for wake word...")

    def awake(self):
        with self._lock:
            self.is_awake = True
            self._last_awake_time = time.time()

    def touch(self):
        self._last_awake_time = time.time()

    def _detect_sample_rate(self):
        try:
            device = sd.default.device[0]
            if device is not None and device >= 0:
                info = sd.query_devices(device)
                return int(info.get("default_samplerate", 16000))
        except Exception:
            pass
        return 16000

    @staticmethod
    def _resample_16k(audio, orig_sr):
        if orig_sr == 16000:
            return audio
        target_sr = 16000
        duration = len(audio) / orig_sr
        new_len = int(duration * target_sr)
        indices = np.linspace(0, len(audio) - 1, new_len)
        return np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)

    def _resolve_device(self, device):
        if device is None:
            return None
        if isinstance(device, int):
            return device
        try:
            device_str = str(device).lower()
            devices = sd.query_devices()
            for i, d in enumerate(devices):
                if d["max_input_channels"] > 0 and device_str in d["name"].lower():
                    return i
        except Exception:
            pass
        return None

    def poll(self):
        if not self.is_awake:
            return False
        if self._last_awake_time and time.time() - self._last_awake_time > 30:
            self.sleep()
            return False
        return True

    def _listen_loop(self):
        duration = 2.0
        n_samples = int(duration * self.sample_rate)

        model = self._get_model()
        if model is None:
            return

        while self._running:
            if self.is_awake:
                time.sleep(0.2)
                continue

            try:
                audio = sd.rec(n_samples, samplerate=self.sample_rate, channels=1, dtype="int16")
                sd.wait()

                if audio.max() == 0 and audio.min() == 0:
                    continue

                energy = np.sqrt(np.mean(audio.astype(np.float64) ** 2))
                if energy < 200:
                    continue

                audio_float = audio.astype(np.float32).flatten() / 32768.0
                audio_float = self._resample_16k(audio_float, self.sample_rate)
                result = model.transcribe(audio_float, language=self.language, fp16=False)
                text = result.get("text", "").lower().strip()

                if not text:
                    continue

                log.debug("Wake word check: %s (energy=%d)", text, int(energy))
                for ww in self.wake_words:
                    if ww in text:
                        log.info("Wake word detected: %s", ww)
                        with self._lock:
                            self.is_awake = True
                            self._last_awake_time = time.time()
                        time.sleep(1)
                        break

            except Exception as e:
                log.debug("Wakeword error (retrying): %s", e)
                time.sleep(1)
