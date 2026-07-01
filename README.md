# Sentinel v1.1.0-apple-pie

> 🎙️ Voice-controlled AI agent for complete operating system management  
> ♿ Designed for universal accessibility — usable by anyone, regardless of age or ability

[English](#english) | [Español](#espanol)

---

<a name="english"></a>
## English

### 🤖 What is Sentinel?

Sentinel is a voice-controlled AI agent that manages your operating system. You speak, it acts.

- 🖥️ **Open applications** — "Abre Spotify", "Open Chrome"
- 🌐 **Search the web** — "Busca restaurantes en Madrid"
- 📂 **Manage files** — "Crea un documento en el escritorio"
- 📸 **Read your screen** — "¿Qué hay en pantalla?"
- 🗣️ **Guided workflows** — "Quiero enviar un correo"
- 💬 **Natural conversation** — Follow-up questions without pressing keys again

---

### ⚡ Quick Start

```bash
git clone https://github.com/jsabnor/Sentinel.git sentinel
cd sentinel
python install.py
```

The interactive installer handles everything: dependencies, API keys, voice models, and optionally installs Sentinel as a background service that starts with your OS.

```bash
start_sentinel.bat        # Launch background service (Windows)
python main.py chat        # Text chat mode
```

---

### 🎮 Usage

| Action | How |
|--------|-----|
| **Push-to-talk** | Press **F9**, speak, release. Auto-listens 4s for follow-up. |
| **Chat mode** | `python main.py chat` — text interface |
| **Background service** | `start_sentinel.bat` — no console, starts with Windows |
| **List devices** | `python main.py --list-audio` |
| **List sessions** | `python main.py --list-sessions` |

**Chat commands:** `/exit` `/voice` `/provider` `/mode ask|auto|deny` `/sessions` `/help`

---

### 🔊 Voice Pipeline — 100% Local

| Stage | Engine | Notes |
|-------|--------|-------|
| 🎤 **Speech-to-Text** | Whisper (`small`) | Offline, multi-language |
| 🔊 **Text-to-Speech** | Piper / pyttsx3 / Edge | Neural TTS, offline |
| 🎵 **Audio Capture** | sounddevice | Auto-detects device sample rate |

> No cloud voice APIs. Only the LLM needs internet — or use Ollama for fully offline operation.

---

### ♿ Accessibility Features

| Feature | Description |
|---------|-------------|
| 🎙️ **Full voice control** | No keyboard or mouse needed |
| 🔊 **Audio cues** | Beep when listening, double-chime when done |
| 📊 **Visual indicator** | Top-right status: "En espera" · "REC Escuchando" · "Procesando" · "Respondiendo" |
| 👶👨‍💻 **User profiles** | `child` (simple + safe) · `standard` · `expert` (concise) |
| 💬 **Conversation mode** | Auto-listens for follow-up after each response |
| 📖 **Screen reading** | Describes windows and content by voice |
| 🗺️ **Guided workflows** | Step-by-step for email, browsing, weather, files |
| 🧹 **Clean speech** | No emojis, markdown, or formatting in voice output |
| 💾 **Sessions** | Save and restore conversations by voice |
| 🛡️ **Error recovery** | Clear spoken explanations, never crashes silently |

---

### ⚙️ Configuration (`config.yaml`)

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
  conversation_timeout: 4     # Auto-listen seconds after response
  wake_words: [sentinel, centinela]
  wakeword_model: tiny
  input_device: null
  output_device: null
  stt:
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
  high_risk_patterns: [delete, remove, shutdown, kill]
```

---

### 🧠 Knowledge Base

Agent knowledge is stored as editable Markdown files in `knowledge/`:

| File | Content |
|------|---------|
| `01-identity.md` | Agent identity, voice rules, accessibility |
| `02-opening-apps.md` | Application launching procedure |
| `03-windows.md` | Windows administration |
| `04-linux.md` | Linux administration |
| `05-macos.md` | macOS administration |
| `06-cross-platform.md` | Cross-platform commands |
| `07-sessions.md` | Session management |
| `08-efficiency.md` | Efficient command patterns |
| `09-accessibility.md` | Universal accessibility design |
| `10-help.md` | Help and onboarding |
| `11-workflows.md` | Guided task workflows |

> Edit or add `.md` files to extend the agent's knowledge without touching code.

---

### 🛠️ Tools (20)

| Tool | Description |
|------|-------------|
| `terminal_execute` | Run shell commands (auto non-blocking for apps) |
| `desktop_screenshot` | Take screenshots |
| `desktop_read_screen` | Describe what's on screen |
| `desktop_click` | Click at coordinates |
| `desktop_type` | Type text |
| `desktop_move_mouse` | Move cursor |
| `desktop_press_key` | Press a key |
| `desktop_hotkey` | Key combinations |
| `file_read` `file_write` `file_list` `file_delete` | File operations |
| `process_list` `process_kill` | Process management |
| `system_info` | CPU, RAM, disk |
| `window_list` `window_focus` `window_minimize` | Window management |
| `session_list` `session_load` | Session management |

---

### 🌐 Supported LLM Providers

| Provider | Model | Notes |
|----------|-------|-------|
| 🚀 **DeepSeek** | `deepseek-v4-flash` | Recommended |
| 🧠 **OpenAI** | `gpt-4o` | Automatic caching |
| 🔮 **Anthropic** | `claude-sonnet-4` | Prompt caching |
| 🏠 **Ollama** | `llama3` | Local, no API key |
| ⚡ **Groq** | `llama-3.3-70b` | Fast inference |
| 🌟 **Google** | `gemini-2.5-flash` | Gemini API |
| 🔗 **OpenRouter** | `openai/gpt-4o` | Multi-provider |

---

### 🖥️ Background Service

| OS | Install | Control |
|----|---------|---------|
| **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` / `stop_sentinel.bat` |
| **Linux** | `bash install_service.sh` | `systemctl --user start/stop sentinel` |
| **macOS** | `bash install_service.sh` | `launchctl load/unload` |

No console window. Global hotkey from any application. F9 to talk, Ctrl+Alt+Q to quit. Auto-starts with OS.

---

### 📁 Project Structure

```
sentinel/
├── main.py                    # Entry point + CLI
├── install.py                 # Interactive installer
├── sentinelw.pyw              # Windows background launcher (no console)
├── sentinel_service.py        # Cross-platform background service
├── start_sentinel.bat         # Start service
├── stop_sentinel.bat          # Stop service
├── check_sentinel.bat         # Check service status
├── install_service.ps1        # Windows service installer
├── install_service.sh         # Linux/macOS service installer
├── config.yaml                # Configuration
├── requirements.txt           # Dependencies
├── knowledge/                 # Agent knowledge (.md files)
├── sessions/                  # Saved conversations
└── sentinel/
    ├── core.py                # Main agent loop, tools, voice modes
    ├── config.py              # YAML + .env loader
    ├── sessions.py            # Session save/load/list
    ├── agent/
    │   ├── llm.py             # LLM engine, knowledge loader, caching
    │   └── prompts.py         # System prompt
    ├── actions/
    │   ├── terminal.py        # Shell execution + app launching
    │   ├── desktop.py         # Mouse, keyboard, screenshots, screen reading
    │   ├── files.py           # File operations
    │   ├── processes.py       # Process management
    │   └── windows.py         # Window management
    ├── providers/             # 9 LLM providers
    ├── safety/
    │   ├── permissions.py     # Permission manager
    │   └── sandbox.py         # Sandbox
    ├── voice/
    │   ├── wakeword.py        # Wake word detection
    │   ├── stt.py             # Speech-to-text (Whisper)
    │   └── tts.py             # Text-to-speech (Piper/pyttsx3/Edge)
    └── ui/
        ├── indicator.py       # Desktop status indicator
        └── sounds.py          # Audio feedback cues
```

---

### 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Microphone not capturing | `python main.py --list-audio`, set `input_device` in config |
| No sound output | Check `output_device` or set to `null` for Windows default |
| Whisper model download | First use auto-downloads. Pre-download: `python install.py` |
| Piper voice issues | Download `.onnx` from [Piper releases](https://github.com/rhasspy/piper/releases) |
| DeepSeek errors | Ensure `DEEPSEEK_API_KEY` in `.env`. Use `deepseek-v4-flash` |
| Service won't start | Run `check_sentinel.bat`. Check `sentinel_service.log` |

---

<a name="espanol"></a>
## Español

### 🤖 Qué es Sentinel

Sentinel es un agente de IA controlado por voz que gestiona tu sistema operativo. Tú hablas, él actúa.

- 🖥️ **Abre aplicaciones** — "Abre Spotify", "Abre Chrome"
- 🌐 **Busca en internet** — "Busca restaurantes en Madrid"
- 📂 **Gestiona archivos** — "Crea un documento en el escritorio"
- 📸 **Lee tu pantalla** — "¿Qué hay en pantalla?"
- 🗣️ **Te guía paso a paso** — "Quiero enviar un correo"
- 💬 **Conversación natural** — Te sigue la conversación sin pulsar teclas

---

### ⚡ Inicio Rápido

```bash
git clone https://github.com/jsabnor/Sentinel.git sentinel
cd sentinel
python install.py
```

El instalador configura todo: dependencias, API keys, modelos de voz, y opcionalmente instala Sentinel como servicio en segundo plano.

```bash
start_sentinel.bat        # Iniciar servicio (Windows)
python main.py chat        # Modo chat (texto)
```

---

### 🎮 Uso

| Acción | Cómo |
|--------|------|
| **Push-to-talk** | Pulsa **F9**, habla, suelta. Auto-escucha 4s para seguir la conversación. |
| **Modo chat** | `python main.py chat` |
| **Servicio en segundo plano** | `start_sentinel.bat` — sin consola, arranca con Windows |
| **Listar dispositivos** | `python main.py --list-audio` |
| **Listar sesiones** | `python main.py --list-sessions` |

---

### 🔊 Pipeline de Voz — 100% Local

| Etapa | Motor |
|-------|-------|
| 🎤 Voz a Texto | Whisper (`small`) |
| 🔊 Texto a Voz | Piper / pyttsx3 / Edge |
| 🎵 Captura de audio | sounddevice |

---

### ♿ Accesibilidad

| Funcionalidad | Descripción |
|---------------|-------------|
| 🎙️ Control total por voz | Sin teclado ni ratón |
| 🔊 Sonidos de estado | Beep al escuchar, doble chime al terminar |
| 📊 Indicador visual | Barra superior: "En espera" · "REC Escuchando" · "Procesando" · "Respondiendo" |
| 👶👨‍💻 Perfiles | `child` (infantil) · `standard` · `expert` |
| 💬 Modo conversación | Auto-escucha tras cada respuesta |
| 📖 Lectura de pantalla | Describe ventanas y contenido |
| 🗺️ Workflows guiados | Email, búsquedas, clima, archivos |
| 🧹 Voz limpia | Sin emojis ni markdown en TTS |
| 💾 Sesiones | Guardar y recuperar conversaciones |
| 🛡️ Errores | Explicaciones habladas, nunca crashes silenciosos |

---

### 🌐 Proveedores LLM

🚀 **DeepSeek** · 🧠 **OpenAI** · 🔮 **Anthropic** · 🏠 **Ollama** · ⚡ **Groq** · 🌟 **Google** · 🔗 **OpenRouter**

---

### 🖥️ Servicio en Segundo Plano

| SO | Instalar | Control |
|----|---------|---------|
| **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` / `stop_sentinel.bat` |
| **Linux** | `bash install_service.sh` | `systemctl --user start/stop sentinel` |
| **macOS** | `bash install_service.sh` | `launchctl load/unload` |

Sin ventana de consola. F9 funciona desde cualquier aplicación. Ctrl+Alt+Q para salir.

---

### 📁 Estructura del Proyecto

```
sentinel/
├── main.py                    # Punto de entrada + CLI
├── install.py                 # Instalador interactivo
├── sentinelw.pyw              # Lanzador Windows sin consola
├── sentinel_service.py        # Servicio multiplataforma
├── start_sentinel.bat         # Iniciar servicio
├── stop_sentinel.bat          # Parar servicio
├── check_sentinel.bat         # Verificar estado
├── install_service.ps1        # Instalador de servicio Windows
├── install_service.sh         # Instalador de servicio Linux/macOS
├── config.yaml                # Configuración
├── requirements.txt           # Dependencias
├── knowledge/                 # Conocimiento del agente (.md)
├── sessions/                  # Conversaciones guardadas
└── sentinel/
    ├── core.py                # Bucle principal, herramientas, modos de voz
    ├── agent/llm.py           # Motor LLM, caching
    ├── actions/               # Terminal, escritorio, archivos, procesos, ventanas
    ├── providers/             # 9 proveedores LLM
    ├── safety/                # Permisos y sandbox
    ├── voice/                 # Wakeword, STT, TTS
    └── ui/                    # Indicador visual, sonidos
```
