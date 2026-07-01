# Sentinel v1.1.0 - AI OS Agent

> Voice-controlled AI agent for complete operating system management.
> Designed for universal accessibility — usable by anyone, regardless of age or ability.

[English](#english) | [Español](#espanol)

---

<a name="english"></a>
## English

### What is Sentinel?

Sentinel is a voice-controlled AI agent that manages your operating system. You speak, it acts. It opens applications, searches the web, manages files, controls the desktop, reads your screen, and guides you through complex tasks — all by voice. Designed for accessibility.

### Quick Start

```bash
git clone <repo-url> sentinel
cd sentinel
python install.py
```

The installer sets up everything: dependencies, API keys, voice models, and optionally installs Sentinel as a background service that starts with your OS.

### Usage

| Action | How |
|--------|-----|
| **Push-to-talk** (default) | Press **F9**, speak, release. Agent responds. Then auto-listens 4s for follow-up. |
| **Chat mode** | `python main.py chat` |
| **Background service** | `start_sentinel.bat` (Windows) — no console, starts with OS |
| **List sessions** | `python main.py --list-sessions` |
| **List audio devices** | `python main.py --list-audio` |

### Voice Pipeline (100% Local)

| Stage | Engine | Notes |
|-------|--------|-------|
| Speech-to-Text | Whisper (`small` recommended) | Offline, Spanish-capable |
| Text-to-Speech | Piper / pyttsx3 / Edge | Offline neural TTS |
| Audio Capture | sounddevice | Auto-detects device sample rate |

### Configuration (`config.yaml`)

```yaml
llm:
  provider: deepseek          # openai, anthropic, deepseek, ollama, groq, google, openrouter
  model: deepseek-v4-flash
  temperature: 0.2

voice:
  profile: standard           # child, standard, expert
  activation: pushtotalk      # wakeword, pushtotalk, always
  push_to_talk_key: f9
  quit_key: ctrl+alt+q
  conversation_timeout: 4     # Auto-listen seconds after response (0 = off)
  wake_words: [sentinel, centinela]
  wakeword_model: tiny
  input_device: null          # Mic (null = Windows default)
  output_device: null         # Speakers (null = Windows default)
  stt:
    engine: whisper
    language: es
    model: small
  tts:
    engine: piper             # piper, pyttsx3, edge
    piper:
      model_path: "models/piper/es_ES-carlfm-x_low/es_ES-carlfm-x_low.onnx"

safety:
  default_mode: auto
  permissions:
    terminal:
      mode: auto
      blocked_commands: [rm -rf /, format, diskpart]
    files:
      mode: auto
      blocked_paths: [C:\Windows, C:\Windows\System32, /etc, /boot]
    processes:
      mode: auto
      blocked_processs: [System, svchost]
  high_risk_patterns: [delete, remove, shutdown, kill]
```

### Accessibility Features

| Feature | Description |
|---------|-------------|
| **Voice control** | Full PC control by voice. No keyboard or mouse needed. |
| **Audio cues** | Beep when listening (F9 pressed), double-chime when done. |
| **Visual indicator** | Top-right status bar: "En espera", "REC Escuchando", "Procesando", "Respondiendo". |
| **User profiles** | `child` (simple words, extra safety), `standard`, `expert` (concise). |
| **Conversation mode** | After responding, auto-listens for follow-up questions. |
| **Screen reading** | "¿Qué hay en pantalla?" — describes windows and content. |
| **Guided workflows** | Step-by-step for email, browsing, weather, file management. |
| **Clean speech** | Responses stripped of emojis, markdown, and formatting for natural TTS. |
| **Session management** | Save/restore conversations. Voice or chat commands. |
| **Error recovery** | Clear spoken explanations on failure. Crash logs for debugging. |

### Capabilities (17 Tools)

`terminal_execute`, `desktop_screenshot`, `desktop_read_screen`, `desktop_click`, `desktop_type`, `desktop_move_mouse`, `desktop_press_key`, `desktop_hotkey`, `file_read`, `file_write`, `file_list`, `file_delete`, `process_list`, `process_kill`, `system_info`, `window_list`, `window_focus`, `window_minimize`, `session_list`, `session_load`

### Background Service

| OS | Install | Control |
|----|---------|---------|
| **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` / `stop_sentinel.bat` |
| **Linux** | `bash install_service.sh` | `systemctl --user start/stop sentinel` |
| **macOS** | `bash install_service.sh` | `launchctl load/unload` |

No console window. Global hotkey works from any application. F9 to talk, Ctrl+Alt+Q to quit.

### Supported LLM Providers

| Provider | Model | Notes |
|----------|-------|-------|
| DeepSeek | `deepseek-v4-flash` | Recommended |
| OpenAI | `gpt-4o` | Prompt caching automatic |
| Anthropic | `claude-sonnet-4` | Prompt caching via `cache_control` |
| Ollama | `llama3` | Local, no API key |
| Groq | `llama-3.3-70b` | Fast inference |
| Google | `gemini-2.5-flash` | Gemini API |
| OpenRouter | `openai/gpt-4o` | Multi-provider |
| MiniMax | `abab7-chat` | |
| OpenCode | | |

### Knowledge Base

Agent knowledge is stored as editable Markdown files in `knowledge/`:
- `01-identity.md` — Agent identity and voice rules
- `02-opening-apps.md` — Application launching procedure
- `03-windows.md` — Windows administration
- `04-linux.md` — Linux administration
- `05-macos.md` — macOS administration
- `06-cross-platform.md` — Cross-platform commands
- `07-sessions.md` — Session management
- `08-efficiency.md` — Efficient command patterns
- `09-accessibility.md` — Universal accessibility design
- `10-help.md` — Help and onboarding
- `11-workflows.md` — Guided task workflows

### Project Structure

```
sentinel/
├── main.py                    # Entry point + CLI
├── install.py                 # Interactive installer
├── sentinelw.pyw              # Windows background launcher (no console)
├── sentinel_service.py        # Cross-platform background service
├── start_sentinel.bat         # Start background service
├── stop_sentinel.bat          # Stop background service
├── check_sentinel.bat         # Check if service is running
├── install_service.ps1        # Windows service installer
├── install_service.sh         # Linux/macOS service installer
├── config.yaml                # Configuration
├── requirements.txt           # Dependencies
├── knowledge/                 # Agent knowledge (.md files)
├── sessions/                  # Saved conversations
├── sentinel/
│   ├── core.py                # Main agent loop, tools, voice modes
│   ├── config.py              # YAML + .env loader
│   ├── sessions.py            # Session save/load/list
│   ├── agent/
│   │   ├── llm.py             # LLM engine, knowledge loader, caching
│   │   └── prompts.py         # System prompt
│   ├── actions/
│   │   ├── terminal.py        # Shell execution + app launching
│   │   ├── desktop.py         # Mouse, keyboard, screenshots, screen reading
│   │   ├── files.py           # File operations
│   │   ├── processes.py       # Process management
│   │   └── windows.py         # Window management
│   ├── providers/             # 9 LLM providers
│   ├── safety/
│   │   ├── permissions.py     # Permission manager
│   │   └── sandbox.py         # Sandbox
│   ├── voice/
│   │   ├── wakeword.py        # Wake word detection
│   │   ├── stt.py             # Speech-to-text (Whisper)
│   │   └── tts.py             # Text-to-speech (Piper/pyttsx3/Edge)
│   └── ui/
│       ├── indicator.py       # Desktop status indicator
│       └── sounds.py          # Audio feedback cues
```

---

<a name="espanol"></a>
## Español

### Qué es Sentinel

Sentinel es un agente de IA controlado por voz que gestiona tu sistema operativo. Abre aplicaciones, busca en internet, gestiona archivos, controla el escritorio, lee tu pantalla y te guía paso a paso — todo por voz. Diseñado para accesibilidad universal.

### Inicio Rápido

```bash
git clone <repo-url> sentinel
cd sentinel
python install.py
```

El instalador configura todo: dependencias, API keys, modelos de voz, y opcionalmente instala Sentinel como servicio en segundo plano.

### Uso

| Acción | Cómo |
|--------|------|
| **Push-to-talk** | Pulsa **F9**, habla, suelta. El agente responde y auto-escucha 4s. |
| **Modo chat** | `python main.py chat` |
| **Servicio en segundo plano** | `start_sentinel.bat` — sin consola, arranca con el SO |
| **Listar sesiones** | `python main.py --list-sessions` |
| **Listar audio** | `python main.py --list-audio` |

### Pipeline de Voz (100% Local)

| Etapa | Motor |
|-------|-------|
| Voz a Texto | Whisper (`small` recomendado) |
| Texto a Voz | Piper / pyttsx3 / Edge |
| Captura de audio | sounddevice |

### Funcionalidades de Accesibilidad

| Funcionalidad | Descripción |
|---------------|-------------|
| **Control por voz** | Manejo completo del PC sin teclado ni ratón |
| **Sonidos de estado** | Beep al escuchar, doble chime al terminar |
| **Indicador visual** | Barra superior derecha con estado y texto |
| **Perfiles de usuario** | `child`, `standard`, `expert` |
| **Modo conversación** | Auto-escucha 4s tras cada respuesta |
| **Lectura de pantalla** | "¿Qué hay en pantalla?" |
| **Workflows guiados** | Email, búsquedas, clima, archivos |
| **Limpieza de voz** | Sin emojis ni markdown en TTS |
| **Sesiones** | Guardar y restaurar conversaciones |

### Proveedores LLM

DeepSeek, OpenAI, Anthropic, Ollama, Groq, Google, OpenRouter, MiniMax, OpenCode.

### Servicio en Segundo Plano

| SO | Instalar | Control |
|----|---------|---------|
| **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` / `stop_sentinel.bat` |
| **Linux** | `bash install_service.sh` | `systemctl --user start/stop sentinel` |
| **macOS** | `bash install_service.sh` | `launchctl load/unload` |

Sin ventana de consola. F9 para hablar desde cualquier aplicación. Ctrl+Alt+Q para salir.
