import json
import logging

from sentinel.providers.base import BaseProvider

log = logging.getLogger("sentinel.providers.anthropic")

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class AnthropicProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        if not HAS_ANTHROPIC:
            raise ImportError("anthropic package required: pip install anthropic")

        provider_config = config.get("providers", {}).get("anthropic", {})
        api_key = provider_config.get("api_key", config.get("api_key"))

        self.client = Anthropic(api_key=api_key)
        self.model = provider_config.get("model", "claude-sonnet-4-20250514")
        self.max_tokens = config.get("max_tokens", 4096)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        system = ""
        chat_messages = []
        use_cache = False

        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
                if msg.get("cache_control"):
                    use_cache = True
            else:
                chat_messages.append(msg)

        if use_cache and system:
            system = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ]

            if chat_messages:
                last_idx = len(chat_messages) - 1
                last_msg = chat_messages[last_idx]
                if isinstance(last_msg.get("content"), str):
                    chat_messages[last_idx] = {
                        **last_msg,
                        "content": [
                            {
                                "type": "text",
                                "text": last_msg["content"],
                                "cache_control": {"type": "ephemeral"},
                            }
                        ],
                    }

        kwargs = {
            "model": self.model,
            "messages": chat_messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }
        if system:
            kwargs["system"] = system
        if tools:
            anthropic_tools = []
            for t in tools:
                func = t.get("function", t)
                anthropic_tools.append({
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "input_schema": {
                        "type": "object",
                        "properties": func.get("parameters", {}).get("properties", {}),
                        "required": func.get("parameters", {}).get("required", []),
                    },
                })
            kwargs["tools"] = anthropic_tools

        response = self.client.messages.create(**kwargs)

        result = {"content": ""}
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "name": block.name,
                    "arguments": block.input,
                    "id": block.id,
                })

        if tool_calls:
            result["tool_calls"] = tool_calls

        return result
