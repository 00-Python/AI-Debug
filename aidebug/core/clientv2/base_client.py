from abc import ABC, abstractmethod
from typing import Dict, Generator, List

class BaseClient(ABC):
    @abstractmethod
    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        top_probability: float
    ) -> Generator[str, None, None]:
        pass