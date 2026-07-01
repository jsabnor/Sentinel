# Sentinel v1.1.0-apple-pie

> 🎙️ Agente de IA controlado por voz para la gestión completa del sistema operativo  
> ♿ Diseñado para accesibilidad universal — usable por cualquier persona, sin importar edad o capacidad

[English](README.md) | Español

---

## 🤖 Qué es Sentinel

Sentinel es un agente de IA controlado por voz que gestiona tu sistema operativo. Tú hablas, él actúa.

- 🖥️ **Abre aplicaciones** — "Abre Spotify", "Abre Chrome"
- 🌐 **Busca en internet** — "Busca restaurantes en Madrid"
- 📂 **Gestiona archivos** — "Crea un documento en el escritorio"
- 📸 **Lee tu pantalla** — "¿Qué hay en pantalla?"
- 🗣️ **Te guía paso a paso** — "Quiero enviar un correo"
- 💬 **Conversación natural** — Te sigue la conversación sin pulsar teclas

---

## ⚡ Inicio Rápido

```bash
git clone https://github.com/jsabnor/Sentinel.git sentinel
cd sentinel
python install.py
```

El instalador configura todo: dependencias, API keys, modelos de voz, y opcionalmente instala Sentinel como servicio en segundo plano que arranca con el SO.

```bash
start_sentinel.bat        # Iniciar servicio en segundo plano (Windows)
python main.py chat        # Modo chat (texto)
```

---

## 🎮 Uso

| Acción | Cómo |
|--------|------|
| **Push-to-talk** | Pulsa **F9**, habla, suelta. Auto-escucha 4s para seguir la conversación. |
| **Modo chat** | `python main.py chat` — interfaz de texto |
| **Servicio en segundo plano** | `start_sentinel.bat` — sin consola, arranca con Windows |
| **Listar dispositivos** | `python main.py --list-audio` |
| **Listar sesiones** | `python main.py --list-sessions` |

**Comandos del chat:** `/exit` `/voice` `/provider` `/mode ask|auto|deny` `/sessions` `/help`

---

## 🔊 Pipeline de Voz — 100% Local

| Etapa | Motor | Notas |
|-------|-------|-------|
| 🎤 **Voz a Texto** | Whisper (`small`) | Sin conexión, multi-idioma |
| 🔊 **Texto a Voz** | Piper / pyttsx3 / Edge | TTS neuronal, offline |
| 🎵 **Captura de audio** | sounddevice | Auto-detecta frecuencia del dispositivo |

> Sin APIs de voz en la nube. Solo el LLM necesita internet — o usa Ollama para funcionar 100% offline.

---

## ♿ Funcionalidades de Accesibilidad

| Funcionalidad | Descripción |
|---------------|-------------|
| 🎙️ **Control total por voz** | Sin necesidad de teclado ni ratón |
| 🔊 **Sonidos de estado** | Beep al empezar a escuchar, doble chime al terminar |
| 📊 **Indicador visual** | Barra superior derecha: "En espera" · "REC Escuchando" · "Procesando" · "Respondiendo" |
| 👶👨‍💻 **Perfiles de usuario** | `child` (infantil, seguro) · `standard` · `expert` (conciso) |
| 💬 **Modo conversación** | Auto-escucha tras cada respuesta para seguir el diálogo |
| 📖 **Lectura de pantalla** | Describe ventanas y contenido por voz |
| 🗺️ **Workflows guiados** | Paso a paso para email, búsquedas, clima, archivos |
| 🧹 **Voz limpia** | Sin emojis, markdown ni formato en la salida de voz |
| 💾 **Sesiones** | Guardar y recuperar conversaciones por voz |
| 🛡️ **Recuperación de errores** | Explicaciones claras habladas, nunca crashes silenciosos |

---

## ⚙️ Configuración (`config.yaml`)

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
  conversation_timeout: 4     # Segundos de auto-escucha tras respuesta
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

## 🧠 Base de Conocimiento

El conocimiento del agente está en archivos Markdown editables en `knowledge/`:

| Archivo | Contenido |
|---------|-----------|
| `01-identity.md` | Identidad, reglas de voz, accesibilidad |
| `02-opening-apps.md` | Procedimiento para abrir aplicaciones |
| `03-windows.md` | Administración de Windows |
| `04-linux.md` | Administración de Linux |
| `05-macos.md` | Administración de macOS |
| `06-cross-platform.md` | Referencia multiplataforma |
| `07-sessions.md` | Gestión de sesiones |
| `08-efficiency.md` | Patrones de comandos eficientes |
| `09-accessibility.md` | Diseño de accesibilidad universal |
| `10-help.md` | Ayuda y onboarding |
| `11-workflows.md` | Workflows guiados |

> Edita o añade archivos `.md` para ampliar el conocimiento sin tocar código.

---

## 🛠️ Herramientas (20)

| Herramienta | Descripción |
|-------------|-------------|
| `terminal_execute` | Ejecutar comandos shell (no bloqueante para apps) |
| `desktop_screenshot` | Capturas de pantalla |
| `desktop_read_screen` | Describir qué hay en pantalla |
| `desktop_click` | Clic en coordenadas |
| `desktop_type` | Escribir texto |
| `desktop_move_mouse` | Mover cursor |
| `desktop_press_key` | Pulsar tecla |
| `desktop_hotkey` | Combinaciones de teclas |
| `file_read` `file_write` `file_list` `file_delete` | Operaciones con archivos |
| `process_list` `process_kill` | Gestión de procesos |
| `system_info` | CPU, RAM, disco |
| `window_list` `window_focus` `window_minimize` | Gestión de ventanas |
| `session_list` `session_load` | Gestión de sesiones |

---

## 🌐 Proveedores LLM Soportados

| Proveedor | Modelo | Notas |
|----------|-------|-------|
| 🚀 **DeepSeek** | `deepseek-v4-flash` | Recomendado |
| 🧠 **OpenAI** | `gpt-4o` | Caching automático |
| 🔮 **Anthropic** | `claude-sonnet-4` | Caching vía `cache_control` |
| 🏠 **Ollama** | `llama3` | Local, sin API key |
| ⚡ **Groq** | `llama-3.3-70b` | Inferencia rápida |
| 🌟 **Google** | `gemini-2.5-flash` | API Gemini |
| 🔗 **OpenRouter** | `openai/gpt-4o` | Multi-proveedor |

---

## 🖥️ Servicio en Segundo Plano

| SO | Instalar | Control |
|----|---------|---------|
| **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` / `stop_sentinel.bat` |
| **Linux** | `bash install_service.sh` | `systemctl --user start/stop sentinel` |
| **macOS** | `bash install_service.sh` | `launchctl load/unload` |

Sin ventana de consola. F9 funciona desde cualquier aplicación. Ctrl+Alt+Q para salir. Arranca automáticamente con el SO.

---

## 📁 Estructura del Proyecto

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

---

## 🐛 Solución de Problemas

| Problema | Solución |
|----------|----------|
| El micrófono no captura | `python main.py --list-audio`, configura `input_device` |
| No se oye nada | Revisa `output_device` o ponlo a `null` para usar el de Windows |
| Descarga del modelo Whisper | Se descarga solo. Pre-descarga: `python install.py` |
| Problemas con Piper | Descarga `.onnx` de [Piper releases](https://github.com/rhasspy/piper/releases) |
| Errores de DeepSeek | API key en `.env`. Usa `deepseek-v4-flash` |
| El servicio no arranca | Ejecuta `check_sentinel.bat`. Revisa `sentinel_service.log` |
