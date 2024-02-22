import os
import json
from typing import Dict, Generator, List
from gpt4all import GPT4All

class Gpt4allClient():

    def __init__(self, model: str):
        self.model= GPT4All(model)

    def process_prompts(self, prompts: List[Dict[str, str]]):
        pass

    def request(self, 
                prompts: List[str], 
                max_tokens: int, 
                temp: float = 0.7,
                top_k: int=40, 
                top_p: float = 0.4, 
                repeat_penalty: float=1.18, 
                repeat_last_n: int=64, 
                n_batch: int=8, 
                streaming: bool=True):

        results = list()

        for i, prompt in enumerate(prompts):
            for token in self.model.generate(prompt, max_tokens=max_tokens, temp=temp, top_k=top_k, top_p=top_p, repeat_penalty=repeat_penalty, repeat_last_n=repeat_last_n, n_batch=n_batch, streaming=streaming):
                print(token)
                results.append(token)
        
        return results

    def get_completion(self):
        pass


if __name__ == "__main__":
    model = Gpt4allClient("orca-mini-3b-gguf2-q4_0.gguf")

    prompts = [
        "Hello Make me a python code that solves ceaser cipher",
        "Make me a python code that counts down from 10 and goes boom and makes the terminal flash"
    ]

    model.request(prompts=prompts, max_tokens=200)
