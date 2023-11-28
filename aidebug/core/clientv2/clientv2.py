'''Credit to TheR1D for original code - https://github.com/TheR1D/shell_gpt/blob/main/sgpt/client.py'''

'''
MIT License

Copyright (c) 2023 Farkhod Sadykov

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import os
import json
from pathlib import Path
from typing import Dict, Generator, List

import requests


REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))
DISABLE_STREAMING = os.getenv("DISABLE_STREAMING", "false")


class OpenAIClient:

    def __init__(self, api_host: str, api_key: str) -> None:
        self.__api_key = api_key
        self.api_host = api_host

    def _request(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 1,
        top_probability: float = 1,
    ) -> Generator[str, None, None]:
        """
        Make request to OpenAI API, read more:
        https://platform.openai.com/docs/api-reference/chat

        :param messages: List of messages {"role": user or assistant, "content": message_string}
        :param model: String gpt-3.5-turbo or gpt-3.5-turbo-0301
        :param temperature: Float in 0.0 - 2.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :return: Response body JSON.
        """
        stream = DISABLE_STREAMING == "false"
        data = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "top_p": top_probability,
            "stream": stream,
        }
        endpoint = f"{self.api_host}/v1/chat/completions"
        response = requests.post(
            endpoint,
            # Hide API key from Rich traceback.
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.__api_key}",
            },
            json=data,
            timeout=REQUEST_TIMEOUT,
            stream=stream,
        )
        response.raise_for_status()
        # TODO: Optimise.
        # https://github.com/openai/openai-python/blob/237448dc072a2c062698da3f9f512fae38300c1c/openai/api_requestor.py#L98
        if not stream:
            data = response.json()
            yield data['choices'][0]['message']['content']  # type: ignore
            return
        for line in response.iter_lines():
            data = line.lstrip(b"data: ").decode("utf-8")
            if data == "[DONE]":  # type: ignore
                break
            if not data:
                continue
            data = json.loads(data)  # type: ignore
            delta = data["choices"][0]["delta"]  # type: ignore
            if "content" not in delta:
                continue
            yield delta['content']

    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 1,
        top_probability: float = 1,
    ) -> Generator[str, None, None]:
        """
        Generates single completion for prompt (message).

        :param messages: List of dict with messages and roles.
        :param model: String gpt-3.5-turbo or gpt-3.5-turbo-0301.
        :param temperature: Float in 0.0 - 1.0 range.
        :param top_probability: Float in 0.0 - 1.0 range.
        :return: String generated completion.
        """
        yield from self._request(
            messages,
            model,
            temperature,
            top_probability,
        )

def main(messages):
    # Example usage of OpenAIClient
    api_host = os.getenv("OPENAI_API_HOST", "https://api.openai.com")  # Replace with your API host
    api_key = ""    # Replace with your API key

    client = OpenAIClient(api_host, api_key)



    for completion in client.get_completion(messages):
        print(completion, end='')
    print()

if __name__ == '__main__':
    messages = [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there! I am a python code debugger, What is your error message?"},
    {"role": "user", "content": " how do i fix a syntaxerror"},
    ]

    main(messages)
