# 🛡️ Sentinel — Agente de IA para SO

> *"Tu voz. Tu sistema. Tu centinela."*  
> Agente de IA controlado por voz que gestiona tu sistema operativo al completo.  
> Diseñado para accesibilidad ♿ — 100% utilizable por personas con discapacidad visual.

[🌐 English](README.md) · Español

---

## 🤖 Qué es Sentinel

Sentinel es un agente de IA que convierte tu voz en acciones sobre tu ordenador. Le hablas — y él hace clic, escribe, abre aplicaciones, gestiona archivos, ejecuta comandos y controla ventanas por ti.

Sin ratón. Sin teclado. Sin pantalla. **Tú hablas. Sentinel actúa.**

| 🎯 Caso de uso | 💬 Solo di... |
|---------------|---------------|
| 🌐 Abrir apps y webs | *"Abre Chrome y ve a YouTube"* |
| 📁 Archivos y carpetas | *"Crea una carpeta Proyecto en el escritorio"* |
| 💻 Información del sistema | *"Cuánta RAM tengo libre?"* |
| 🪟 Control de ventanas | *"Minimiza todas las ventanas"* |
| 🔍 Búsquedas en internet | *"Busca en Google el tiempo en el Puerto de Santa María"* |
| ⌨️ Comandos de terminal | *"Dime mi dirección IP"* |
| ⌨️ Atajos de teclado | *"Pulsa Control+Shift+Escape"* |
| 📊 Gestión de procesos | *"Cierra Spotify"* |
| 🖱️ Control del ratón | *"Haz clic en el centro de la pantalla"* |
| 📝 Escribir texto | *"Escribe un correo en el Bloc de notas"* |

---

## ⚡ Instalación Rápida

```bash
git clone https://github.com/jsabnor/sentinel.git
cd sentinel
python install.py
```

El instalador interactivo te guía paso a paso:

1. 📦 Instalación de dependencias Python
2. 🧠 Selección de proveedor LLM y API key
3. 🎤 Configuración de voz — modelo Whisper + motor TTS (pyttsx3, Piper, Edge)
4. ⬇️ Descarga del modelo Whisper (~150-500 MB según tamaño)
5. ⬇️ Descarga de voz Piper (opcional, ~30 MB)
6. 🔐 Configuración de palabras de activación y permisos
7. 📝 Generación de `.env` y `config.yaml`
8. 🪟 **Servicio en segundo plano** para auto-inicio con Windows

Después solo ejecuta:

```bash
start_sentinel.bat        # Windows
# O inicia automáticamente al hacer login si elegiste la opción de servicio
```

> 🏠 **Voz 100% local.** Whisper para reconocimiento de voz, Piper/pyttsx3 para habla.  
> Sin APIs de voz en la nube. Solo el LLM necesita internet — o nada si usas Ollama local.

### Instalación manual

```bash
pip install -r requirements.txt
# Copia .env.example a .env y añade tu API key
# Personaliza config.yaml a tu gusto
python main.py
```

---

## 🎮 Uso

```bash
python main.py                 # 🎤 Modo voz (push-to-talk con F9)
python main.py chat            # 💬 Modo chat por texto
python main.py --help          # 📋 Ver todas las opciones disponibles
python main.py --list-audio    # 🎧 Listar dispositivos de audio
python main.py --list-sessions # 📂 Ver sesiones guardadas
```

### 🎤 Push-to-Talk — ¿Cómo funciona?

| Tecla | Acción |
|-------|--------|
| `F9` | Empezar / parar grabación (configurable en `config.yaml`) |
| `Ctrl+Alt+Q` | Salir de Sentinel en cualquier momento |

**Flujo de uso típico:**

1. Pulsa `F9` → Sentinel te escucha 🟢
2. Di tu comando, por ejemplo: *"Abre el navegador y ve a Gmail"*
3. Pulsa `F9` otra vez → Sentinel procesa tu petición
4. Sentinel ejecuta la acción y te responde por voz 🔊

> 💡 *No hace falta mantener pulsada la tecla. Pulsas una vez para empezar, pulsas otra vez para enviar.*

### 💬 Comandos del chat

En modo texto, tienes estos comandos disponibles:

| Comando | Descripción |
|---------|-------------|
| `/exit` | 🚪 Salir de Sentinel |
| `/voice` | 🎤 Cambiar al modo voz (push-to-talk) |
| `/provider` | 🧠 Ver el proveedor LLM actual |
| `/mode ask` | 🔐 Activar modo "preguntar antes de actuar" |
| `/mode auto` | ⚡ Activar modo "ejecutar sin preguntar" |
| `/mode deny` | 🛑 Bloquear todas las acciones |
| `/sessions` | 📂 Listar sesiones guardadas |
| `/help` | ❓ Mostrar esta ayuda |

---

## 🗣️ Pipeline de Voz — ¿Cómo escucha y habla?

Sentinel usa un pipeline de voz completamente offline para máxima privacidad:

| Componente | Motor | Detalles |
|-----------|-------|----------|
| 🎯 Palabra de activación (opcional) | Whisper `tiny` | Rápido, bajo consumo de CPU |
| 🎤 Voz → Texto (STT) | Whisper `base` / `small` | Reconocimiento offline, multi-idioma |
| 🔊 Texto → Voz (TTS) | pyttsx3 / Piper / Edge | Voz neuronal offline, natural |

- **Idiomas soportados:** Español, Inglés, Francés, Alemán, y más.
- **Calidad:** El modelo `small` ofrece un balance óptimo entre precisión y velocidad.
- **Auto-detección:** Sentinel detecta la frecuencia de muestreo de tu micrófono automáticamente.

---

## ⚙️ Configuración (`config.yaml`)

```yaml
llm:
  provider: deepseek              # openai, anthropic, ollama, groq, google, openrouter
  model: deepseek-v4-flash
  temperature: 0.4                # 0 = preciso, 1 = creativo
  max_tokens: 4096

voice:
  input_device: null              # null = micrófono por defecto de Windows
  output_device: null             # null = altavoces por defecto de Windows
  stt:
    engine: whisper
    language: es                  # en, es, fr, de, pt...
    model: small                  # tiny, base, small, medium, large
    sample_rate: 16000
    energy_threshold: 800
    pause_threshold: 1.5
  tts:
    engine: piper                 # pyttsx3, piper, edge
    rate: 180                     # Velocidad del habla
    volume: 0.9
    piper:
      model_path: "models/piper/es_ES-carlfm-x_low/es_ES-carlfm-x_low.onnx"
  activation: pushtotalk          # wakeword, pushtotalk, always
  wake_words: [sentinel]          # Palabras que activan al agente
  push_to_talk_key: f9            # Tecla para push-to-talk
  quit_key: ctrl+alt+q

safety:
  default_mode: auto              # ask → pedir confirmación | auto → confiar | deny → bloquear
  permissions:
    terminal:
      mode: auto
      blocked_commands:           # Comandos bloqueados por seguridad
        - rm -rf /
        - del /f /s C:\*
        - format
        - diskpart
    desktop:
      mode: auto
    files:
      mode: auto
      blocked_paths:              # Rutas protegidas
        - C:\Windows
        - C:\Windows\System32
        - /etc
        - /boot
    processes:
      mode: auto
      blocked_processes:          # Procesos del sistema que no se tocan
        - System
        - svchost
  high_risk_patterns:             # Patrones que activan verificación extra
    - delete
    - remove
    - shutdown
    - kill

sandbox:
  enabled: false                  # Activar para máxima seguridad
  allowed_paths: []
  max_command_timeout: 60

desktop:
  screenshot_quality: 80          # Calidad JPEG de capturas
  mouse_speed: 0.3                # Velocidad del movimiento del ratón

logging:
  level: INFO
  file: sentinel.log
```

---

## 🧰 Capacidades — Lo que Sentinel puede hacer por ti

Esta es la lista completa de herramientas que Sentinel tiene a su disposición:

| 🛠️ Herramienta | 📝 Descripción | 💬 Ejemplo de comando |
|----------------|---------------|----------------------|
| `terminal_execute` | Ejecutar comandos de terminal | *"Instala requests con pip"* |
| `desktop_screenshot` | Capturar la pantalla | *"Haz una captura de pantalla"* |
| `desktop_click` | Hacer clic en coordenadas | *"Haz clic en el botón de Inicio"* |
| `desktop_type` | Escribir texto donde esté el cursor | *"Escribe Hola Mundo en el Bloc de notas"* |
| `desktop_move_mouse` | Mover el ratón | *"Mueve el ratón a la esquina superior derecha"* |
| `desktop_press_key` | Pulsar una tecla | *"Pulsa Escape"* |
| `desktop_hotkey` | Combinación de teclas | *"Haz Alt+Tab para cambiar de ventana"* |
| `file_read` | Leer el contenido de un archivo | *"Léeme el archivo README.md"* |
| `file_write` | Crear o sobrescribir un archivo | *"Guarda 'hola mundo' en notas.txt"* |
| `file_list` | Listar archivos de una carpeta | *"Qué archivos hay en Descargas?"* |
| `file_delete` | Eliminar un archivo | *"Borra el archivo temporal.txt"* |
| `process_list` | Listar procesos en ejecución | *"Qué programas tengo abiertos?"* |
| `process_kill` | Cerrar un proceso por nombre | *"Cierra Google Chrome"* |
| `system_info` | Ver CPU, RAM, disco | *"Cómo va el sistema? Cuánta memoria tengo?"* |
| `window_list` | Listar ventanas abiertas | *"Qué ventanas tengo abiertas?"* |
| `window_focus` | Cambiar a una ventana | *"Llévame a la ventana de VS Code"* |
| `window_minimize` | Minimizar una ventana | *"Minimiza el explorador de archivos"* |
| `session_list` | Listar sesiones anteriores | *"Muéstrame mis sesiones guardadas"* |
| `session_load` | Restaurar una sesión | *"Restaura la sesión de ayer"* |

---

## 🪟 Servicio en Segundo Plano (Sin Consola)

¿Quieres usar Sentinel sin una ventana de consola? El instalador configura un servicio en segundo plano que se inicia con Windows:

| SO | Instalar | Iniciar | Parar |
|----|---------|-------|------|
| 🪟 **Windows** | `powershell -File install_service.ps1` | Auto al iniciar, o `start_sentinel.bat` | `stop_sentinel.bat` o `Ctrl+Alt+Q` |
| 🐧 **Linux** | `bash install_service.sh` | Auto al iniciar (systemd) | `systemctl --user stop sentinel` |
| 🍏 **macOS** | `bash install_service.sh` | Auto al iniciar (launchd) | `launchctl unload ~/Library/LaunchAgents/com.sentinel.agent.plist` |

Cuando funciona como servicio:
- 🟢 Solo un pequeño icono verde en la bandeja del sistema — Sentinel está listo
- 🎤 Pulsa `F9` desde cualquier aplicación para darle órdenes
- ❌ `Ctrl+Alt+Q` para cerrar Sentinel cuando quieras
- 🔊 Las respuestas se escuchan por los altavoces

---

## 📚 Base de Conocimiento

Sentinel no es solo un ejecutor de comandos — tiene conocimiento incorporado sobre cómo administrar sistemas operativos. Este conocimiento vive en archivos Markdown dentro de `knowledge/` y se carga automáticamente según tu SO:

```
knowledge/
├── 01-identity.md           🧠 Identidad del agente, reglas de voz, accesibilidad
├── 02-opening-apps.md       🚀 Procedimiento para abrir aplicaciones correctamente
├── 03-windows.md            🪟 Administración específica de Windows
├── 04-linux.md              🐧 Administración específica de Linux
├── 05-macos.md              🍏 Administración específica de macOS
├── 06-cross-platform.md     🌐 Referencia de comandos multi-plataforma
├── 07-sessions.md           💾 Gestión de sesiones de conversación
└── 08-efficiency.md         ⚡ Consejos de rendimiento y optimización
```

> 💡 **Extensible:** Edita los archivos existentes o añade nuevos `.md` para enseñarle a Sentinel procedimientos específicos para tu flujo de trabajo. **Sin tocar código.**

---

## 💾 Sesiones — Tu historial, siempre a mano

Sentinel recuerda tus conversaciones entre ejecuciones:

- 📅 Cada inicio crea una **sesión nueva** con marca de tiempo
- 💾 Se **guarda automáticamente** al salir en `sessions/`
- 🎤 Di: *"Restaura mi última sesión"* — y continúas donde lo dejaste
- 💬 O usa `/sessions` en modo chat para ver y elegir entre sesiones anteriores
- ✂️ El historial se recorta a los **últimos 12 mensajes** para ahorrar tokens

---

## ⚡ Optimización de Tokens — Más barato, más rápido

Cada token cuesta dinero (o tiempo en local). Sentinel optimiza agresivamente:

| Técnica | Qué hace | Ahorro aprox. |
|---------|----------|---------------|
| ✂️ Recorte de historial | Solo los últimos 12 mensajes van al LLM | ~60% menos tokens |
| 🎯 Conocimiento por SO | Carga solo `.md` de tu sistema operativo | ~40% menos tokens |
| 📦 Caching de Anthropic | System prompt cacheado en servidor | Reutiliza prompt base |
| 🧹 Limpieza TTS | Elimina emojis, markdown y formato extra | Respuestas más limpias |

---

## 🔌 Proveedores LLM Soportados

Elige el cerebro que prefieras. Sentinel se adapta:

| Proveedor | Variable de entorno | Ideal para... |
|-----------|-------------------|---------------|
| 🧠 **DeepSeek** | `DEEPSEEK_API_KEY` | ✅ Recomendado. Rápido, barato, excelente calidad |
| 🤖 **OpenAI** | `OPENAI_API_KEY` | GPT-4o, GPT-4. El estándar de la industria |
| 🎓 **Anthropic** | `ANTHROPIC_API_KEY` | Claude. Prompt caching que ahorra costes |
| 🏠 **Ollama** | *Ninguna* | ✅ 100% local. Sin internet. Privacidad total |
| ⚡ **Groq** | `GROQ_API_KEY` | Inferencia ultrarrápida con hardware especializado |
| 🌐 **Google** | `GOOGLE_API_KEY` | Modelos Gemini. Buena relación calidad/precio |
| 🔀 **OpenRouter** | `OPENROUTER_API_KEY` | Acceso a más de 200 modelos en un solo endpoint |
| 🎯 **MiniMax** | `MINIMAX_API_KEY` | Alternativa económica |
| 💻 **OpenCode** | `OPENCODE_API_KEY` | API especializada en código |

---

## 🩺 Solución de Problemas

| Síntoma | Causa probable | Solución |
|---------|---------------|----------|
| 🎤 No captura el micrófono | Dispositivo incorrecto | `python main.py --list-audio` y configura `input_device` |
| 🔊 No se oyen las respuestas | Altavoces no configurados | Configura `output_device` o usa los predeterminados de Windows |
| ⬇️ Whisper no descarga | Primera ejecución pendiente | Auto-descarga en primer uso (~150MB `base`, ~500MB `small`) |
| 🗣️ Piper no habla | Falta el modelo de voz | Descarga `.onnx` + `.json` de [Piper releases](https://github.com/rhasspy/piper/releases) |
| 🔑 Error de API DeepSeek | Key incorrecta o modelo obsoleto | Verifica `.env`. El modelo `deepseek-chat` está obsoleto — usa `deepseek-v4-flash` |
| 🐌 Respuestas lentas | Modelo Whisper muy grande | Baja a `tiny` o `base` en config.yaml |
| 🛑 No ejecuta comandos | Modo `deny` activado | Cambia a `auto` con `/mode auto` o voz |

---

## 🗂️ Estructura del Proyecto

```
sentinel/
├── 🚀 main.py                    # Punto de entrada + CLI
├── 📦 install.py                 # Instalador interactivo completo
├── 🪟 sentinel_service.py        # Servicio en segundo plano (Windows)
├── 🪟 sentinelw.pyw              # Lanzador sin ventana de consola
├── ⚙️ config.yaml                # Configuración principal
├── 📋 requirements.txt           # Dependencias Python
├── 📚 knowledge/                 # Conocimiento del agente (Markdown)
│   ├── 01-identity.md
│   ├── 02-opening-apps.md
│   ├── 03-windows.md / 04-linux.md / 05-macos.md
│   ├── 06-cross-platform.md
│   ├── 07-sessions.md
│   └── 08-efficiency.md
├── 🛡️ sentinel/
│   ├── core.py                   # 🔄 Bucle principal, herramientas, push-to-talk
│   ├── config.py                 # 📄 Cargador YAML + variables de entorno
│   ├── sessions.py               # 💾 Guardar, cargar y listar sesiones
│   ├── agent/
│   │   ├── llm.py                # 🧠 Motor LLM + carga de conocimiento + caching
│   │   └── prompts.py            # 💬 Constructor del system prompt
│   ├── actions/                  # 🛠️ Herramientas de automatización del SO
│   │   ├── terminal.py           # ⌨️ Ejecución de comandos shell
│   │   ├── desktop.py            # 🖱️ Ratón, teclado, capturas de pantalla
│   │   ├── files.py              # 📁 Lectura/escritura/borrado de archivos
│   │   ├── processes.py          # 📊 Gestión de procesos del sistema
│   │   └── windows.py            # 🪟 Gestión de ventanas
│   ├── providers/                # 🔌 Proveedores LLM
│   │   ├── base.py, openai.py, anthropic.py, deepseek.py
│   │   ├── ollama.py, groq.py, google.py
│   │   └── minimax.py, opencode.py, openrouter.py
│   ├── safety/                   # 🔐 Seguridad y permisos
│   │   ├── permissions.py        # Gestor de permisos por acción
│   │   └── sandbox.py            # Sandbox de ejecución aislada
│   ├── voice/                    # 🎤 Pipeline de voz completo
│   │   ├── wakeword.py           # Detección de palabra de activación
│   │   ├── stt.py                # Voz a texto (Whisper)
│   │   └── tts.py                # Texto a voz (Piper/pyttsx3/Edge)
│   └── ui/
│       └── indicator.py          # 🟢 Indicador visual en bandeja del sistema
├── 📂 sessions/                  # Sesiones guardadas (auto-generado)
├── 📝 sentinel.log               # Archivo de log (auto-generado)
└── 🔑 .env                       # API keys (NO se sube a git)
```
