import json
import logging

from sentinel.providers.base import BaseProvider

log = logging.getLogger("sentinel.providers.google")

try:
    import google.generativeai as genai
    HAS_GOOGLE = True
except ImportError:
    HAS_GOOGLE = False


class GoogleProvider(BaseProvider):
    def __init__(self, config: dict):
        super().__init__(config)
        if not HAS_GOOGLE:
            raise ImportError("google-generativeai package required: pip install google-generativeai")

        provider_config = config.get("providers", {}).get("google", {})
        genai.configure(api_key=provider_config.get("api_key", config.get("api_key")))
        self.model = provider_config.get("model", "gemini-2.5-flash")
        self.client = genai.GenerativeModel(self.model)

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        contents = []
        system = ""

        for msg in messages:
            role = msg["role"]
            if role == "system":
                system = msg["content"]
            elif role == "user":
                contents.append({"role": "user", "parts": [msg["content"]]})
            elif role == "assistant":
                parts = [msg["content"]] if msg.get("content") else []
                contents.append({"role": "model", "parts": parts})
            elif role == "tool":
                contents.append({"role": "user", "parts": [f"Tool result: {msg['content']}"]})

        if system:
            contents.insert(0, {"role": "user", "parts": [system]})

        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }

        if tools:
            gemini_tools = []
            for t in tools:
                func = t.get("function", t)
                gemini_tools.append({
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "parameters": func.get("parameters", {}),
                })
            self.client = genai.GenerativeModel(
                self.model,
                tools=gemini_tools,
            )

        response = self.client.generate_content(
            contents,
            generation_config=generation_config,
        )

        result = {"content": ""}
        tool_calls = []

        for part in response.parts:
            if part.text:
                result["content"] += part.text
            elif hasattr(part, "function_call") and part.function_call:
                tool_calls.append({
                    "name": part.function_call.name,
                    "arguments": dict(part.function_call.args),
                    "id": f"call_{len(tool_calls)}",
                })

        if tool_calls:
            result["tool_calls"] = tool_calls

        return result
