import os
import json
import requests
from typing import Dict, Generator, List

from .base_client import BaseClient

REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
DISABLE_STREAMING = os.getenv("DISABLE_STREAMING", "false").lower() == "true"

class OpenAIClient(BaseClient):
    def __init__(self, api_host: str, api_key: str) -> None:
        self.__api_key = api_key
        self.api_host = api_host

    def _request(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        top_probability: float
    ) -> Generator[str, None, None]:
        data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "top_p": top_probability,
            "stream": not DISABLE_STREAMING,
        }
        endpoint = f"{self.api_host}/v1/chat/completions"
        response = requests.post(
            endpoint,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__api_key}",
            },
            json=data,
            timeout=REQUEST_TIMEOUT,
            stream=not DISABLE_STREAMING,
        )
        response.raise_for_status()
        if not DISABLE_STREAMING:
            for line in response.iter_lines():
                data = line.lstrip(b"data: ").decode("utf-8")
                if data == "[DONE]":
                    break
                if data:
                    yield json.loads(data)["choices"][0].get("delta", {}).get("content", "")
        else:
            yield response.json()['choices'][0]['message']['content']

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 1,
        top_probability: float = 1,
    ) -> Generator[str, None, None]:
        yield from self._request(
            messages,
            model,
            temperature,
            top_probability,
        )