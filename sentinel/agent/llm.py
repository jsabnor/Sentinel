import logging
import sys
from pathlib import Path

from sentinel.providers.base import BaseProvider
from sentinel.agent.prompts import SYSTEM_PROMPT

log = logging.getLogger("sentinel.llm")

_PROVIDER_MAP = {
    "openai": "sentinel.providers.openai.OpenAIProvider",
    "anthropic": "sentinel.providers.anthropic.AnthropicProvider",
    "ollama": "sentinel.providers.ollama.OllamaProvider",
    "groq": "sentinel.providers.groq.GroqProvider",
    "deepseek": "sentinel.providers.deepseek.DeepSeekProvider",
    "google": "sentinel.providers.google.GoogleProvider",
    "minimax": "sentinel.providers.minimax.MiniMaxProvider",
    "opencode": "sentinel.providers.opencode.OpenCodeProvider",
    "openrouter": "sentinel.providers.openrouter.OpenRouterProvider",
}


def _detect_os() -> str:
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "macos"
    return "linux"


def _load_knowledge() -> str:
    knowledge_dir = Path(__file__).parent.parent.parent / "knowledge"
    if not knowledge_dir.is_dir():
        return ""

    current_os = _detect_os()

    core_files = {
        "01-identity.md", "02-opening-apps.md", "06-cross-platform.md",
        "07-sessions.md", "08-efficiency.md", "09-accessibility.md",
        "10-help.md", "11-workflows.md",
    }
    os_files = {
        "windows": {"03-windows.md"},
        "linux": {"04-linux.md"},
        "macos": {"05-macos.md"},
    }

    target_files = core_files | os_files.get(current_os, set())

    parts = []
    for md_file in sorted(knowledge_dir.glob("*.md")):
        if md_file.name not in target_files:
            continue
        try:
            content = md_file.read_text(encoding="utf-8")
            if content.strip():
                parts.append(content)
        except Exception:
            pass

    skipped = len(list(knowledge_dir.glob("*.md"))) - len(parts)
    if skipped > 0:
        log.info("Knowledge loaded: %d files (%d skipped, not for %s)", len(parts), skipped, current_os)

    return "\n\n".join(parts)


_FULL_SYSTEM_PROMPT = SYSTEM_PROMPT + "\n\n" + _load_knowledge()


def get_profile_prompt(profile: str) -> str:
    if profile == "child":
        return """
## CHILD MODE - CRITICAL
You are speaking to a young child. Follow these rules strictly:
- Use very simple words. Short sentences. Like talking to a 5-year-old.
- Be encouraging and playful. Celebrate their successes.
- NEVER suggest anything dangerous, violent, or inappropriate.
- NEVER open social media, messaging apps, or adult content.
- NEVER reveal personal information or passwords.
- If the child asks about something you shouldn't do, gently redirect: "Mejor hagamos otra cosa divertida."
- Suggest educational and creative activities when they don't know what to do.
- Use examples from cartoons, animals, games, and fun topics.
"""
    elif profile == "expert":
        return """
## EXPERT MODE
You are speaking to a technical expert. Be concise and efficient.
- Minimal pleasantries. Direct commands and results.
- Use technical terminology freely.
- Show command outputs directly.
- One sentence confirmations: "Done. Spotify opened."
"""
    return ""


class LLMEngine:
    def __init__(self, config: dict):
        self.config = config
        self.provider_type = config.get("provider", "openai")
        self.model = config.get("model", "gpt-4o")
        self._provider: BaseProvider = None
        self._init_provider()

    def _init_provider(self):
        provider_path = _PROVIDER_MAP.get(self.provider_type)
        if not provider_path:
            raise ValueError(f"Unknown LLM provider: {self.provider_type}")

        module_path, class_name = provider_path.rsplit(".", 1)
        import importlib

        module = importlib.import_module(module_path)
        provider_class = getattr(module, class_name)
        self._provider = provider_class(self.config)
        self.model = self._provider.model
        log.info("LLM provider: %s | model: %s", self.provider_type, self.model)

    def chat(self, messages: list[dict], tools: list[dict] | None = None, profile: str = "standard") -> dict:
        profile_prompt = get_profile_prompt(profile)
        system_content = _FULL_SYSTEM_PROMPT
        if profile_prompt:
            system_content += "\n" + profile_prompt

        system_msg = {"role": "system", "content": system_content}
        self._apply_caching(system_msg)
        full_messages = [system_msg] + messages

        response = self._provider.chat(full_messages, tools=tools)
        return self._normalize(response)

    def _apply_caching(self, system_msg: dict):
        if self.provider_type == "anthropic":
            system_msg["cache_control"] = {"type": "ephemeral"}

        elif self.provider_type == "deepseek":
            system_msg["cache_control"] = {"type": "ephemeral"}

    def _normalize(self, response: dict) -> dict:
        result = {
            "role": "assistant",
            "content": response.get("content", ""),
        }
        if response.get("tool_calls"):
            result["tool_calls"] = response["tool_calls"]
        return result

    def _full_prompt_text(self) -> str:
        return _FULL_SYSTEM_PROMPT
