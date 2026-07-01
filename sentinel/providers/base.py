from abc import ABC, abstractmethod


class BaseProvider(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.model = config.get("model", "")
        self.temperature = config.get("temperature", 0.7)
        self.max_tokens = config.get("max_tokens", 4096)

    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        pass

    @property
    def provider_type(self):
        return self.__class__.__name__.replace("Provider", "").lower()
