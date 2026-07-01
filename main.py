#!/usr/bin/env python3
"""
Sentinel - AI OS Agent
Voice-controlled AI agent for complete operating system management.

Usage:
    sentinel voice              Start in voice mode (default)
    sentinel chat               Start in text/chat mode
    sentinel --help             Show help
"""

import argparse
import sys
import signal

from sentinel.config import load_config
from sentinel.core import SentinelAgent


def list_audio_devices():
    print("\nAudio Devices\n=============")

    # Input devices via sounddevice
    try:
        import sounddevice as sd
        print("\n[SoundDevice] All devices:")
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            io = ""
            if d["max_input_channels"] > 0:
                io += " INPUT"
            if d["max_output_channels"] > 0:
                io += " OUTPUT"
            print(f"  {i}: {d['name']}{io} (hostapi={d['hostapi']})")
    except ImportError:
        print("\n  sounddevice not installed. pip install sounddevice")
    except Exception as e:
        print(f"\n  Error: {e}")

    # PyAudio devices (used by speech_recognition)
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        print(f"\n[PyAudio] Default host API info:")
        info = p.get_host_api_info_by_index(0)
        print(f"  Host API: {info['name']}")
        print(f"  Default input device: {p.get_default_input_device_info()['name']}")
        print(f"  Default output device: {p.get_default_output_device_info()['name']}")
        p.terminate()
    except ImportError:
        pass
    except Exception:
        pass

    print("\nUse the device index or name in config.yaml:")
    print("  voice:")
    print("    input_device: 1           # Mic index or name")
    print("    output_device: \"Speakers\" # Speaker index or name")


def list_saved_sessions():
    from sentinel.sessions import SessionManager
    sm = SessionManager()
    sessions = sm.list_sessions()
    if not sessions:
        print("No saved sessions found.")
        return
    print(f"\nSaved sessions ({len(sessions)}):\n")
    print(f"{'Name':<20} {'Messages':<10} {'Last saved':<22}")
    print("-" * 55)
    for s in sessions:
        print(f"{s['name']:<20} {s['messages']:<10} {s['saved_at'][:19]:<22}")


def main():
    parser = argparse.ArgumentParser(
        prog="sentinel",
        description="Sentinel - AI OS Agent. Control your OS with voice or text.",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="voice",
        choices=["voice", "chat"],
        help="Operating mode: voice (voice-controlled) or chat (text-based)",
    )
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to configuration file",
    )
    parser.add_argument(
        "-p", "--provider",
        default=None,
        help="Override LLM provider from config",
    )
    parser.add_argument(
        "-m", "--model",
        default=None,
        help="Override LLM model from config",
    )
    parser.add_argument(
        "--no-voice",
        action="store_true",
        help="Disable voice output even in voice mode",
    )
    parser.add_argument(
        "--permission-mode",
        default=None,
        choices=["ask", "auto", "deny"],
        help="Override default permission mode",
    )
    parser.add_argument(
        "--list-audio",
        action="store_true",
        help="List available audio input/output devices and exit",
    )
    parser.add_argument(
        "--list-sessions",
        action="store_true",
        help="List saved sessions and exit",
    )
    parser.add_argument(
        "--background",
        action="store_true",
        help="Run in background mode (no console, use pythonw)",
    )

    args = parser.parse_args()

    if args.list_audio:
        list_audio_devices()
        return

    if args.list_sessions:
        list_saved_sessions()
        return

    if args.background:
        print("For background mode, run: pythonw sentinelw.pyw")
        print("Or double-click sentinelw.pyw in File Explorer.")
        print("Or use: start_sentinel.bat")
        return

    config = load_config(args.config)

    if args.provider:
        config["llm"]["provider"] = args.provider
    if args.model:
        config["llm"]["model"] = args.model
    if args.permission_mode:
        config["safety"]["default_mode"] = args.permission_mode

    voice_enabled = args.mode == "voice" and not args.no_voice

    agent = SentinelAgent(config, voice_enabled=voice_enabled)

    def shutdown(sig, frame):
        print("\nShutting down Sentinel...")
        agent.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        if args.mode == "voice":
            agent.run_voice()
        else:
            agent.run_chat()
    except KeyboardInterrupt:
        pass
    finally:
        agent.stop()


if __name__ == "__main__":
    main()
