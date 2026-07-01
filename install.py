#!/usr/bin/env python3
"""
Sentinel - Interactive Installer
=================================
Cross-platform installer that configures Sentinel step by step,
downloads Whisper and Piper models, and generates configuration files.

Usage:
    python install.py            Interactive installation
    python install.py --quiet    Non-interactive with defaults
    python install.py --help     Show help
"""

import os
import sys
import shutil
import subprocess
import json
import urllib.request
import tarfile
import tempfile
import platform
import textwrap
from pathlib import Path

# ── Constants ────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).parent.resolve()
MODELS_DIR = PROJECT_ROOT / "models"
WHISPER_MODELS = ["tiny", "base", "small", "medium", "large"]

PIPER_VOICES = {
    "es": {
        "es_ES-carlfm-x_low": {
            "name": "Carl (Español - España, calidad baja, rápido)",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/x_low/es_ES-carlfm-x_low.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/carlfm/x_low/es_ES-carlfm-x_low.onnx.json",
        },
        "es_MX-claude-high": {
            "name": "Claude (Español - México, calidad alta)",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_MX/claude/high/es_MX-claude-high.onnx.json",
        },
    },
    "en": {
        "en_US-lessac-medium": {
            "name": "Lessac (English - US, medium quality)",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json",
        },
        "en_US-amy-medium": {
            "name": "Amy (English - US, medium quality)",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json",
        },
        "en_US-ryan-high": {
            "name": "Ryan (English - US, high quality)",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json",
        },
        "en_GB-alan-medium": {
            "name": "Alan (English - UK, medium quality)",
            "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx",
            "config_url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json",
        },
    },
}

PROVIDERS = {
    "1": {"id": "openai", "name": "OpenAI (GPT-4o, GPT-4, etc.)", "env_var": "OPENAI_API_KEY", "default_model": "gpt-4o"},
    "2": {"id": "anthropic", "name": "Anthropic (Claude)", "env_var": "ANTHROPIC_API_KEY", "default_model": "claude-sonnet-4-20250514"},
    "3": {"id": "groq", "name": "Groq (fast inference)", "env_var": "GROQ_API_KEY", "default_model": "llama-3.3-70b-versatile"},
    "4": {"id": "deepseek", "name": "DeepSeek", "env_var": "DEEPSEEK_API_KEY", "default_model": "deepseek-v4-flash"},
    "5": {"id": "google", "name": "Google Gemini", "env_var": "GOOGLE_API_KEY", "default_model": "gemini-2.5-flash"},
    "6": {"id": "ollama", "name": "Ollama (local, no API key needed)", "env_var": None, "default_model": "llama3"},
    "7": {"id": "openrouter", "name": "OpenRouter (multi-provider)", "env_var": "OPENROUTER_API_KEY", "default_model": "openai/gpt-4o"},
}

COLORS = {
    "header": "\033[95m",
    "blue": "\033[94m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "red": "\033[91m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def _color(c, text):
    if os.name == "nt":
        return text
    return f"{COLORS.get(c, '')}{text}{COLORS['reset']}"


def _print_header(text):
    border = "=" * 60
    print(f"\n{_color('bold', _color('header', border))}")
    print(_color('bold', f"  {text}"))
    print(f"{_color('bold', _color('header', border))}\n")


def _print_step(n, text):
    print(f"\n{_color('blue', f'[{n}]')} {_color('bold', text)}")


def _print_ok(text):
    print(f"  {_color('green', '[OK]')} {text}")


def _print_warn(text):
    print(f"  {_color('yellow', '[!]')} {text}")


def _print_err(text):
    print(f"  {_color('red', '[X]')} {text}")


def _input(prompt, default=None):
    if default:
        result = input(f"  {prompt} [{default}]: ").strip()
        return result if result else default
    return input(f"  {prompt}: ").strip()


def _input_yesno(prompt, default="y"):
    resp = input(f"  {prompt} (y/n) [{default}]: ").strip().lower()
    if not resp:
        resp = default
    return resp in ("y", "yes", "s", "si", "sí")


def _download_file(url, dest_path, desc=""):
    if desc:
        print(f"  Descargando {desc}...", end=" ", flush=True)
    try:
        urllib.request.urlretrieve(url, dest_path)
        if desc:
            print(_color('green', 'OK'))
        return True
    except Exception as e:
        if desc:
            print(_color('red', f'ERROR: {e}'))
        return False


def _detect_os():
    system = platform.system().lower()
    if system == "windows":
        return "windows"
    elif system == "darwin":
        return "macos"
    else:
        return "linux"


def _check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        _print_err(f"Python 3.10+ required. Current: {version.major}.{version.minor}")
        sys.exit(1)
    _print_ok(f"Python {version.major}.{version.minor}.{version.micro}")


def _check_pip():
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"],
                       capture_output=True, check=True)
        _print_ok("pip disponible")
    except Exception:
        _print_err("pip no encontrado. Instala pip primero.")
        sys.exit(1)


def _run_pip(args, desc=""):
    cmd = [sys.executable, "-m", "pip"] + args
    if desc:
        print(f"  {desc}...", end=" ", flush=True)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            if desc:
                print(_color('green', 'OK'))
            return True
        else:
            if desc:
                print(_color('red', 'ERROR'))
                print(f"    {result.stderr.strip()[-300:]}")
            return False
    except subprocess.TimeoutExpired:
        if desc:
            print(_color('red', 'TIMEOUT'))
        return False


# ── Installation Steps ───────────────────────────────────────────────────────

def install_dependencies():
    _print_step(1, "Instalando dependencias Python")
    requirements = PROJECT_ROOT / "requirements.txt"
    if not requirements.exists():
        _print_err("requirements.txt no encontrado")
        sys.exit(1)
    ok = _run_pip(["install", "-r", str(requirements)], "Instalando paquetes")
    if ok:
        _print_ok("Dependencias instaladas")
    else:
        _print_warn("Algunas dependencias fallaron. Revisa los errores arriba.")
    return ok


def configure_llm():
    _print_step(2, "Configurando proveedor LLM")

    print("\n  Proveedores disponibles:")
    for key, prov in PROVIDERS.items():
        print(f"    {_color('blue', key)}) {prov['name']}")

    default = "1"
    choice = _input("Selecciona un proveedor", default=default)
    if choice not in PROVIDERS:
        choice = default

    provider = PROVIDERS[choice]
    _print_ok(f"Proveedor: {provider['name']}")

    api_key = ""
    if provider["env_var"]:
        api_key = _input(f"API Key ({provider['env_var']})")
        if not api_key:
            _print_warn("No se ingresó API key. Deberás configurarla en .env manualmente.")
    else:
        _print_ok("Ollama no requiere API key")

    model = _input("Modelo", default=provider["default_model"])
    base_url = ""
    if provider["id"] == "ollama":
        base_url = _input("URL base de Ollama", default="http://localhost:11434")

    temperature = _input("Temperature (0.0-1.0)", default="0.7")

    return {
        "provider": provider["id"],
        "model": model,
        "api_key": api_key,
        "env_var": provider["env_var"],
        "base_url": base_url,
        "temperature": float(temperature),
    }


def configure_voice():
    _print_step(3, "Configurando voz (STT + TTS)")

    print()
    lang = _input("Idioma principal (es, en, fr, de...)", default="es")
    whisper_model = _input(
        f"Modelo Whisper ({'/'.join(WHISPER_MODELS)})",
        default="base"
    )
    if whisper_model not in WHISPER_MODELS:
        whisper_model = "base"

    print(f"\n  Motores TTS disponibles:")
    print(f"    {_color('blue', '1)')} pyttsx3 (offline, usa voces del sistema)")
    print(f"    {_color('blue', '2)')} piper (offline, voces neuronales locales)")
    print(f"    {_color('blue', '3)')} edge (solo Windows, voces nativas)")

    tts_choice = _input("Motor TTS", default="1")
    tts_engine = {"1": "pyttsx3", "2": "piper", "3": "edge"}.get(tts_choice, "pyttsx3")

    piper_voice_id = None
    if tts_engine == "piper":
        piper_voice_id = _select_piper_voice(lang)

    print()
    activation = _input("Modo de activación (wakeword/pushtotalk/always)", default="wakeword")
    wake_words = []
    if activation == "wakeword":
        wake_words_str = _input("Palabras de activación (separadas por coma)", default="sentinel,centinela,hey sentinel")
        wake_words = [w.strip() for w in wake_words_str.split(",") if w.strip()]
        wakeword_model = _input("Modelo Whisper para wakeword (tiny recomendado)", default="tiny")

    return {
        "language": lang,
        "whisper_model": whisper_model,
        "tts_engine": tts_engine,
        "piper_voice_id": piper_voice_id,
        "activation": activation,
        "wake_words": wake_words,
        "wakeword_model": locals().get("wakeword_model", "tiny"),
    }


def _select_piper_voice(lang):
    print(f"\n  Voces Piper disponibles para '{lang}':")
    voices = PIPER_VOICES.get(lang, {})
    if not voices:
        voices = PIPER_VOICES.get("en", {})

    voice_list = list(voices.items())
    for i, (vid, vinfo) in enumerate(voice_list, 1):
        print(f"    {_color('blue', str(i))}) {vinfo['name']}")
    print(f"    {_color('blue', str(len(voice_list) + 1))}) Descargar otra manualmente")

    choice = _input("Selecciona una voz", default="1")
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(voice_list):
            return voice_list[idx][0]
    except ValueError:
        pass
    return None


def configure_safety():
    _print_step(4, "Configurando seguridad y permisos")

    print(f"\n  Modos:")
    print(f"    {_color('blue', 'ask')}  - Preguntar antes de cada acción")
    print(f"    {_color('blue', 'auto')} - Ejecutar automáticamente (confianza total)")
    print(f"    {_color('blue', 'deny')} - Bloquear todas las acciones")

    mode = _input("Modo por defecto", default="ask")
    if mode not in ("ask", "auto", "deny"):
        mode = "ask"

    enable_sandbox = _input_yesno("Activar sandbox (restringir comandos y rutas)", default="n")

    return {
        "default_mode": mode,
        "sandbox_enabled": enable_sandbox,
    }


def download_whisper_model(model_name):
    _print_step(5, f"Descargando modelo Whisper '{model_name}'")

    try:
        import whisper
    except ImportError:
        _print_warn("openai-whisper no instalado. Instalando...")
        _run_pip(["install", "openai-whisper"], "Instalando openai-whisper")
        try:
            import whisper
        except ImportError:
            _print_err("No se pudo instalar openai-whisper. El modelo se descargará en el primer uso.")
            return False

    print(f"  Descargando whisper/{model_name} (puede tardar unos minutos)...", end=" ", flush=True)
    try:
        whisper.load_model(model_name)
        print(_color('green', 'OK'))
        _print_ok(f"Modelo whisper/{model_name} listo")
        return True
    except Exception as e:
        print(_color('red', f'ERROR: {e}'))
        _print_warn(f"El modelo se descargará automáticamente en el primer uso de Sentinel.")
        return False


def download_piper_model(voice_id, lang):
    _print_step(6, f"Descargando voz Piper '{voice_id}'")

    voices = PIPER_VOICES.get(lang, PIPER_VOICES.get("en", {}))
    voice_info = voices.get(voice_id)

    if not voice_info:
        _print_warn(f"No se encontró información de descarga para '{voice_id}'.")
        _print_warn("Descarga el modelo manualmente y configura model_path en config.yaml")
        return None

    MODELS_DIR.mkdir(exist_ok=True)
    voice_dir = MODELS_DIR / "piper" / voice_id
    voice_dir.mkdir(parents=True, exist_ok=True)

    model_path = voice_dir / f"{voice_id}.onnx"
    config_path = voice_dir / f"{voice_id}.onnx.json"

    if model_path.exists() and config_path.exists():
        _print_ok(f"Modelo ya descargado: {model_path}")
        return str(model_path)

    ok1 = _download_file(voice_info["url"], model_path, f"{voice_id}.onnx")
    ok2 = _download_file(voice_info["config_url"], config_path, f"{voice_id}.onnx.json")

    if ok1 and ok2:
        _print_ok(f"Voz Piper lista: {model_path}")
        return str(model_path)
    else:
        _print_err("Error descargando el modelo Piper.")
        return None


def generate_env(llm_config):
    _print_step(7, "Generando archivo .env")

    env_path = PROJECT_ROOT / ".env"
    lines = []

    if llm_config["env_var"] and llm_config["api_key"]:
        lines.append(f"{llm_config['env_var']}={llm_config['api_key']}")
        _print_ok(f"{llm_config['env_var']}=... configurado")
    elif llm_config["provider"] != "ollama":
        lines.append(f"# {llm_config['env_var']}=your-key-here")
        _print_warn(f"Agrega tu API key en .env → {llm_config['env_var']}")

    with open(env_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    _print_ok(".env generado")


def _install_windows_service():
    _print_step(9, "Instalando servicio de Windows")
    try:
        script = PROJECT_ROOT / "install_service.ps1"
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            input="i\n", text=True, capture_output=True, timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        if result.returncode == 0:
            _print_ok("Servicio instalado. Sentinel arrancara al iniciar sesion.")
        else:
            _print_warn("No se pudo instalar el servicio. Ejecuta manualmente:")
            _print_warn("  powershell -File install_service.ps1")
    except Exception as e:
        _print_warn(f"No se pudo instalar el servicio: {e}")
        _print_warn("Ejecuta manualmente: powershell -File install_service.ps1")


def _install_unix_service():
    _print_step(9, "Instalando servicio del sistema")
    try:
        script = PROJECT_ROOT / "install_service.sh"
        result = subprocess.run(
            ["bash", str(script)], input="install\n", text=True,
            capture_output=True, timeout=30,
        )
        if result.returncode == 0:
            _print_ok("Servicio instalado. Sentinel arrancara al iniciar sesion.")
        else:
            _print_warn("No se pudo instalar el servicio. Ejecuta manualmente:")
            _print_warn("  bash install_service.sh")
    except Exception as e:
        _print_warn(f"No se pudo instalar el servicio: {e}")
        _print_warn("Ejecuta manualmente: bash install_service.sh")


def generate_config(llm_config, voice_config, safety_config):
    _print_step(8, "Generando config.yaml")

    # Build the YAML manually to preserve structure and comments
    tts_extra = ""
    piper_path = ""
    if voice_config["piper_voice_id"]:
        piper_path = str(MODELS_DIR / "piper" / voice_config["piper_voice_id"] / f"{voice_config['piper_voice_id']}.onnx")
        piper_path = piper_path.replace("\\", "/")
    else:
        piper_path = ""

    wake_words_yaml = "\n".join(f"    - {w}" for w in voice_config["wake_words"]) if voice_config["wake_words"] else "    - sentinel"

    sandbox_enabled = str(safety_config["sandbox_enabled"]).lower()

    config_content = f"""# =============================================================================
# Sentinel - AI OS Agent Configuration
# Generated by install.py
# =============================================================================

llm:
  provider: {llm_config['provider']}
  model: {llm_config['model']}
  temperature: {llm_config['temperature']}
  max_tokens: 4096
  api_key: ${{{llm_config.get('env_var') or 'OPENAI_API_KEY'}}}
  base_url: {'null' if not llm_config.get('base_url') else llm_config['base_url']}

  providers:
    openai:
      api_key: ${{OPENAI_API_KEY}}
    anthropic:
      api_key: ${{ANTHROPIC_API_KEY}}
      model: claude-sonnet-4-20250514
    ollama:
      base_url: http://localhost:11434
      model: llama3
    groq:
      api_key: ${{GROQ_API_KEY}}
      model: llama-3.3-70b-versatile
    deepseek:
      api_key: ${{DEEPSEEK_API_KEY}}
      model: deepseek-v4-flash
    google:
      api_key: ${{GOOGLE_API_KEY}}
      model: gemini-2.5-flash
    openrouter:
      api_key: ${{OPENROUTER_API_KEY}}
      model: openai/gpt-4o
    minimax:
      api_key: ${{MINIMAX_API_KEY}}
      model: abab7-chat
    opencode:
      api_key: ${{OPENCODE_API_KEY}}
      base_url: https://api.opencode.ai/v1

voice:
  enabled: true

  # Audio devices (index or name). List with: python main.py --list-audio
  input_device: null
  output_device: null

  stt:
    engine: whisper
    language: {voice_config['language']}
    model: {voice_config['whisper_model']}
    sample_rate: 16000
    energy_threshold: 800
    pause_threshold: 1.5

  tts:
    engine: {voice_config['tts_engine']}
    rate: 180
    voice: default
    volume: 0.9
    piper:
      model_path: "{piper_path}"
      config_path: null

  activation: {voice_config['activation']}
  wakeword_model: {voice_config['wakeword_model']}
  wake_words:
{wake_words_yaml}
  push_to_talk_key: right ctrl
  quit_key: ctrl+alt+q

safety:
  default_mode: {safety_config['default_mode']}

  permissions:
    terminal:
      mode: auto
      blocked_commands:
        - rm -rf /
        - del /f /s C:\\*
        - format
        - diskpart
    desktop:
      mode: auto
    files:
      mode: auto
      blocked_paths:
        - C:\\Windows
        - C:\\Windows\\System32
        - /etc
        - /boot
    processes:
      mode: auto
      blocked_processes:
        - System
        - svchost
    windows:
      mode: auto

  high_risk_patterns:
    - delete
    - remove
    - shutdown
    - kill

sandbox:
  enabled: {sandbox_enabled}
  allowed_paths: []
  allowed_commands: []
  max_command_timeout: 60

desktop:
  screenshot_quality: 80
  mouse_speed: 0.3
  pause_between_actions: 0.1

logging:
  level: INFO
  file: sentinel.log
  max_size_mb: 10
  backup_count: 3
"""

    config_path = PROJECT_ROOT / "config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config_content)

    _print_ok("config.yaml generado")


def finish(voice_config):
    _print_header("Instalacion completada")
    print(f"""
  {_color('green', 'Sentinel esta listo.')}

  Para iniciar:
    {_color('bold', f'python main.py')}           Modo voz (push-to-talk)
    {_color('bold', f'python main.py chat')}       Modo chat (texto)
    {_color('bold', f'python main.py --help')}     Ver todas las opciones

  Archivos generados:
    .env                  API keys
    config.yaml           Configuracion completa

  Modelos descargados:
    Whisper: {voice_config['whisper_model']}""")

    if voice_config["piper_voice_id"]:
        print(f"    Piper:   {voice_config['piper_voice_id']}")

    print()

    if _detect_os() == "windows":
        print(f"  {_color('yellow', 'Servicio en segundo plano (opcional):')}")
        print(f"    {_color('bold', 'powershell -File install_service.ps1')}")
        print(f"    Sentinel arrancara al iniciar sesion, sin consola.")
    else:
        print(f"  {_color('yellow', 'Servicio en segundo plano (opcional):')}")
        print(f"    {_color('bold', 'bash install_service.sh')}")
        print(f"    Sentinel arrancara al iniciar sesion como daemon.")

    print(f"""
  Si necesitas reconfigurar algo, edita {_color('bold', 'config.yaml')}
  o vuelve a ejecutar {_color('bold', 'python install.py')}.
""")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    _print_header("Sentinel - Instalador interactivo")

    os_name = _detect_os()
    print(f"  Sistema detectado: {_color('bold', os_name.upper())}")

    _check_python()
    _check_pip()

    interactive = "--quiet" not in sys.argv

    if not interactive:
        print("\n  Modo no-interactivo. Usando valores por defecto...\n")
        llm_config = {"provider": "ollama", "model": "llama3", "api_key": "", "env_var": None, "base_url": "http://localhost:11434", "temperature": 0.7}
        voice_config = {"language": "en", "whisper_model": "base", "tts_engine": "pyttsx3", "piper_voice_id": None, "activation": "wakeword", "wake_words": ["sentinel"], "wakeword_model": "tiny"}
        safety_config = {"default_mode": "ask", "sandbox_enabled": False}
    else:
        install_dependencies()
        llm_config = configure_llm()
        voice_config = configure_voice()
        safety_config = configure_safety()

    # Download models
    download_whisper_model(voice_config["whisper_model"])

    if voice_config["piper_voice_id"]:
        download_piper_model(voice_config["piper_voice_id"], voice_config["language"])

    # Generate config files
    generate_env(llm_config)
    generate_config(llm_config, voice_config, safety_config)

    if _detect_os() == "windows":
        if _input_yesno("Instalar Sentinel como servicio (arranca al iniciar sesion)?", default="y"):
            _install_windows_service()
    else:
        if _input_yesno("Instalar Sentinel como servicio (arranca al iniciar sesion)?", default="y"):
            _install_unix_service()

    if interactive:
        finish(voice_config)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{_color('yellow', 'Instalación cancelada.')}")
        sys.exit(0)
