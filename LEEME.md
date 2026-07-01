# Sentinel v1.1.0 - Agente de IA para SO

> Agente de IA controlado por voz para la gestión completa del sistema operativo.
> Diseñado para accesibilidad universal — usable por cualquier persona, sin importar edad o capacidad.

[English](README.md) | Español

---

## Qué es Sentinel

Sentinel es un agente de IA controlado por voz que gestiona tu sistema operativo. Abre aplicaciones, busca en internet, gestiona archivos, controla el escritorio, lee tu pantalla y te guía paso a paso — todo por voz. Diseñado para accesibilidad universal.

## Inicio Rápido

```bash
git clone <repo-url> sentinel
cd sentinel
python install.py
```

El instalador configura todo: dependencias, API keys, modelos de voz, y opcionalmente instala Sentinel como servicio en segundo plano que arranca con el SO.

## Uso

| Acción | Cómo |
|--------|------|
| **Push-to-talk** (por defecto) | Pulsa **F9**, habla, suelta. El agente responde y auto-escucha 4s para seguir la conversación. |
| **Modo chat** | `python main.py chat` |
| **Servicio en segundo plano** | `start_sentinel.bat` (Windows) — sin consola, arranca con el SO |
| **Listar sesiones** | `python main.py --list-sessions` |
| **Listar dispositivos** | `python main.py --list-audio` |

## Pipeline de Voz (100% Local)

| Etapa | Motor | Notas |
|-------|-------|-------|
| Voz a Texto | Whisper (`small` recomendado) | Sin conexión, español |
| Texto a Voz | Piper / pyttsx3 / Edge | TTS neuronal offline |
| Captura de audio | sounddevice | Auto-detecta frecuencia del dispositivo |

## Configuración (`config.yaml`)

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
  conversation_timeout: 4     # Segundos de auto-escucha tras respuesta (0 = desactivado)
  wake_words: [sentinel, centinela]
  wakeword_model: tiny
  input_device: null          # Micrófono (null = predeterminado de Windows)
  output_device: null         # Altavoces
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

## Funcionalidades de Accesibilidad

| Funcionalidad | Descripción |
|---------------|-------------|
| **Control por voz** | Manejo completo del PC sin teclado ni ratón |
| **Sonidos de estado** | Beep al escuchar (F9 pulsado), doble chime al terminar |
| **Indicador visual** | Barra superior derecha: "En espera", "REC Escuchando", "Procesando", "Respondiendo" |
| **Perfiles de usuario** | `child` (vocabulario simple, protección extra), `standard`, `expert` (conciso) |
| **Modo conversación** | Auto-escucha 4s tras cada respuesta para seguir el diálogo |
| **Lectura de pantalla** | "¿Qué hay en pantalla?" — describe ventanas y contenido |
| **Workflows guiados** | Paso a paso para email, búsquedas, clima, archivos |
| **Limpieza de voz** | Respuestas sin emojis, markdown ni formato para TTS natural |
| **Sesiones** | Guardar y restaurar conversaciones por voz o chat |
| **Recuperación de errores** | Explicaciones claras habladas. Logs de crash para depuración |

## Capacidades (17 Herramientas)

`terminal_execute`, `desktop_screenshot`, `desktop_read_screen`, `desktop_click`, `desktop_type`, `desktop_move_mouse`, `desktop_press_key`, `desktop_hotkey`, `file_read`, `file_write`, `file_list`, `file_delete`, `process_list`, `process_kill`, `system_info`, `window_list`, `window_focus`, `window_minimize`, `session_list`, `session_load`

## Servicio en Segundo Plano

| SO | Instalar | Control |
|----|---------|---------|
| **Windows** | `powershell -File install_service.ps1` | `start_sentinel.bat` / `stop_sentinel.bat` |
| **Linux** | `bash install_service.sh` | `systemctl --user start/stop sentinel` |
| **macOS** | `bash install_service.sh` | `launchctl load/unload` |

Sin ventana de consola. F9 funciona desde cualquier aplicación. Ctrl+Alt+Q para salir.

## Proveedores LLM Soportados

| Proveedor | Modelo | Notas |
|----------|-------|-------|
| DeepSeek | `deepseek-v4-flash` | Recomendado |
| OpenAI | `gpt-4o` | Caching automático |
| Anthropic | `claude-sonnet-4` | Caching vía `cache_control` |
| Ollama | `llama3` | Local, sin API key |
| Groq | `llama-3.3-70b` | Inferencia rápida |
| Google | `gemini-2.5-flash` | API Gemini |
| OpenRouter | `openai/gpt-4o` | Multi-proveedor |
| MiniMax | `abab7-chat` | |
| OpenCode | | |

## Base de Conocimiento

El conocimiento del agente está en archivos Markdown editables en `knowledge/`:
- `01-identity.md` — Identidad y reglas de voz
- `02-opening-apps.md` — Procedimiento para abrir aplicaciones
- `03-windows.md` — Administración de Windows
- `04-linux.md` — Administración de Linux
- `05-macos.md` — Administración de macOS
- `06-cross-platform.md` — Referencia multiplataforma
- `07-sessions.md` — Gestión de sesiones
- `08-efficiency.md` — Patrones de comandos eficientes
- `09-accessibility.md` — Diseño de accesibilidad universal
- `10-help.md` — Ayuda y onboarding
- `11-workflows.md` — Workflows guiados

---

## Estructura del Proyecto

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
    ├── config.py              # Cargador YAML + .env
    ├── sessions.py            # Guardar/cargar/listar sesiones
    ├── agent/
    │   ├── llm.py             # Motor LLM, carga de conocimiento, caching
    │   └── prompts.py         # System prompt
    ├── actions/
    │   ├── terminal.py        # Shell + lanzamiento de apps
    │   ├── desktop.py         # Ratón, teclado, capturas, lectura de pantalla
    │   ├── files.py           # Operaciones con archivos
    │   ├── processes.py       # Gestión de procesos
    │   └── windows.py         # Gestión de ventanas
    ├── providers/             # 9 proveedores LLM
    ├── safety/
    │   ├── permissions.py     # Gestor de permisos
    │   └── sandbox.py         # Sandbox
    ├── voice/
    │   ├── wakeword.py        # Detección de palabra de activación
    │   ├── stt.py             # Voz a texto (Whisper)
    │   └── tts.py             # Texto a voz (Piper/pyttsx3/Edge)
    └── ui/
        ├── indicator.py       # Indicador visual de estado
        └── sounds.py          # Sonidos de feedback
```
