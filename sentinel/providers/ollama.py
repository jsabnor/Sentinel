import json
import logging

from sentinel.providers.base import BaseProvider

log = logging.getLogger("sentinel.providers.ollama")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class OllamaProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        if not HAS_OPENAI:
            raise ImportError("openai package required for Ollama: pip install openai")

        provider_config = config.get("providers", {}).get("ollama", {})
        self.client = OpenAI(
            base_url=provider_config.get("base_url", "http://localhost:11434/v1"),
            api_key="ollama",
        )
        self.model = provider_config.get("model", "llama3")
        self.max_tokens = config.get("max_tokens", 4096)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        msg = choice.message

        result = {"content": msg.content or ""}

        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]

        return result
