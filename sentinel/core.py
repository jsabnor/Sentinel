import logging
import time

import numpy as np

from sentinel.agent.llm import LLMEngine
from sentinel.actions.terminal import TerminalController
from sentinel.actions.desktop import DesktopController
from sentinel.actions.files import FileController
from sentinel.actions.processes import ProcessController
from sentinel.actions.windows import WindowController
from sentinel.safety.permissions import PermissionManager
from sentinel.safety.sandbox import Sandbox
from sentinel.voice.stt import SpeechToText
from sentinel.voice.tts import TextToSpeech
from sentinel.voice.wakeword import WakeWordDetector
from sentinel.ui.indicator import StatusIndicator
from sentinel.sessions import SessionManager
from sentinel.ui.sounds import play_listen_start, play_task_done

log = logging.getLogger("sentinel")


_TOOL_HANDLERS: dict[str, callable] = {}


def _register(name):
    def decorator(fn):
        _TOOL_HANDLERS[name] = fn
        return fn
    return decorator


class SentinelAgent:
    def __init__(self, config: dict, voice_enabled: bool = True):
        self.config = config
        self.voice_enabled = voice_enabled
        self.running = False
        self.conversation_history: list[dict] = []

        self.session = SessionManager()
        self.session.start_new()
        self._total_tokens = 0

        self.llm = LLMEngine(config.get("llm", {}))
        self.terminal = TerminalController(config.get("sandbox", {}))
        self.desktop = DesktopController(config.get("desktop", {}))
        self.files = FileController(config.get("sandbox", {}))
        self.processes = ProcessController()
        self.windows = WindowController()
        self.permissions = PermissionManager(config.get("safety", {}))
        self.sandbox = Sandbox(config.get("sandbox", {}))
        stt_config = config.get("voice", {}).get("stt", {})
        self.indicator = StatusIndicator(language=stt_config.get("language", "es"))

        if self.voice_enabled:
            self.stt = SpeechToText(config.get("voice", {}))
            self.tts = TextToSpeech(config.get("voice", {}))
            self.wakeword = WakeWordDetector(config.get("voice", {}))
            voice_cfg = config.get("voice", {})
            self._activation = voice_cfg.get("activation", "wakeword")
            self._ptt_key = voice_cfg.get("push_to_talk_key", "ctrl+alt+s")
            self._profile = voice_cfg.get("profile", "standard")
            self._conv_timeout = voice_cfg.get("conversation_timeout", 0)
            self._max_history = voice_cfg.get("max_history", 4)
            self._max_tool_calls = voice_cfg.get("max_tool_calls", 6)
        else:
            self.stt = None
            self.tts = None
            self.wakeword = None
            self._activation = "always"
            self._ptt_key = None
            self._conv_timeout = 0
            self._max_history = 4
            self._max_tool_calls = 6

        self._register_tools()

    def _register_tools(self):
        @_register("terminal_execute")
        def terminal_execute(command: str, timeout: int = 30):
            if not self.sandbox.is_command_allowed(command):
                return "Command blocked by sandbox policy."
            if self.permissions.is_blocked("terminal", command):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("terminal", command):
                approved = self._request_approval(f"Execute: {command}")
                if not approved:
                    return "User denied terminal execution."
            if "start " in command.lower() or "cmd /c start" in command.lower():
                timeout = min(timeout, 5)
            return self.terminal.execute(command, timeout=timeout)

        @_register("terminal_output")
        def terminal_output():
            return self.terminal.get_last_output()

        @_register("desktop_screenshot")
        def desktop_screenshot():
            if self.permissions.is_blocked("desktop", "screenshot"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("desktop", "screenshot"):
                approved = self._request_approval("Take screenshot?")
                if not approved:
                    return "User denied screenshot."
            return self.desktop.screenshot()

        @_register("desktop_read_screen")
        def desktop_read_screen():
            return self.desktop.read_screen()

        @_register("desktop_click")
        def desktop_click(x: int, y: int, button: str = "left"):
            if self.permissions.is_blocked("desktop", f"click at ({x},{y})"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("desktop", f"click at ({x},{y})"):
                approved = self._request_approval(f"Click at ({x}, {y})?")
                if not approved:
                    return "User denied click action."
            return self.desktop.click(x, y, button)

        @_register("desktop_type")
        def desktop_type(text: str, interval: float = 0.05):
            if self.permissions.is_blocked("desktop", f"type: {text[:50]}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("desktop", f"type: {text[:50]}"):
                approved = self._request_approval(f"Type: '{text[:80]}'?")
                if not approved:
                    return "User denied typing action."
            return self.desktop.type_text(text, interval)

        @_register("desktop_move_mouse")
        def desktop_move_mouse(x: int, y: int):
            return self.desktop.move_mouse(x, y)

        @_register("desktop_press_key")
        def desktop_press_key(key: str):
            if self.permissions.is_blocked("desktop", f"press: {key}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("desktop", f"press: {key}"):
                approved = self._request_approval(f"Press key: {key}?")
                if not approved:
                    return "User denied key press."
            return self.desktop.press_key(key)

        @_register("desktop_hotkey")
        def desktop_hotkey(keys: list[str]):
            combo = "+".join(keys)
            if self.permissions.is_blocked("desktop", f"hotkey: {combo}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("desktop", f"hotkey: {combo}"):
                approved = self._request_approval(f"Press hotkey: {combo}?")
                if not approved:
                    return "User denied hotkey."
            return self.desktop.hotkey(keys)

        @_register("file_read")
        def file_read(path: str, lines: int = 200):
            if not self.sandbox.is_path_allowed(path):
                return f"Access to {path} blocked by sandbox."
            if self.permissions.is_blocked("files", f"read: {path}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("files", f"read: {path}"):
                approved = self._request_approval(f"Read file: {path}?")
                if not approved:
                    return "User denied file read."
            return self.files.read(path, lines)

        @_register("file_write")
        def file_write(path: str, content: str):
            if not self.sandbox.is_path_allowed(path):
                return f"Access to {path} blocked by sandbox."
            if self.permissions.is_blocked("files", f"write: {path}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("files", f"write: {path}"):
                approved = self._request_approval(f"Write to file: {path}?")
                if not approved:
                    return "User denied file write."
            return self.files.write(path, content)

        @_register("file_list")
        def file_list(path: str = "."):
            if self.permissions.is_blocked("files", f"list: {path}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("files", f"list: {path}"):
                approved = self._request_approval(f"List directory: {path}?")
                if not approved:
                    return "User denied directory listing."
            return self.files.list_dir(path)

        @_register("file_delete")
        def file_delete(path: str):
            if not self.sandbox.is_path_allowed(path):
                return f"Access to {path} blocked by sandbox."
            if self.permissions.is_blocked("files", f"delete: {path}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("files", f"delete: {path}"):
                approved = self._request_approval(f"DELETE file: {path}? [HIGH RISK]")
                if not approved:
                    return "User denied file deletion."
            return self.files.delete(path)

        @_register("process_list")
        def process_list():
            return self.processes.list_processes()

        @_register("process_kill")
        def process_kill(pid: int = None, name: str = None):
            target = str(pid) if pid else name
            if self.permissions.is_blocked("processes", f"kill: {target}"):
                return "Action blocked by safety policy."
            if self.permissions.needs_approval("processes", f"kill: {target}"):
                approved = self._request_approval(f"Kill process: {target}?")
                if not approved:
                    return "User denied process kill."
            return self.processes.kill(pid=pid, name=name)

        @_register("system_info")
        def system_info():
            return self.processes.system_info()

        @_register("window_list")
        def window_list():
            return self.windows.list_windows()

        @_register("window_focus")
        def window_focus(title: str):
            return self.windows.focus(title)

        @_register("window_minimize")
        def window_minimize(title: str):
            return self.windows.minimize(title)

        @_register("session_list")
        def session_list(limit: int = 5):
            sessions = self.session.list_sessions()
            if not sessions:
                return "No saved sessions found."
            shown = sessions[:limit]
            lines = [f"{len(sessions)} saved sessions. Showing {len(shown)}:"]
            for i, s in enumerate(shown, 1):
                date = s["saved_at"][:16].replace("T", " ")
                lines.append(f"  {i}. {s['name']} - {s['messages']} messages - {date}")
            if len(sessions) > limit:
                lines.append(f"  ... and {len(sessions) - limit} more. Ask for more if needed.")
            return "\n".join(lines)

        @_register("session_load")
        def session_load(name: str):
            messages = self.session.load(name)
            if messages is None:
                sessions = self.session.list_sessions()
                names = [s["name"] for s in sessions[:5]]
                return f"Session '{name}' not found. Available: {', '.join(names)}"
            self.conversation_history = messages
            return f"Session '{name}' restored with {len(messages)} messages."

    def run_chat(self):
        self.running = True
        print("Sentinel chat mode. Type /exit to quit, /voice to speak.")
        print(f"Provider: {self.llm.provider_type} | Model: {self.llm.model}")
        print(f"Permission mode: {self.permissions.default_mode}")

        while self.running:
            try:
                user_input = input("\n> ").strip()
                if not user_input:
                    continue

                if user_input.startswith("/"):
                    self._handle_command(user_input[1:])
                    continue

                response = self._process(user_input)
                self._speak(response)

            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                log.exception("Error in agent loop")

    def run_voice(self):
        self.running = True

        if self._activation == "pushtotalk":
            return self._run_pushtotalk()
        elif self._activation == "always":
            return self._run_always()
        else:
            return self._run_wakeword()

    def _run_wakeword(self):
        self.running = True
        print("Sentinel voice mode (wake word). Listening...")
        print(f"  Say '{', '.join(self.wakeword.wake_words)}' to activate.")

        self.indicator.start()
        self.indicator.set_state("sleep")
        self.wakeword.start()

        idle_count = 0

        while self.running:
            try:
                if not self.wakeword.is_awake:
                    self.wakeword.poll()
                    self.indicator.set_state("sleep")
                    time.sleep(0.1)
                    continue

                self.indicator.set_state("listening")
                text = self.stt.listen(timeout=5, phrase_time_limit=10)
                self.wakeword.touch()

                if not text:
                    idle_count += 1
                    if idle_count >= 3:
                        self._speak("Modo espera.")
                        self.wakeword.sleep()
                        self.indicator.set_state("sleep")
                        idle_count = 0
                    continue

                idle_count = 0
                try:
                    print(f"  [Heard] {text}")
                except Exception:
                    pass

                if text.lower() in ("salir", "exit", "apagar", "shutdown", "stop sentinel"):
                    self._speak("Apagando Sentinel. Hasta luego.")
                    break

                if self._is_sleep_command(text):
                    self.indicator.set_state("speaking")
                    self._speak("Hasta luego.")
                    self.wakeword.sleep()
                    self.indicator.set_state("sleep")
                    continue

                self.indicator.set_state("processing")
                response = self._process(text)
                self.indicator.set_state("speaking")
                self._speak(response)

                if self.tts:
                    time.sleep(0.5)

                self.wakeword.sleep()

            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                log.exception("Error in agent loop")

    def _run_pushtotalk(self):
        self.running = True

        try:
            import keyboard as kb
        except ImportError:
            print("Push-to-talk requires: pip install keyboard")
            print("Falling back to always-listening mode.")
            return self._run_always()

        import numpy as np
        try:
            import sounddevice as sd
        except ImportError:
            print("Push-to-talk requires sounddevice.")
            return

        ptt_combo = self._ptt_key.strip().lower()
        print(f"Sentinel voice mode (push-to-talk). Hold {self._ptt_key} to speak, release to send.")

        import sounddevice as _sd
        try:
            dev = _sd.query_devices(_sd.default.device[0])
            print(f"Mic: {dev['name']} @ {int(dev['default_samplerate'])}Hz")
        except Exception:
            pass

        self.indicator.start()
        self.indicator.set_state("sleep")

        sr = self.stt.sample_rate
        max_duration = 15

        while self.running:
            try:
                self.indicator.set_state("sleep")
                if not kb.is_pressed(ptt_combo):
                    time.sleep(0.1)
                    continue

                self.indicator.set_state("listening")
                play_listen_start()
                time.sleep(0.3)  # Let wakeword release the mic
                print("  [Recording...] release to send", end="", flush=True)

                full_audio = sd.rec(int(max_duration * sr), samplerate=sr, channels=1, dtype="int16")

                start_time = time.time()
                released_time = max_duration

                while kb.is_pressed(ptt_combo):
                    elapsed = time.time() - start_time
                    if elapsed >= max_duration:
                        break
                    time.sleep(0.05)
                else:
                    released_time = time.time() - start_time

                sd.stop()
                print(f" ({released_time:.1f}s)")

                actual_samples = min(
                    int(released_time * sr) + sr // 10,
                    len(full_audio)
                )
                audio = full_audio[:actual_samples]
                audio_float = audio.astype(np.float32).flatten() / 32768.0
                audio_float = self._resample(audio_float, sr)

                energy = np.sqrt(np.mean(audio.astype(np.float64) ** 2))
                if energy < 100 or released_time < 0.5:
                    print(f"  [Too short / silent] energy={int(energy)}")
                    continue

                self.indicator.set_state("processing")
                model = self.stt._get_model()
                if model is None:
                    continue

                result = model.transcribe(audio_float, language=self.stt.language, fp16=False)
                text = result.get("text", "").strip()

                if not text:
                    print(f"  [No speech detected] energy={int(energy)}")
                    continue

                if text.lower() in ("salir", "exit", "apagar", "shutdown", "stop sentinel"):
                    self.indicator.set_state("speaking")
                    self._speak("Apagando Sentinel. Hasta luego.")
                    break

                if self._is_sleep_command(text):
                    self.indicator.set_state("speaking")
                    self._speak("Hasta luego.")
                    continue

                response = self._process(text)
                self.indicator.set_state("speaking")
                play_task_done()
                self._speak(response)

                if self.tts:
                    time.sleep(0.5)

                if self._conv_timeout > 0:
                    self.indicator.set_state("listening")
                    time.sleep(0.3)
                    followup = self.stt.listen(timeout=self._conv_timeout, phrase_time_limit=6)
                    if followup and followup.strip():
                        print(f"  [Followup] {followup}")
                        text = followup
                        self.indicator.set_state("processing")
                        response = self._process(text)
                        self.indicator.set_state("speaking")
                        play_task_done()
                        self._speak(response)
                        if self.tts:
                            time.sleep(0.5)

            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                log.exception("Error in agent loop")

    def _run_always(self):
        self.running = True
        print("Sentinel voice mode (always listening). Say 'salir' to quit.")

        self.indicator.start()
        self.indicator.set_state("sleep")

        if self.wakeword:
            self.wakeword.is_awake = True

        idle_count = 0

        while self.running:
            try:
                self.indicator.set_state("listening")
                text = self.stt.listen(timeout=5, phrase_time_limit=10)

                if not text:
                    idle_count += 1
                    self.indicator.set_state("sleep")
                    if idle_count >= 6:
                        print("  [Idle - still listening...]")
                        idle_count = 0
                    continue

                idle_count = 0
                try:
                    print(f"  [Heard] {text}")
                except Exception:
                    pass

                if text.lower() in ("salir", "exit", "apagar", "shutdown", "stop sentinel"):
                    self.indicator.set_state("speaking")
                    self._speak("Apagando Sentinel. Hasta luego.")
                    break

                if self._is_sleep_command(text):
                    self.indicator.set_state("speaking")
                    self._speak("Hasta luego.")
                    continue

                self.indicator.set_state("processing")
                response = self._process(text)
                self.indicator.set_state("speaking")
                self._speak(response)

                if self.tts:
                    time.sleep(0.5)

            except (EOFError, KeyboardInterrupt):
                break
            except Exception:
                log.exception("Error in agent loop")

    def _process(self, text: str):
        log.info("User: %s", text)
        self.conversation_history.append({"role": "user", "content": text})

        try:
            return self._process_with_tools()
        except Exception as e:
            error_msg = str(e)
            log.error("LLM error: %s", error_msg)

            if "400" in error_msg or "context" in error_msg.lower() or "token" in error_msg.lower():
                self.conversation_history = self.conversation_history[-4:]
                try:
                    return self._process_with_tools()
                except Exception:
                    pass

            self.conversation_history = self.conversation_history[-2:]
            return "Lo siento, ha ocurrido un error. He reiniciado la conversacion. Puedes repetir tu ultima peticion?"

    def _process_with_tools(self):
        self._trim_history(max_messages=self._max_history)
        response = self.llm.chat(self.conversation_history, tools=self._get_tool_definitions(), profile=self._profile)
        self._count_tokens(response)

        tool_iterations = 0
        max_iterations = self._max_tool_calls
        last_content = ""

        while response.get("tool_calls"):
            if tool_iterations >= max_iterations:
                log.warning("Max tool iterations (%d), forcing response", max_iterations)
                if last_content:
                    response = {"role": "assistant", "content": last_content}
                else:
                    response = {"role": "assistant", "content": "He encontrado informacion pero necesito que seas mas especifico. Puedes concretar que necesitas?"}
                break

            tool_iterations += 1
            if response.get("content"):
                last_content = response["content"]

            tool_results = []
            for call in response["tool_calls"]:
                func = call.get("function", call)
                name = func.get("name", call.get("name", ""))
                args = func.get("arguments", call.get("arguments", {}))
                if isinstance(args, str):
                    import json
                    try:
                        args = json.loads(args)
                    except Exception:
                        args = {}
                handler = _TOOL_HANDLERS.get(name)
                if handler:
                    result = handler(**args)
                    result_str = str(result)
                    if len(result_str) > 5000:
                        half = 2500
                        result_str = result_str[:half] + f"\n[... {len(result_str) - 2*half} chars omitted ...]\n" + result_str[-half:]
                    tool_results.append({
                        "name": name,
                        "result": result_str,
                        "call_id": call.get("id", "call"),
                    })
                    try:
                        print(f"  [{name}] {str(result)[:120]}")
                    except Exception:
                        pass

            self.conversation_history.append(response)
            for tr in tool_results:
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tr.get("call_id", "call"),
                    "content": tr["result"],
                })

            response = self.llm.chat(self.conversation_history, tools=self._get_tool_definitions(), profile=self._profile)
            self._count_tokens(response)

        reply = response.get("content", "")
        self.conversation_history.append({"role": "assistant", "content": reply})
        self._trim_history()
        log.info("Sentinel: %s", reply)
        return reply

    def _count_tokens(self, response):
        try:
            content = response.get("content", "")
            self._total_tokens += max(len(content) // 4, 1)
            tokens_str = self._total_tokens
            if tokens_str >= 1000:
                label = f"{tokens_str/1000:.1f}K" if tokens_str < 10000 else f"{tokens_str//1000}K"
            else:
                label = str(tokens_str)
            self.indicator.set_tokens(label)
        except Exception:
            pass

    def _trim_history(self, max_messages: int = None):
        if len(self.conversation_history) <= max_messages:
            return

        for i in range(len(self.conversation_history) - max_messages, len(self.conversation_history)):
            if self.conversation_history[i]["role"] == "user":
                self.conversation_history = self.conversation_history[i:]
                return

        self.conversation_history = self.conversation_history[-max_messages:]

    def _get_tool_definitions(self):
        return [
            {
                "type": "function",
                "function": {
                    "name": "terminal_execute",
                    "description": "Execute a shell command. For launching apps, use 'start \"AppName\" \"path\"' with timeout=5. The command runs synchronously and returns output.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "The shell command to execute"},
                            "timeout": {"type": "integer", "description": "Timeout in seconds (use 5 for app launching, default 30)", "default": 30},
                        },
                        "required": ["command"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "desktop_screenshot",
                    "description": "Take a screenshot of the current desktop",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "desktop_read_screen",
                    "description": "Analyze what's currently on screen. Use with window_list to understand context.",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "desktop_click",
                    "description": "Click at screen coordinates",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "integer", "description": "X coordinate"},
                            "y": {"type": "integer", "description": "Y coordinate"},
                            "button": {"type": "string", "enum": ["left", "right", "middle"], "default": "left"},
                        },
                        "required": ["x", "y"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "desktop_type",
                    "description": "Type text using the keyboard",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to type"},
                            "interval": {"type": "number", "description": "Seconds between keystrokes", "default": 0.05},
                        },
                        "required": ["text"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "desktop_press_key",
                    "description": "Press a single keyboard key",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string", "description": "Key name (enter, esc, tab, backspace, etc.)"},
                        },
                        "required": ["key"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "desktop_hotkey",
                    "description": "Press a key combination like ctrl+c",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keys": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Keys to press together (e.g. ['ctrl', 'c'])",
                            },
                        },
                        "required": ["keys"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "file_read",
                    "description": "Read the contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"},
                            "lines": {"type": "integer", "description": "Max lines to return", "default": 200},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "file_write",
                    "description": "Write content to a file (creates or overwrites)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"},
                            "content": {"type": "string", "description": "Content to write"},
                        },
                        "required": ["path", "content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "file_list",
                    "description": "List files and directories in a path",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Directory path", "default": "."},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "file_delete",
                    "description": "Delete a file or empty directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to delete"},
                        },
                        "required": ["path"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "process_list",
                    "description": "List all running processes with PID, name, CPU, and memory usage",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "process_kill",
                    "description": "Kill a process by PID or name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pid": {"type": "integer", "description": "Process ID to kill"},
                            "name": {"type": "string", "description": "Process name to kill"},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "system_info",
                    "description": "Get system information: CPU, memory, disk usage",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "window_list",
                    "description": "List all open windows with their titles",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "window_focus",
                    "description": "Focus/bring to front a window by title",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Window title (partial match)"},
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "window_minimize",
                    "description": "Minimize a window by title",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Window title (partial match)"},
                        },
                        "required": ["title"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "session_list",
                    "description": "List saved conversation sessions (last 5 by default)",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Number of sessions to show", "default": 5},
                        },
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "session_load",
                    "description": "Restore a saved conversation session by name",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Session name to restore"},
                        },
                        "required": ["name"],
                    },
                },
            },
        ]

    def _request_approval(self, action: str) -> bool:
        print(f"\n  [PERMISSION] {action}")
        resp = input("  Allow? (y/n/always): ").strip().lower()
        if resp in ("y", "yes", "s", "si", "sí"):
            return True
        if resp == "always":
            self.permissions.set_mode_for("terminal", "auto")
            self.permissions.set_mode_for("desktop", "auto")
            self.permissions.set_mode_for("files", "auto")
            return True
        return False

    def _speak(self, text: str):
        cleaned = self._clean_for_voice(text)
        try:
            print(f"\n{cleaned}")
        except Exception:
            pass
        if self.voice_enabled and self.tts:
            self.tts.say(cleaned)

    @staticmethod
    def _clean_for_voice(text: str) -> str:
        import re

        # Remove code blocks
        text = re.sub(r"```[\s\S]*?```", "", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)

        # Remove markdown formatting
        text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
        text = re.sub(r"\*([^*]+)\*", r"\1", text)
        text = re.sub(r"__([^_]+)__", r"\1", text)
        text = re.sub(r"_([^_]+)_", r"\1", text)
        text = re.sub(r"~~([^~]+)~~", r"\1", text)

        # Remove any remaining standalone formatting chars
        text = re.sub(r"(?<!\w)[*_~]{1,3}(?!\w)", "", text)

        # Remove markdown headers
        text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)

        # Remove bullet points with symbols
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

        # Remove horizontal rules
        text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)

        # Remove emojis (Unicode ranges)
        text = re.sub(
            r"[\U0001F600-\U0001F64F"
            r"\U0001F300-\U0001F5FF"
            r"\U0001F680-\U0001F6FF"
            r"\U0001F1E0-\U0001F1FF"
            r"\U00002702-\U000027B0"
            r"\U000024C2-\U0001F251"
            r"\U0001F900-\U0001F9FF"
            r"\U0001FA00-\U0001FA6F"
            r"\U0001FA70-\U0001FAFF"
            r"\U00002600-\U000026FF"
            r"\U0000FE00-\U0000FE0F"
            r"\U0000200D"
            r"\U000023CF"
            r"\U000023E9-\U000023F3"
            r"\U000023F8-\U000023FA"
            r"\U00002B50"
            r"\U0001F004"
            r"\U0001F0CF"
            r"\U0001F18E"
            r"\U0001F191-\U0001F19A"
            r"\U0001F201-\U0001F202"
            r"\U0001F21A"
            r"\U0001F22F"
            r"\U0001F232-\U0001F23A"
            r"\U0001F250-\U0001F251"
            r"\U0001F310-\U0001F320"
            r"\U0001F32D-\U0001F335"
            r"\U0001F337-\U0001F37C"
            r"\U0001F37E-\U0001F393"
            r"\U0001F3A0-\U0001F3CA"
            r"\U0001F3CF-\U0001F3D3"
            r"\U0001F3E0-\U0001F3F0"
            r"\U0001F3F4"
            r"\U0001F3F8-\U0001F43E"
            r"\U0001F440"
            r"\U0001F442-\U0001F4FC"
            r"\U0001F4FF-\U0001F53D"
            r"\U0001F54B-\U0001F54E"
            r"\U0001F550-\U0001F567"
            r"\U0001F57A"
            r"\U0001F595-\U0001F596"
            r"\U0001F5A4"
            r"\U0001F5FB-\U0001F64F"
            r"\U0001F680-\U0001F6C5"
            r"\U0001F6CC"
            r"\U0001F6D0-\U0001F6D2"
            r"\U0001F6D5-\U0001F6D7"
            r"\U0001F6EB-\U0001F6EC"
            r"\U0001F6F3-\U0001F6FC"
            r"\U0001F7E0-\U0001F7EB"
            r"\U0001F90C-\U0001F93A"
            r"\U0001F93C-\U0001F945"
            r"\U0001F947-\U0001F971"
            r"\U0001F973-\U0001F976"
            r"\U0001F97A-\U0001F9A2"
            r"\U0001F9A5-\U0001F9AA"
            r"\U0001F9AE-\U0001F9CA"
            r"\U0001F9CD-\U0001F9FF"
            r"\U0001FA70-\U0001FA74"
            r"\U0001FA78-\U0001FA7C"
            r"\U0001FA80-\U0001FA86"
            r"\U0001FA90-\U0001FAA8"
            r"\U0001FAB0-\U0001FAB6"
            r"\U0001FAC0-\U0001FAC2"
            r"\U0001FAD0-\U0001FAD6"
            r"]+",
            "",
            text,
        )

        # Remove zero-width and invisible characters
        text = text.replace("\u200b", "").replace("\u200c", "").replace("\u200d", "")
        text = text.replace("\ufeff", "").replace("\u200e", "").replace("\u200f", "")

        # Normalize for voice: remove characters that TTS pronounces awkwardly
        text = text.replace("→", ". ")
        text = text.replace("—", ", ")
        text = text.replace("–", "-")
        text = text.replace("…", ".")

        # Remove remaining non-speech symbols (keep letters, numbers, punctuation)
        text = re.sub(r"[<>\[\]{}|\\^~`@#$%&]", "", text)

        # Clean up extra whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" {2,}", " ", text)
        text = re.sub(r"\.{2,}", ".", text)
        text = re.sub(r",{2,}", ",", text)
        text = text.strip()

        # Ensure it ends with proper punctuation
        if text and text[-1] not in ".!?":
            text += "."

        return text

    @staticmethod
    def _resample(audio, orig_sr):
        if orig_sr == 16000:
            return audio
        target_sr = 16000
        duration = len(audio) / orig_sr
        new_len = int(duration * target_sr)
        indices = np.linspace(0, len(audio) - 1, new_len)
        return np.interp(indices, np.arange(len(audio)), audio).astype(np.float32)

    def _is_sleep_command(self, text: str) -> bool:
        t = text.lower().strip()
        sleep_phrases = (
            "dormir", "duerme", "a dormir", "descansa", "sleep",
            "adiós", "adios", "hasta luego", "hasta mañana",
            "nada más", "nada mas", "eso es todo", "ya está",
            "gracias", "thank you", "no necesito nada más",
        )
        return any(phrase in t for phrase in sleep_phrases)

    def _handle_command(self, cmd: str):
        parts = cmd.split()
        if not parts:
            return

        name = parts[0]
        if name == "exit" or name == "quit":
            self.running = False
        elif name == "voice":
            print("Switching to voice mode...")
            self.voice_enabled = True
            if not self.stt:
                self.stt = SpeechToText(self.config.get("voice", {}))
                self.tts = TextToSpeech(self.config.get("voice", {}))
                self.wakeword = WakeWordDetector(self.config.get("voice", {}))
            self.run_voice()
        elif name == "provider":
            print(f"Current provider: {self.llm.provider_type}")
            print(f"Current model: {self.llm.model}")
        elif name == "mode":
            if len(parts) > 1:
                mode = parts[1]
                if mode in ("ask", "auto", "deny"):
                    self.permissions.set_default_mode(mode)
                    print(f"Permission mode set to: {mode}")
                else:
                    print(f"Invalid mode: {mode}")
            else:
                print(f"Current mode: {self.permissions.default_mode}")
        elif name == "help":
            print("Commands: /exit, /voice, /provider, /mode [ask|auto|deny], /sessions, /help")
        elif name == "sessions":
            sessions = self.session.list_sessions()
            if not sessions:
                print("No saved sessions.")
            else:
                for i, s in enumerate(sessions[:5], 1):
                    date = s["saved_at"][:16].replace("T", " ")
                    print(f"  {i}. {s['name']} ({s['messages']} msgs) - {date}")

    def stop(self):
        self.running = False
        self.session.save(self.conversation_history)
        self.indicator.stop()
        if self.stt:
            self.stt.close_stream()
        if self.wakeword:
            self.wakeword.stop()
