# Sentinel - Agente de IA para SO

> Agente de IA controlado por voz para la gestión completa del sistema operativo.
> Diseñado para accesibilidad — totalmente utilizable por personas invidentes.

[English](README.md) | Español

---

## Qué es Sentinel

Sentinel es un agente de IA que controla tu sistema operativo mediante voz o texto. Ejecuta comandos de terminal, gestiona archivos, controla el escritorio (ratón, teclado, capturas de pantalla), maneja ventanas y procesos — todo con lenguaje natural.

Tú hablas, Sentinel actúa. Diseñado para accesibilidad.

---

## Instalación Rápida

```bash
git clone <repo-url> sentinel
cd sentinel
python install.py
```

El instalador interactivo te guía por:
1. Instalación de dependencias Python
2. Selección de proveedor LLM y API key
3. Configuración de voz: modelo Whisper + motor TTS (pyttsx3, Piper, Edge)
4. Descarga del modelo Whisper para reconocimiento de voz offline
5. Descarga de voz Piper si se selecciona
6. Palabras de activación y configuración de permisos
7. Generación de `.env` y `config.yaml`

> **Voz 100% local**: Whisper para STT, Piper/pyttsx3 para TTS. Sin APIs de voz en la nube. Solo el LLM necesita internet (salvo que uses Ollama local).

O instalación manual:

```bash
pip install -r requirements.txt
# Crea .env con tu API key
# Edita config.yaml
```

---

## Uso

```bash
python main.py              # Modo voz (push-to-talk)
python main.py chat          # Modo chat (texto)
python main.py --help        # Ver todas las opciones
python main.py --list-audio  # Listar dispositivos de audio
python main.py --list-sessions  # Listar sesiones guardadas
```

**Push-to-talk**: Mantén pulsado `Ctrl+Alt+S`, habla, suelta para enviar. (Configurable en `config.yaml`)

**Comandos del chat**:
| Comando | Descripción |
|---------|-------------|
| `/exit` | Salir |
| `/voice` | Cambiar a modo voz |
| `/provider` | Ver proveedor LLM actual |
| `/mode ask\|auto\|deny` | Cambiar permisos |
| `/sessions` | Listar sesiones guardadas |
| `/help` | Mostrar ayuda |

---

## Pipeline de Voz (100% Local)

| Componente | Motor | Notas |
|-----------|-------|-------|
| Palabra de activación | Whisper `tiny` | Rápido, pocos recursos |
| Voz a Texto | Whisper `base`/`small` | Sin conexión, español |
| Texto a Voz | pyttsx3 / Piper / Edge | TTS neuronal offline |

Auto-detecta la frecuencia de muestreo del dispositivo. Resamplea a 16kHz para Whisper.

---

## Configuración (`config.yaml`)

```yaml
llm:
  provider: deepseek          # openai, anthropic, deepseek, ollama, groq, google, openrouter
  model: deepseek-v4-flash
  temperature: 0.2

voice:
  input_device: null           # Micrófono (null = predeterminado de Windows)
  output_device: null          # Altavoces
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
      mode: auto               # Todo en auto = sin pedir confirmación
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

## Capacidades (Herramientas)

| Herramienta | Descripción |
|-------------|-------------|
| `terminal_execute` | Ejecutar comandos (no bloqueante al abrir apps) |
| `desktop_screenshot` | Capturas de pantalla |
| `desktop_click` | Clic en coordenadas |
| `desktop_type` | Escribir texto |
| `desktop_move_mouse` | Mover cursor |
| `desktop_press_key` | Pulsar tecla |
| `desktop_hotkey` | Combinaciones de teclas |
| `file_read` / `file_write` / `file_list` / `file_delete` | Operaciones con archivos |
| `process_list` / `process_kill` | Gestión de procesos |
| `system_info` | CPU, RAM, disco |
| `window_list` / `window_focus` / `window_minimize` | Gestión de ventanas |
| `session_list` / `session_load` | Gestión de sesiones |

---

## Base de Conocimiento

El conocimiento de administración de SO está en archivos Markdown dentro de `knowledge/`. Se cargan automáticamente al iniciar. Solo se cargan los archivos relevantes para el SO detectado.

```
knowledge/
  01-identity.md       - Identidad, reglas de voz, accesibilidad
  02-opening-apps.md   - Procedimiento para abrir apps
  03-windows.md        - Administración de Windows
  04-linux.md          - Administración de Linux
  05-macos.md          - Administración de macOS
  06-cross-platform.md - Referencia multiplataforma
  07-sessions.md       - Gestión de sesiones
```

Edita o añade archivos `.md` para ampliar el conocimiento sin tocar código.

---

## Sesiones

- Cada inicio crea una sesión nueva (nombre = timestamp)
- Se guarda automáticamente al salir en `sessions/`
- Por voz: "restaura la sesión anterior" → lista las últimas 5
- Por chat: `/sessions` lista las sesiones guardadas
- El historial se recorta a 12 mensajes para ahorrar tokens

---

## Optimización de Tokens

- **Recorte de historial**: solo últimos 12 mensajes
- **Conocimiento por SO**: solo carga archivos `.md` relevantes (40% menos tokens)
- **Caching de Anthropic**: system prompt cacheado en servidor
- **Limpieza de respuestas**: elimina emojis, markdown y formato antes del TTS

---

### Servicio en Segundo Plano (Sin Consola)

Ejecuta Sentinel sin ventana de consola, accesible desde cualquier aplicacion:

| SO | Instalar | Iniciar | Parar |
|----|---------|-------|------|
| **Windows** | `powershell -File install_service.ps1` | Auto al iniciar, o `start_sentinel.bat` | `stop_sentinel.bat` o `Ctrl+Alt+Q` |
| **Linux** | `bash install_service.sh` | Auto al iniciar (systemd) | `systemctl --user stop sentinel` |
| **macOS** | `bash install_service.sh` | Auto al iniciar (launchd) | `launchctl unload ~/Library/LaunchAgents/com.sentinel.agent.plist` |

Como servicio:
- Sin ventana de consola, solo el indicador verde en pantalla
- Push-to-talk funciona globalmente desde cualquier ventana
- Ctrl+Alt+Q para salir
- Respuestas por voz por los altavoces
- Logs en `sentinel_service.log`

---

## Proveedores LLM Soportados

| Proveedor | API Key | Notas |
|----------|---------|-------|
| DeepSeek | `DEEPSEEK_API_KEY` | Recomendado (deepseek-v4-flash) |
| OpenAI | `OPENAI_API_KEY` | GPT-4o, GPT-4 |
| Anthropic | `ANTHROPIC_API_KEY` | Claude, caching de prompt |
| Ollama | Ninguna | Local, sin internet |
| Groq | `GROQ_API_KEY` | Inferencia rápida |
| Google | `GOOGLE_API_KEY` | Gemini |
| OpenRouter | `OPENROUTER_API_KEY` | Multi-proveedor |

---

## Solución de Problemas

**El micrófono no captura**: Ejecuta `python main.py --list-audio`, encuentra tu dispositivo y configura `input_device` en config.yaml.

**No se oye nada**: Revisa `output_device` en config.yaml. Asegúrate de que los altavoces estén como predeterminados en Windows.

**Descarga del modelo Whisper**: El primer uso descarga automáticamente (~150MB base, ~500MB small). Usa `python install.py` para pre-descargar.

**Voz Piper**: Descarga `.onnx` y `.json` de [Piper releases](https://github.com/rhasspy/piper/releases). Configura `model_path` en config.yaml.

**Errores de DeepSeek**: Asegúrate de que `DEEPSEEK_API_KEY` está en `.env`. El modelo `deepseek-chat` está obsoleto — usa `deepseek-v4-flash`.

---

## Estructura del Proyecto

```
sentinel/
├── main.py                    # Punto de entrada + CLI
├── install.py                 # Instalador interactivo
├── config.yaml                # Configuración
├── requirements.txt           # Dependencias
├── knowledge/                 # Conocimiento del agente (.md editables)
├── sessions/                  # Sesiones guardadas
├── sentinel/
│   ├── core.py                # Bucle principal, herramientas, push-to-talk
│   ├── config.py              # Cargador YAML + .env
│   ├── sessions.py            # Guardar/cargar/listar sesiones
│   ├── agent/
│   │   ├── llm.py             # Motor LLM, carga de conocimiento, caching
│   │   └── prompts.py         # System prompt
│   ├── actions/
│   │   ├── terminal.py        # Ejecución shell + lanzamiento de apps
│   │   ├── desktop.py         # Ratón, teclado, capturas
│   │   ├── files.py           # Operaciones con archivos
│   │   ├── processes.py       # Gestión de procesos
│   │   └── windows.py         # Gestión de ventanas
│   ├── providers/             # OpenAI, Anthropic, DeepSeek, Ollama, etc.
│   ├── safety/
│   │   ├── permissions.py     # Gestor de permisos
│   │   └── sandbox.py         # Sandbox
│   ├── voice/
│   │   ├── wakeword.py        # Detección de palabra de activación
│   │   ├── stt.py             # Voz a texto (Whisper)
│   │   └── tts.py             # Texto a voz (Piper/pyttsx3/Edge)
│   └── ui/
│       └── indicator.py       # Indicador visual de estado
```
