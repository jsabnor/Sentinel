import logging

import numpy as np

log = logging.getLogger("sentinel.voice.stt")

try:
    import sounddevice as sd
    HAS_SD = True
except ImportError:
    HAS_SD = False

try:
    import whisper
    import warnings
    warnings.filterwarnings("ignore")
    import os as _os
    _os.environ["TQDM_DISABLE"] = "1"
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False


class SpeechToText:
    def __init__(self, voice_config: dict = None):
        self.config = voice_config or {}
        stt_config = self.config.get("stt", {})

        self.language = stt_config.get("language", "es")
        self.model_name = stt_config.get("model", "base")
        self.energy_threshold = stt_config.get("energy_threshold", 800)
        self.pause_threshold = stt_config.get("pause_threshold", 1.5)

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
        self._model = None

        if not HAS_WHISPER:
            log.warning("openai-whisper not installed. Voice input disabled.")
        if not HAS_SD:
            log.warning("sounddevice not installed. Voice input disabled.")

    def _get_model(self):
        if self._model is None and HAS_WHISPER:
            try:
                self._model = whisper.load_model(self.model_name)
            except Exception as e:
                log.error("Failed to load whisper model '%s': %s", self.model_name, e)
        return self._model

    def close_stream(self):
        pass

    def listen(self, timeout: float = None, phrase_time_limit: float = 10) -> str:
        if not HAS_SD or not HAS_WHISPER:
            return ""

        model = self._get_model()
        if model is None:
            return ""

        try:
            duration = min(timeout, phrase_time_limit) if timeout else phrase_time_limit
            n_samples = int(duration * self.sample_rate)

            audio = sd.rec(n_samples, samplerate=self.sample_rate, channels=1, dtype="int16")
            sd.wait()

            energy = np.sqrt(np.mean(audio.astype(np.float64) ** 2))
            if energy < 200:
                return ""

            audio_float = audio.astype(np.float32).flatten() / 32768.0
            audio_float = self._resample_16k(audio_float, self.sample_rate)
            result = model.transcribe(audio_float, language=self.language, fp16=False)
            return result.get("text", "").strip()

        except Exception as e:
            log.error("STT error: %s", e)
            return ""

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

    @staticmethod
    def _resolve_device(device):
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
