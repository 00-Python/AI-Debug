import os
from typing import Dict, Generator, List

from google.generativeai import configure, GenerativeModel
from .base_client import BaseClient

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
DISABLE_STREAMING = os.getenv("DISABLE_STREAMING", "false").lower() == "true"

class GoogleClient(BaseClient):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.api_host = "https://geminai.googleapis.com"  # Example API host, update as necessary
        configure(api_key=self.api_key)
        self.model = GenerativeModel('gemini-1.5-pro')

    def _request(self, messages: List[Dict[str, str]], is_chat: bool = False) -> Generator[str, None, None]:
        prompt = "\n".join(message["content"] for message in messages)

        response = self.model.chat(prompt) if is_chat else self.model.generate_content(prompt)
        yield response.text

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-1.5-pro",
        temperature: float = 1,
        top_probability: float = 1,
        is_chat: bool = False,
    ) -> Generator[str, None, None]:
        if model:
            self.model = GenerativeModel(model)
        yield from self._request(messages, is_chat=is_chat)