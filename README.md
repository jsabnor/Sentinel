# Sentinel - AI OS Agent

> Voice-controlled AI agent for complete operating system management.
> Designed for accessibility — fully usable by visually impaired users.

[English](#english) | [Español](#espanol)

---

<a name="english"></a>
## English

### What is Sentinel?

Sentinel is an AI agent that controls your operating system via voice or text. It executes terminal commands, manages files, controls the desktop (mouse, keyboard, screenshots), handles windows and processes — all through natural language.

You speak, Sentinel acts. Designed for accessibility.

---

### Quick Install

```bash
git clone <repo-url> sentinel
cd sentinel
python install.py
```

The interactive installer guides you through:
1. Python dependencies
2. LLM provider selection and API key
3. Voice configuration: Whisper STT model + TTS engine (pyttsx3, Piper, Edge)
4. Downloads Whisper model for offline speech recognition
5. Downloads Piper voice model if selected
6. Wake words and permissions setup
7. Generates `.env` and `config.yaml`
8. **Optional: installs as a background service** (auto-start with OS)

After install, just run:
```bash
start_sentinel.bat        # Windows
# or it starts automatically on next login if you chose the service option
```

> **100% local voice**: Whisper for STT, Piper/pyttsx3 for TTS. No cloud voice APIs. Only the LLM needs internet (unless using local Ollama).

Or manual install:

```bash
pip install -r requirements.txt
# Create .env with your API key
# Edit config.yaml
```

---

### Usage

```bash
python main.py              # Voice mode (push-to-talk)
python main.py chat          # Text chat mode
python main.py --help        # All options
python main.py --list-audio  # List audio devices
python main.py --list-sessions  # List saved sessions
```

**Push-to-talk**: Hold `Ctrl+Alt+S`, speak, release to send. (Configurable in `config.yaml`)

**Chat mode** commands:
| Command | Description |
|---------|-------------|
| `/exit` | Quit |
| `/voice` | Switch to voice mode |
| `/provider` | Show current LLM provider |
| `/mode ask\|auto\|deny` | Change permissions |
| `/sessions` | List saved sessions |
| `/help` | Show help |

---

### Voice Pipeline (100% Local)

| Component | Engine | Notes |
|-----------|--------|-------|
| Wake Word | Whisper `tiny` | Fast, low resource |
| Speech-to-Text | Whisper `base`/`small` | Offline, Spanish-capable |
| Text-to-Speech | pyttsx3 / Piper / Edge | Offline neural TTS |

Auto-detects device sample rate. Resamples to 16kHz for Whisper.

---

### Configuration (`config.yaml`)

```yaml
llm:
  provider: deepseek          # openai, anthropic, deepseek, ollama, groq, google, openrouter
  model: deepseek-v4-flash
  temperature: 0.2

voice:
  input_device: null           # Mic index/name (null = Windows default)
  output_device: null          # Speaker index/name
  stt:
    engine: whisper
    language: es
    model: small               # tiny, base, small, medium, large
  tts:
    engine: piper              # pyttsx3, piper, edge
    piper:
      model_path: "models/piper/es_ES-carlfm-x_low/es_ES-carlfm-x_low.onnx"
  activation: pushtotalk       # wakeword, pushtotalk, always
  wakeword_model: tiny
  wake_words: [sentinel, centinela]
  push_to_talk_key: ctrl+alt+s
  quit_key: ctrl+alt+q

safety:
  default_mode: auto           # ask, auto, deny
  permissions:
    terminal:
      mode: auto               # All auto = no confirmation prompts
      blocked_commands: [rm -rf /, format, diskpart]
    files:
      blocked_paths: [C:\Windows, /etc]
    processes:
      blocked_processs: [System, svchost]
  high_risk_patterns: [delete, remove, shutdown, kill]

sandbox:
  enabled: false

desktop:
  screenshot_quality: 80
  mouse_speed: 0.3

logging:
  level: INFO
```

---

### Capabilities (Tools)

| Tool | Description |
|------|-------------|
| `terminal_execute` | Run shell commands (auto non-blocking for app launches) |
| `desktop_screenshot` | Take screenshots |
| `desktop_click` | Click at coordinates |
| `desktop_type` | Type text |
| `desktop_move_mouse` | Move cursor |
| `desktop_press_key` | Press a key |
| `desktop_hotkey` | Key combinations |
| `file_read` / `file_write` / `file_list` / `file_delete` | File operations |
| `process_list` / `process_kill` | Process management |
| `system_info` | CPU, RAM, disk |
| `window_list` / `window_focus` / `window_minimize` | Window management |
| `session_list` / `session_load` | Session management |

---

### Knowledge Base

OS administration knowledge is stored as Markdown files in `knowledge/`, loaded automatically at startup. Only relevant files are loaded for the detected OS.

```
knowledge/
  01-identity.md       - Agent identity, voice rules, accessibility
  02-opening-apps.md   - App launching procedure
  03-windows.md        - Windows administration
  04-linux.md          - Linux administration
  05-macos.md          - macOS administration
  06-cross-platform.md - Cross-platform reference
  07-sessions.md       - Session management
```

Edit or add `.md` files to extend the agent's knowledge without touching code.

---

### Sessions

- Each start creates a new session
- Auto-saved on exit to `sessions/`
- Voice: "restaura la sesion anterior" → lists last 5, ask which to restore
- Chat: `/sessions` lists saved sessions
- History is trimmed to last 12 messages to save tokens

---

### Token Optimization

- **History trimming**: keeps last 12 messages only
- **OS-specific knowledge**: loads only relevant `.md` files (40% fewer tokens)
- **Anthropic prompt caching**: system prompt cached server-side
- **Voice response cleaning**: strips emojis, markdown, and formatting before TTS

---

### Background Service (No Console)

The installer offers to set this up automatically. To manage manually:

| OS | Install | Start | Stop |
|----|---------|-------|------|
| **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` | `stop_sentinel.bat` or `Ctrl+Alt+Q` |
| **Linux** | `bash install_service.sh` | Auto at login (systemd) | `systemctl --user stop sentinel` |
| **macOS** | `bash install_service.sh` | Auto at login (launchd) | `launchctl unload ~/Library/LaunchAgents/com.sentinel.agent.plist` |

When running as a service:
- No console window — only the status indicator on screen
- **F9** to talk globally from any window (configurable)
- **Ctrl+Alt+Q** to quit
- Voice responses play through speakers
- Logs in `sentinel_service.log`

---

| Provider | API Key | Notes |
|----------|---------|-------|
| DeepSeek | `DEEPSEEK_API_KEY` | Recommended (deepseek-v4-flash) |
| OpenAI | `OPENAI_API_KEY` | GPT-4o, GPT-4 |
| Anthropic | `ANTHROPIC_API_KEY` | Claude, prompt caching |
| Ollama | None | Local, no internet |
| Groq | `GROQ_API_KEY` | Fast inference |
| Google | `GOOGLE_API_KEY` | Gemini |
| OpenRouter | `OPENROUTER_API_KEY` | Multi-provider |

---

### Troubleshooting

**Microphone not capturing**: Run `python main.py --list-audio`, find your device index, set `input_device` in config.

**No sound output**: Check `output_device` in config. Ensure speakers are set as Windows default.

**Whisper model download**: First use downloads automatically (~150MB base, ~500MB small). Run `python install.py` to pre-download.

**Piper voice**: Download `.onnx` and `.json` from [Piper releases](https://github.com/rhasspy/piper/releases). Set `model_path` in config.

**DeepSeek errors**: Ensure `DEEPSEEK_API_KEY` is in `.env`. Model `deepseek-chat` deprecated — use `deepseek-v4-flash`.

---

### Project Structure

```
sentinel/
├── main.py                    # Entry point + CLI
├── install.py                 # Interactive installer
├── config.yaml                # Configuration
├── requirements.txt           # Dependencies
├── knowledge/                 # Agent knowledge (editable .md files)
├── sessions/                  # Saved conversation sessions
├── sentinel/
│   ├── core.py                # Main agent loop, tools, push-to-talk
│   ├── config.py              # YAML + .env loader
│   ├── sessions.py            # Session save/load/list
│   ├── agent/
│   │   ├── llm.py             # LLM engine, knowledge loader, caching
│   │   └── prompts.py         # System prompt
│   ├── actions/
│   │   ├── terminal.py        # Shell execution + app launching
│   │   ├── desktop.py         # Mouse, keyboard, screenshots
│   │   ├── files.py           # File operations
│   │   ├── processes.py       # Process management
│   │   └── windows.py         # Window management
│   ├── providers/
│   │   ├── base.py            # Abstract provider
│   │   ├── openai.py, anthropic.py, deepseek.py, ollama.py, groq.py,
│   │   ├── google.py, minimax.py, opencode.py, openrouter.py
│   ├── safety/
│   │   ├── permissions.py     # Permission manager
│   │   └── sandbox.py         # Sandbox
│   ├── voice/
│   │   ├── wakeword.py        # Wake word detection (Whisper tiny)
│   │   ├── stt.py             # Speech-to-text (Whisper)
│   │   └── tts.py             # Text-to-speech (Piper/pyttsx3/Edge)
│   └── ui/
│       └── indicator.py       # Desktop status indicator
```

---

<a name="espanol"></a>
## Español

### Qué es Sentinel

Sentinel es un agente de IA que controla tu sistema operativo mediante voz o texto. Ejecuta comandos de terminal, gestiona archivos, controla el escritorio (ratón, teclado, capturas), maneja ventanas y procesos — todo con lenguaje natural.

Tú hablas, Sentinel actúa. Diseñado para accesibilidad.

---

### Instalación Rápida

```bash
git clone <repo-url> sentinel
cd sentinel
python install.py
```

El instalador interactivo te guía paso a paso: dependencias, proveedor LLM, configuración de voz, descarga de modelos Whisper y Piper.

> **Voz 100% local**: Whisper para STT, Piper/pyttsx3 para TTS. Sin APIs de voz en la nube. Solo el LLM necesita internet (salvo con Ollama local).

---

### Uso

```bash
python main.py              # Modo voz (push-to-talk)
python main.py chat          # Modo chat
python main.py --list-audio  # Listar dispositivos
python main.py --list-sessions  # Ver sesiones
```

**Push-to-talk**: Mantén `Ctrl+Alt+S`, habla, suelta para enviar.

**Modo chat**: `/exit`, `/voice`, `/provider`, `/mode`, `/sessions`, `/help`.

---

### Pipeline de Voz (100% Local)

| Componente | Motor | Notas |
|-----------|-------|-------|
| Wake Word | Whisper `tiny` | Rápido, bajo consumo |
| Voz a Texto | Whisper `base`/`small` | Sin conexión, español |
| Texto a Voz | pyttsx3 / Piper / Edge | TTS neuronal offline |

---

### Capacidades

Ejecución de comandos, capturas de pantalla, clics/tecleo/ratón, gestión de archivos, procesos, ventanas, sesiones. El TTS limpia automáticamente emojis, markdown y formato para que suene natural.

---

### Base de Conocimiento

El conocimiento de administración de SO está en `knowledge/*.md`. Se carga automáticamente al iniciar, solo los archivos relevantes para el SO detectado.

---

### Sesiones

- Cada inicio crea una sesión nueva
- Se guarda automáticamente al salir en `sessions/`
- Por voz: "restaura la sesión anterior" → lista las últimas 5
- Por chat: `/sessions`

---

### Optimización de Tokens

- Historial recortado a 12 mensajes
- Conocimiento específico por SO
- Caching de prompt en Anthropic
- Limpieza de formato en respuestas TTS

---

### Solución de Problemas

**Micrófono no captura**: `python main.py --list-audio`, configura `input_device`.

**Sin sonido**: Configura `output_device` o usa los predeterminados de Windows.

**Modelo Whisper**: Se descarga automáticamente. Usa `python install.py` para pre-descargar.

**Voz Piper**: Descarga `.onnx` de [Piper releases](https://github.com/rhasspy/piper/releases).

**Errores DeepSeek**: API key en `.env`. Usa `deepseek-v4-flash`.
