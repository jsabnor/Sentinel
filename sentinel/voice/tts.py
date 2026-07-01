import logging
import os

log = logging.getLogger("sentinel.voice.tts")

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except ImportError:
    HAS_PYTTSX3 = False

try:
    from piper.voice import PiperVoice
    HAS_PIPER = True
except ImportError:
    HAS_PIPER = False

try:
    import sounddevice as sd
    import numpy as np
    HAS_AUDIO_PLAYBACK = True
except ImportError:
    HAS_AUDIO_PLAYBACK = False


class TextToSpeech:
    def __init__(self, voice_config: dict = None):
        self.config = voice_config or {}
        tts_config = self.config.get("tts", {})

        self.engine_name = tts_config.get("engine", "pyttsx3")
        self.rate = tts_config.get("rate", 180)
        self.volume = tts_config.get("volume", 0.9)

        self._engine = None
        self._piper_voice = None
        self._piper_sample_rate = 22050
        self._output_device = self._resolve_output_device(
            self.config.get("output_device")
        )

        if self.engine_name == "pyttsx3" and HAS_PYTTSX3:
            self._init_pyttsx3()
        elif self.engine_name == "edge":
            self._init_edge()
        elif self.engine_name == "piper":
            self._init_piper()

    def _resolve_output_device(self, device):
        if device is None:
            return None
        if isinstance(device, int):
            return device
        try:
            import sounddevice as sd
            device_str = str(device).lower()
            devices = sd.query_devices()
            for i, d in enumerate(devices):
                if d["max_output_channels"] > 0 and device_str in d["name"].lower():
                    return i
        except Exception:
            pass
        return None

    def _init_pyttsx3(self):
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            self._engine.setProperty("volume", self.volume)

            voices = self._engine.getProperty("voices")
            if voices:
                preferred = self.config.get("tts", {}).get("voice", "default")
                if preferred != "default":
                    for v in voices:
                        if preferred.lower() in v.name.lower():
                            self._engine.setProperty("voice", v.id)
                            break
        except Exception as e:
            log.warning("TTS initialization failed: %s", e)
            self._engine = None

    def _init_edge(self):
        self._engine = "edge"

    def _init_piper(self):
        if not HAS_PIPER:
            log.warning("piper-tts not installed. Install: pip install piper-tts")
            return

        piper_config = self.config.get("tts", {}).get("piper", {})
        model_path = piper_config.get("model_path", "")
        config_path = piper_config.get("config_path", None)

        if not model_path:
            log.warning("Piper model_path not configured in config.yaml → voice → tts → piper")
            return

        if not os.path.exists(model_path):
            log.warning("Piper model not found: %s", model_path)
            return

        try:
            self._piper_voice = PiperVoice.load(model_path, config_path=config_path)
            self._piper_sample_rate = self._piper_voice.config.sample_rate
            self._engine = "piper"
            log.info("Piper TTS initialized: %s (sample_rate=%s)", os.path.basename(model_path), self._piper_sample_rate)
        except Exception as e:
            log.warning("Piper initialization failed: %s", e)

    def say(self, text: str):
        if not text:
            return

        if self._engine and self.engine_name == "pyttsx3" and HAS_PYTTSX3:
            try:
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                log.error("TTS error: %s", e)
        elif self._engine == "edge":
            self._say_edge(text)
        elif self._engine == "piper":
            self._say_piper(text)
        else:
            log.debug("TTS not available, text only.")

    def _say_piper(self, text: str):
        if not self._piper_voice:
            log.warning("Piper voice not initialized.")
            return

        if not HAS_AUDIO_PLAYBACK:
            log.warning("sounddevice/numpy not installed. Cannot play Piper audio.")
            return

        try:
            result = self._piper_voice.synthesize(text)
            if hasattr(result, "__iter__") and not isinstance(result, (bytes, bytearray)):
                audio_bytes = b"".join(chunk.audio_int16_bytes for chunk in result)
            elif hasattr(result, "audio_int16_bytes"):
                audio_bytes = result.audio_int16_bytes
            else:
                audio_bytes = result

            samples = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            output_sr = self._get_output_sample_rate()

            if output_sr and output_sr != self._piper_sample_rate:
                duration = len(samples) / self._piper_sample_rate
                new_len = int(duration * output_sr)
                indices = np.linspace(0, len(samples) - 1, new_len)
                samples = np.interp(indices, np.arange(len(samples)), samples).astype(np.float32)
                play_sr = output_sr
            else:
                play_sr = self._piper_sample_rate

            sd.play(samples, samplerate=play_sr, device=self._output_device)
            sd.wait()
        except Exception as e:
            log.error("Piper TTS error: %s", e)

    def _get_output_sample_rate(self):
        try:
            if self._output_device is not None:
                info = sd.query_devices(self._output_device)
                return int(info.get("default_samplerate", 0))
        except Exception:
            pass
        return 0

    def _say_edge(self, text: str):
        try:
            import subprocess
            import sys

            if sys.platform == "win32":
                escaped = text.replace('"', '`"')
                ps_script = (
                    f'Add-Type -AssemblyName System.Speech; '
                    f'$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; '
                    f'$s.Speak("{escaped}")'
                )
                subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                    capture_output=True,
                    timeout=30,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
        except Exception as e:
            log.error("Edge TTS error: %s", e)
