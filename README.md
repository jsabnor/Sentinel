# 🛡️ Sentinel — AI OS Agent

> *"Tu voz. Tu sistema. Tu centinela."*  
> Agente de IA controlado por voz que gestiona tu sistema operativo al completo.  
> Diseñado para accesibilidad ♿ — 100% utilizable por personas con discapacidad visual.

[🧭 English](#english) · [🌐 Español](#espanol)

---

<a name="english"></a>
## 🧭 English

### 🤖 What is Sentinel?

Sentinel is a voice-controlled AI agent that turns natural language into actions on your computer. Just talk to it — it clicks, types, opens apps, manages files, runs terminal commands, and controls windows for you.

No mouse. No keyboard. No screen required. **You speak. Sentinel acts.**

| 🎯 Use Case | 💬 Just say... |
|------------|----------------|
| Open apps | *"Open Chrome and go to YouTube"* |
| Files & folders | *"Create a folder called Project on the desktop"* |
| System info | *"How much RAM do I have left?"* |
| Window control | *"Minimize all windows"* |
| Web searches | *"Search Google for the weather in Madrid"* |
| Terminal commands | *"Check my IP address"* |
| Keyboard control | *"Press Ctrl+Shift+Esc"* |
| Process management | *"Close Spotify"* |

---

### ⚡ Quick Install

The fastest way — **one command does it all**:

```bash
git clone https://github.com/jsabnor/sentinel.git
cd sentinel
python install.py
```

### 🧙 What the installer does for you

`install.py` is a complete guided setup. It will NEVER leave you with a half-configured project:

| Step | What happens |
|------|-------------|
| 1. 📦 | **Python dependencies** — installs everything from `requirements.txt` via pip |
| 2. 🧠 | **LLM provider** — choose DeepSeek, OpenAI, Ollama, etc. Paste your API key |
| 3. 🎤 | **Voice setup** — pick Whisper model size (`tiny` to `large`) and TTS engine (pyttsx3, Piper, Edge) |
| 4. ⬇️ | **Downloads Whisper** — offline speech recognition (~150 MB `base`, ~500 MB `small`) |
| 5. 🗣️ | **Downloads Piper voice** — optional neural Spanish/English voice (~30 MB) |
| 6. 🔐 | **Permissions** — set safety mode (`auto` / `ask` / `deny`), configure wake words |
| 7. 📝 | **Creates config** — generates `.env` + `config.yaml` ready to use |
| 8. 🪟 | **Windows service** — optional: install Sentinel as a background service that auto-starts on login |

### 🚀 After install

```bash
start_sentinel.bat        # Windows — starts immediately
```

Or if you installed the service — it launches automatically every time you log in. **You never need to touch a terminal again.**

> 🏠 **Voice is 100% local.** Whisper for speech recognition, Piper/pyttsx3 for TTS.  
> No cloud voice APIs. Only the LLM needs internet — or none at all with Ollama.

### 📦 Manual install (alternative)

```bash
pip install -r requirements.txt
# Copy .env.example to .env and add your API key
# Edit config.yaml to your liking
python main.py
```

---

### 🪟 Background Service — Install once, run forever

The installer offers to set up Sentinel as a **Windows background service**. If you accept:

- ✅ Sentinel starts **automatically** every time you log into Windows
- ✅ No console window — just a 🟢 **green icon** in the system tray
- ✅ `F9` push-to-talk works **globally**, from any application
- ✅ `Ctrl+Alt+Q` quits the service when needed
- ✅ Voice responses play through your speakers

| OS | Install command | Start | Stop |
|----|----------------|-------|------|
| 🪟 **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` or auto | `stop_sentinel.bat` or `Ctrl+Alt+Q` |
| 🐧 **Linux** | `bash install_service.sh` | Auto (systemd) | `systemctl --user stop sentinel` |
| 🍏 **macOS** | `bash install_service.sh` | Auto (launchd) | `launchctl unload ~/Library/LaunchAgents/com.sentinel.agent.plist` |

> 💡 **Tip:** You can install the service later by running the command above, or by re-running `python install.py` and answering "Yes" to the service question.

---

### 🎮 Usage

```bash
python main.py                 # 🎤 Voice mode (push-to-talk)
python main.py chat            # 💬 Text chat mode
python main.py --help          # 📋 All options
python main.py --list-audio    # 🎧 List audio devices
python main.py --list-sessions # 📂 List saved sessions
```

#### 🎤 Push-to-Talk

| Key | Action |
|-----|--------|
| `F9` | Start/stop recording (configurable) |
| `Ctrl+Alt+Q` | Quit Sentinel |

**How it works:** Press `F9` → speak your command → press `F9` again → Sentinel processes and responds by voice.

#### 💬 Chat mode commands

| Command | Description |
|---------|-------------|
| `/exit` | 🚪 Quit |
| `/voice` | 🎤 Switch to voice mode |
| `/provider` | 🧠 Show current LLM provider |
| `/mode ask\|auto\|deny` | 🔐 Change permission mode |
| `/sessions` | 📂 List saved sessions |
| `/help` | ❓ Show help |

---

### 🗣️ Voice Pipeline (100% Local)

| Component | Engine | Details |
|-----------|--------|---------|
| 🎯 Wake Word | Whisper `tiny` | Fast detection, low CPU |
| 🎤 Speech → Text | Whisper `base`/`small` | Offline, multi-language |
| 🔊 Text → Speech | pyttsx3 / Piper / Edge | Neural offline TTS |

Auto-detects device sample rate. Resamples to 16 kHz for Whisper.

---

### ⚙️ Configuration (`config.yaml`)

```yaml
llm:
  provider: deepseek              # openai, anthropic, ollama, groq, google, openrouter
  model: deepseek-v4-flash
  temperature: 0.4
  max_tokens: 4096

voice:
  input_device: null              # null = Windows default mic
  output_device: null             # null = Windows default speakers
  stt:
    engine: whisper
    language: es                  # en, es, fr, de...
    model: small                  # tiny / base / small / medium / large
  tts:
    engine: piper                 # pyttsx3, piper, edge
    rate: 180
    piper:
      model_path: "models/piper/es_ES-carlfm-x_low/es_ES-carlfm-x_low.onnx"
  activation: pushtotalk          # wakeword, pushtotalk, always
  wake_words: [sentinel]
  push_to_talk_key: f9
  quit_key: ctrl+alt+q

safety:
  default_mode: auto              # ask → confirm each action | auto → trust | deny → block all
  permissions:
    terminal:
      blocked_commands: [rm -rf /, format, diskpart]
    files:
      blocked_paths: [C:\Windows, /etc, /boot]
  high_risk_patterns: [delete, remove, shutdown, kill]

desktop:
  screenshot_quality: 80
  mouse_speed: 0.3

logging:
  level: INFO
  file: sentinel.log
```

---

### 🧰 Capabilities — What Sentinel can do for you

| 🛠️ Tool | 📝 Description | 💬 Example command |
|---------|---------------|-------------------|
| `terminal_execute` | Run shell commands | *"Install requests with pip"* |
| `desktop_screenshot` | Take screenshots | *"Show me what's on screen"* |
| `desktop_click` | Click coordinates | *"Click on the Start button"* |
| `desktop_type` | Type text | *"Type Hello World in Notepad"* |
| `desktop_move_mouse` | Move cursor | *"Move the mouse to the center"* |
| `desktop_press_key` | Single key press | *"Press Enter"* |
| `desktop_hotkey` | Key combos | *"Press Alt+Tab"* |
| `file_read` | Read files | *"Read the README file"* |
| `file_write` | Write files | *"Save 'hello' to notes.txt"* |
| `file_list` | List directory | *"What's on my desktop?"* |
| `file_delete` | Delete files | *"Delete temp.txt"* |
| `process_list` | List processes | *"What's running?"* |
| `process_kill` | Kill process | *"Close Chrome"* |
| `system_info` | CPU, RAM, disk | *"How's my system doing?"* |
| `window_list` | List open windows | *"What windows are open?"* |
| `window_focus` | Switch windows | *"Switch to Notepad"* |
| `window_minimize` | Minimize | *"Minimize this window"* |
| `session_list` | Session history | *"Show my sessions"* |
| `session_load` | Resume session | *"Restore my last session"* |

---

### 📚 Knowledge Base

Sentinel loads OS-specific knowledge from `knowledge/*.md` at startup — only the files relevant to your OS, saving tokens.

```
knowledge/
  01-identity.md           Agent persona & voice rules
  02-opening-apps.md       How apps are launched
  03-windows.md            Windows tips & tricks
  04-linux.md              Linux tips & tricks
  05-macos.md              macOS tips & tricks
  06-cross-platform.md     Multi-OS reference
  07-sessions.md           Session management
  08-efficiency.md         Performance optimization
```

Edit or add `.md` files to teach Sentinel new skills — **no code changes needed**.

---

### 💾 Sessions

- Each run creates a timestamped session
- Auto-saved on exit to `sessions/`
- 🎤 *"Restore my last session"* → picks up where you left off
- 💬 `/sessions` lists all saved sessions
- History trimmed to 12 messages to save tokens

---

### ⚡ Token Optimization

| Technique | Savings |
|-----------|---------|
| History trimming (12 msgs) | ~60% fewer tokens |
| OS-specific knowledge | ~40% fewer tokens |
| Anthropic prompt caching | Reuses system prompt |
| TTS response cleaning | Removes emojis & formatting |

---

### 🔌 Supported LLM Providers

| Provider | API Key | Highlights |
|----------|---------|------------|
| 🧠 **DeepSeek** | `DEEPSEEK_API_KEY` | Recommended — fast & affordable |
| 🤖 OpenAI | `OPENAI_API_KEY` | GPT-4o, GPT-4 |
| 🎓 Anthropic | `ANTHROPIC_API_KEY` | Claude, prompt caching |
| 🏠 **Ollama** | *None* | Fully local, zero internet |
| ⚡ Groq | `GROQ_API_KEY` | Ultra-fast inference |
| 🌐 Google | `GOOGLE_API_KEY` | Gemini models |
| 🔀 OpenRouter | `OPENROUTER_API_KEY` | Access to 200+ models |

---

### 🩺 Troubleshooting

| Problem | Solution |
|---------|----------|
| 🎤 Mic not picking up | `python main.py --list-audio` → set `input_device` in config |
| 🔊 No sound | Check `output_device` or use Windows defaults |
| ⬇️ Whisper download | Auto-downloads on first use (~150-500 MB). Use `install.py` to pre-download |
| 🗣️ Piper voice | Download `.onnx` from [Piper releases](https://github.com/rhasspy/piper/releases) |
| 🔑 API errors | Verify key is in `.env`, use `deepseek-v4-flash` (not `deepseek-chat`) |

---

### 🗂️ Project Structure

```
sentinel/
├── main.py                    # 🚀 Entry point + CLI
├── install.py                 # 📦 Interactive installer
├── sentinel_service.py        # 🪟 Background service
├── sentinelw.pyw              # 🪟 No-console launcher
├── config.yaml                # ⚙️ Configuration
├── requirements.txt           # 📋 Dependencies
├── knowledge/                 # 📚 Agent knowledge (.md)
├── sentinel/
│   ├── core.py                # 🔄 Main loop, tools, push-to-talk
│   ├── config.py              # 📄 YAML + .env loader
│   ├── sessions.py            # 💾 Session manager
│   ├── agent/
│   │   ├── llm.py             # 🧠 LLM engine, knowledge loading
│   │   └── prompts.py         # 💬 System prompt builder
│   ├── actions/
│   │   ├── terminal.py        # ⌨️ Terminal & app launcher
│   │   ├── desktop.py         # 🖱️ Mouse, keyboard, screenshots
│   │   ├── files.py           # 📁 File operations
│   │   ├── processes.py       # 📊 Process management
│   │   └── windows.py         # 🪟 Window management
│   ├── providers/             # 🔌 LLM providers (OpenAI, Anthropic, DeepSeek...)
│   ├── safety/
│   │   ├── permissions.py     # 🔐 Permission manager
│   │   └── sandbox.py         # 🏖️ Execution sandbox
│   ├── voice/
│   │   ├── wakeword.py        # 🎯 Wake word detection
│   │   ├── stt.py             # 🎤 Speech-to-text (Whisper)
│   │   └── tts.py             # 🔊 Text-to-speech
│   └── ui/
│       └── indicator.py       # 🟢 System tray indicator
```

---

<a name="espanol"></a>
## 🌐 Español

### 🤖 Qué es Sentinel

Sentinel es un agente de IA que convierte tu voz en acciones sobre el ordenador. Le hablas — y él hace clic, escribe, abre aplicaciones, gestiona archivos, ejecuta comandos y controla ventanas por ti.

Sin ratón. Sin teclado. Sin pantalla. **Tú hablas. Sentinel actúa.**

| 🎯 Caso de uso | 💬 Solo di... |
|---------------|---------------|
| Abrir apps | *"Abre Chrome y ve a YouTube"* |
| Archivos | *"Crea una carpeta Proyecto en el escritorio"* |
| Sistema | *"Cuánta RAM tengo libre?"* |
| Ventanas | *"Minimiza todas las ventanas"* |
| Búsquedas | *"Busca en Google el tiempo en Madrid"* |
| Terminal | *"Dime mi dirección IP"* |
| Teclado | *"Pulsa Control+Shift+Escape"* |
| Procesos | *"Cierra Spotify"* |

---

### ⚡ Instalación Rápida

La forma más rápida — **un solo comando lo hace todo**:

```bash
git clone https://github.com/jsabnor/sentinel.git
cd sentinel
python install.py
```

### 🧙 Lo que hace el instalador por ti

`install.py` es una experiencia guiada completa. NUNCA te deja con una configuración a medias:

| Paso | Qué ocurre |
|------|-----------|
| 1. 📦 | **Dependencias Python** — instala todo desde `requirements.txt` vía pip |
| 2. 🧠 | **Proveedor LLM** — elige DeepSeek, OpenAI, Ollama... Pega tu API key |
| 3. 🎤 | **Configuración de voz** — elige tamaño de Whisper (`tiny` a `large`) y motor TTS (pyttsx3, Piper, Edge) |
| 4. ⬇️ | **Descarga Whisper** — reconocimiento de voz offline (~150 MB `base`, ~500 MB `small`) |
| 5. 🗣️ | **Descarga voz Piper** — voz neuronal en español/inglés opcional (~30 MB) |
| 6. 🔐 | **Permisos** — configura modo de seguridad (`auto` / `ask` / `deny`) y palabras de activación |
| 7. 📝 | **Crea configuración** — genera `.env` + `config.yaml` listos para usar |
| 8. 🪟 | **Servicio Windows** — opcional: instala Sentinel como servicio que arranca solo al iniciar sesión |

### 🚀 Después de instalar

```bash
start_sentinel.bat        # Windows — arranca inmediatamente
```

O si instalaste el servicio — se lanza automáticamente cada vez que inicias sesión. **No necesitas volver a abrir un terminal nunca más.**

> 🏠 **Voz 100% local.** Whisper para reconocimiento, Piper/pyttsx3 para habla.  
> Sin APIs de voz en la nube. Solo el LLM necesita internet — o nada si usas Ollama local.

### 📦 Instalación manual (alternativa)

```bash
pip install -r requirements.txt
# Copia .env.example a .env y añade tu API key
# Personaliza config.yaml a tu gusto
python main.py
```

---

### 🪟 Servicio en Segundo Plano — Instala una vez, funciona siempre

El instalador te ofrece configurar Sentinel como **servicio en segundo plano de Windows**. Si aceptas:

- ✅ Sentinel arranca **automáticamente** cada vez que inicias sesión en Windows
- ✅ Sin ventana de consola — solo un 🟢 **icono verde** en la bandeja del sistema
- ✅ `F9` funciona **globalmente** desde cualquier aplicación
- ✅ `Ctrl+Alt+Q` cierra el servicio cuando quieras
- ✅ Las respuestas se escuchan por los altavoces

| SO | Comando de instalación | Iniciar | Parar |
|----|----------------------|---------|-------|
| 🪟 **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` o auto | `stop_sentinel.bat` o `Ctrl+Alt+Q` |
| 🐧 **Linux** | `bash install_service.sh` | Auto (systemd) | `systemctl --user stop sentinel` |
| 🍏 **macOS** | `bash install_service.sh` | Auto (launchd) | `launchctl unload ~/Library/LaunchAgents/com.sentinel.agent.plist` |

> 💡 **Truco:** Puedes instalar el servicio más tarde ejecutando el comando de arriba, o volviendo a lanzar `python install.py` y diciendo "Sí" a la pregunta del servicio.

---

### 🎮 Uso

```bash
python main.py                 # 🎤 Modo voz (push-to-talk)
python main.py chat            # 💬 Modo chat por texto
python main.py --help          # 📋 Ver todas las opciones
python main.py --list-audio    # 🎧 Listar dispositivos de audio
python main.py --list-sessions # 📂 Ver sesiones guardadas
```

#### 🎤 Push-to-Talk

| Tecla | Acción |
|-------|--------|
| `F9` | Empezar/parar grabación (configurable) |
| `Ctrl+Alt+Q` | Salir de Sentinel |

**Cómo funciona:** Pulsa `F9` → habla tu comando → pulsa `F9` otra vez → Sentinel procesa y responde por voz.

#### 💬 Comandos del chat

| Comando | Descripción |
|---------|-------------|
| `/exit` | 🚪 Salir |
| `/voice` | 🎤 Cambiar a modo voz |
| `/provider` | 🧠 Ver proveedor LLM actual |
| `/mode ask\|auto\|deny` | 🔐 Cambiar modo de permisos |
| `/sessions` | 📂 Listar sesiones guardadas |
| `/help` | ❓ Mostrar ayuda |

---

### 🗣️ Pipeline de Voz (100% Local)

| Componente | Motor | Detalles |
|-----------|-------|----------|
| 🎯 Activación | Whisper `tiny` | Rápido, pocos recursos |
| 🎤 Voz → Texto | Whisper `base`/`small` | Offline, multi-idioma |
| 🔊 Texto → Voz | pyttsx3 / Piper / Edge | TTS neuronal sin internet |

---

### ⚙️ Configuración (`config.yaml`)

```yaml
llm:
  provider: deepseek              # openai, anthropic, ollama, groq, google, openrouter
  model: deepseek-v4-flash
  temperature: 0.4

voice:
  input_device: null              # null = micrófono por defecto
  output_device: null             # null = altavoces por defecto
  stt:
    engine: whisper
    language: es                  # en, es, fr, de...
    model: small                  # tiny / base / small / medium / large
  tts:
    engine: piper                 # pyttsx3, piper, edge
    piper:
      model_path: "models/piper/es_ES-carlfm-x_low/es_ES-carlfm-x_low.onnx"
  activation: pushtotalk          # wakeword, pushtotalk, always
  wake_words: [sentinel]
  push_to_talk_key: f9
  quit_key: ctrl+alt+q

safety:
  default_mode: auto              # ask → pedir permiso | auto → confiar | deny → bloquear
  permissions:
    terminal:
      blocked_commands: [rm -rf /, format, diskpart]
    files:
      blocked_paths: [C:\Windows, /etc, /boot]
  high_risk_patterns: [delete, remove, shutdown, kill]

desktop:
  screenshot_quality: 80
  mouse_speed: 0.3

logging:
  level: INFO
```

---

### 🧰 Capacidades — Lo que Sentinel puede hacer por ti

| 🛠️ Herramienta | 📝 Descripción | 💬 Ejemplo |
|----------------|---------------|-----------|
| `terminal_execute` | Ejecutar comandos | *"Instala requests con pip"* |
| `desktop_screenshot` | Captura de pantalla | *"Muéstrame lo que hay en pantalla"* |
| `desktop_click` | Clic en coordenadas | *"Haz clic en el botón Inicio"* |
| `desktop_type` | Escribir texto | *"Escribe Hola Mundo en el Bloc de notas"* |
| `desktop_move_mouse` | Mover cursor | *"Mueve el ratón al centro"* |
| `desktop_press_key` | Pulsar tecla | *"Pulsa Enter"* |
| `desktop_hotkey` | Combinación | *"Pulsa Alt+Tab"* |
| `file_read` | Leer archivo | *"Léeme el archivo README"* |
| `file_write` | Escribir archivo | *"Guarda 'hola' en notas.txt"* |
| `file_list` | Listar directorio | *"Qué hay en el escritorio?"* |
| `file_delete` | Borrar archivo | *"Borra temp.txt"* |
| `process_list` | Listar procesos | *"Qué programas están abiertos?"* |
| `process_kill` | Matar proceso | *"Cierra Chrome"* |
| `system_info` | CPU, RAM, disco | *"Cómo va el sistema?"* |
| `window_list` | Ventanas abiertas | *"Qué ventanas tengo?"* |
| `window_focus` | Cambiar ventana | *"Ve al Bloc de notas"* |
| `window_minimize` | Minimizar | *"Minimiza esta ventana"* |
| `session_list` | Historial | *"Muéstrame mis sesiones"* |
| `session_load` | Restaurar | *"Restaura mi última sesión"* |

---

### 📚 Base de Conocimiento

Sentinel carga conocimiento específico para tu SO desde `knowledge/*.md` — solo los archivos relevantes, ahorrando tokens.

```
knowledge/
  01-identity.md           Identidad del agente
  02-opening-apps.md       Cómo se abren aplicaciones
  03-windows.md            Administración de Windows
  04-linux.md              Administración de Linux
  05-macos.md              Administración de macOS
  06-cross-platform.md     Referencia multi-OS
  07-sessions.md           Gestión de sesiones
  08-efficiency.md         Optimización de rendimiento
```

Edita o añade `.md` para enseñarle cosas nuevas — **sin tocar código**.

---

### 💾 Sesiones

- Cada ejecución crea una sesión con timestamp
- Se guarda automáticamente al salir en `sessions/`
- 🎤 *"Restaura mi última sesión"* → continúa donde lo dejaste
- 💬 `/sessions` lista todas las sesiones
- Historial recortado a 12 mensajes para ahorrar tokens

---

### ⚡ Optimización de Tokens

| Técnica | Ahorro |
|---------|--------|
| Recorte de historial (12 msgs) | ~60% menos tokens |
| Conocimiento por SO | ~40% menos tokens |
| Caching de Anthropic | Reutiliza system prompt |
| Limpieza TTS | Elimina emojis y formato |

---

### 🔌 Proveedores LLM

| Proveedor | API Key | Destaca por |
|-----------|---------|------------|
| 🧠 **DeepSeek** | `DEEPSEEK_API_KEY` | Recomendado — rápido y económico |
| 🤖 OpenAI | `OPENAI_API_KEY` | GPT-4o, GPT-4 |
| 🎓 Anthropic | `ANTHROPIC_API_KEY` | Claude + prompt caching |
| 🏠 **Ollama** | *Ninguna* | 100% local, sin internet |
| ⚡ Groq | `GROQ_API_KEY` | Inferencia ultrarrápida |
| 🌐 Google | `GOOGLE_API_KEY` | Modelos Gemini |
| 🔀 OpenRouter | `OPENROUTER_API_KEY` | Acceso a +200 modelos |

---

### 🩺 Solución de Problemas

| Problema | Solución |
|----------|----------|
| 🎤 No captura el micro | `python main.py --list-audio` → configura `input_device` |
| 🔊 No se oye nada | Revisa `output_device` o usa los de Windows por defecto |
| ⬇️ Descarga Whisper | Auto-descarga en primer uso (~150-500 MB). Pre-descarga con `install.py` |
| 🗣️ Voz Piper | Descarga `.onnx` de [Piper releases](https://github.com/rhasspy/piper/releases) |
| 🔑 Errores API | Verifica la key en `.env`, usa `deepseek-v4-flash` (no `deepseek-chat`) |

---

### 🗂️ Estructura del Proyecto

```
sentinel/
├── main.py                    # 🚀 Entrada + CLI
├── install.py                 # 📦 Instalador interactivo
├── sentinel_service.py        # 🪟 Servicio en segundo plano
├── sentinelw.pyw              # 🪟 Lanzador sin consola
├── config.yaml                # ⚙️ Configuración
├── requirements.txt           # 📋 Dependencias
├── knowledge/                 # 📚 Conocimiento del agente (.md)
├── sentinel/
│   ├── core.py                # 🔄 Bucle principal, herramientas
│   ├── config.py              # 📄 Cargador YAML + .env
│   ├── sessions.py            # 💾 Gestor de sesiones
│   ├── agent/
│   │   ├── llm.py             # 🧠 Motor LLM, carga de conocimiento
│   │   └── prompts.py         # 💬 Constructor de system prompt
│   ├── actions/
│   │   ├── terminal.py        # ⌨️ Terminal y lanzador de apps
│   │   ├── desktop.py         # 🖱️ Ratón, teclado, capturas
│   │   ├── files.py           # 📁 Operaciones con archivos
│   │   ├── processes.py       # 📊 Gestión de procesos
│   │   └── windows.py         # 🪟 Gestión de ventanas
│   ├── providers/             # 🔌 OpenAI, Anthropic, DeepSeek, Ollama...
│   ├── safety/
│   │   ├── permissions.py     # 🔐 Gestor de permisos
│   │   └── sandbox.py         # 🏖️ Sandbox de ejecución
│   ├── voice/
│   │   ├── wakeword.py        # 🎯 Detección de activación
│   │   ├── stt.py             # 🎤 Voz a texto (Whisper)
│   │   └── tts.py             # 🔊 Texto a voz
│   └── ui/
│       └── indicator.py       # 🟢 Indicador en bandeja del sistema
```
