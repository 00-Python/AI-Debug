from transformers import pipeline
from typing import Dict, Generator, List
from .base_client import BaseClient

class OpenSourceClient(BaseClient):
    def __init__(self) -> None:
        self.pipeline = pipeline('text-generation')

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-2",
        temperature: float = 1,
        top_probability: float = 1,
    ) -> Generator[str, None, None]:
        prompt = "\n".join(message["content"] for message in messages)
        result = self.pipeline(prompt, model=model, temperature=temperature, top_k=top_probability, return_full_text=False)
        yield result[0]['generated_text']