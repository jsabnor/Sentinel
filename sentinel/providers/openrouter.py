import json
import logging

from sentinel.providers.base import BaseProvider

log = logging.getLogger("sentinel.providers.openrouter")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class OpenRouterProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        if not HAS_OPENAI:
            raise ImportError("openai package required: pip install openai")

        provider_config = config.get("providers", {}).get("openrouter", {})
        self.client = OpenAI(
            api_key=provider_config.get("api_key", config.get("api_key")),
            base_url=provider_config.get("base_url", "https://openrouter.ai/api/v1"),
        )
        self.model = provider_config.get("model", "openai/gpt-4o")

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
