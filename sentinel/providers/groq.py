import logging

from sentinel.providers.base import BaseProvider

log = logging.getLogger("sentinel.providers.groq")

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False


class GroqProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        if not HAS_GROQ:
            raise ImportError("groq package required: pip install groq")

        provider_config = config.get("providers", {}).get("groq", {})
        self.client = Groq(api_key=provider_config.get("api_key", config.get("api_key")))
        self.model = provider_config.get("model", "llama-3.3-70b-versatile")

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
