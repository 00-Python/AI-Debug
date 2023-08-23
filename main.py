import argparse
import os
import openai
import pickle
import hashlib
import tempfile
from platform import system as platform_system


class CodeDebugger:
    def __init__(self):
        self.openai_model = "gpt-3.5-turbo-16k"
        self.tmp_cache_dir = tempfile.gettempdir()

        if platform_system() == 'Linux':
            self.tmp_cache_dir = os.path.join(self.tmp_cache_dir, 'cache.pickle')
        elif platform_system() == 'Windows':
            self.tmp_cache_dir = os.path.join(self.tmp_cache_dir, 'cache.pickle')

        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def save_cache(self, cache_data):
        with open(self.tmp_cache_dir, 'wb') as file:
            pickle.dump(cache_data, file)

    def load_cache(self):
        if os.path.exists(self.tmp_cache_dir):
            with open(self.tmp_cache_dir, 'rb') as file:
                try:
                    cache_data = pickle.load(file)
                    return cache_data
                except (pickle.PickleError, EOFError):
                    pass
        return {}

    @staticmethod
    def hash_code(code_content):
        hash_object = hashlib.md5(code_content.encode())
        return hash_object.hexdigest()

    def check_cache(self, model, messages, error, code_content):
        cache_data = self.load_cache()

        if error in cache_data:
            cached_code_hash, cached_result = cache_data[error]
            current_code_hash = self.hash_code(code_content)

            if current_code_hash == cached_code_hash:
                print("Using cached suggestions:")
                print(cached_result)
                return

        computed_result = self.get_suggestions_from_openai(model, messages)

        cache_data[error] = (self.hash_code(code_content), computed_result)
        self.save_cache(cache_data)

        print("Suggestions:")
        print(computed_result)

    @staticmethod
    def get_suggestions_from_openai(model, messages):
        response = openai.ChatCompletion.create(model=model, messages=messages)
        return response.choices[0].message["content"].strip()

    @staticmethod
    def get_code_from_directory_or_file(path):
        code_dict = {}

        if os.path.isfile(path):  
            filename = os.path.basename(path)
            with open(path, "r") as file:
                code_dict[filename] = file.read()
        elif os.path.isdir(path):  
            for filename in os.listdir(path):
                filepath = os.path.join(path, filename)
                if os.path.isfile(filepath):
                    with open(filepath, "r") as file:
                        code_dict[filename] = file.read()
        else:
            print("Invalid path provided.")

        return code_dict

    def clear_cache(self):
        if os.path.exists(self.tmp_cache_dir):
            os.remove(self.tmp_cache_dir)
            print("Cache cleared.")
        else:
            print("Cache is already empty.")

    def main(self):
        parser = argparse.ArgumentParser(description="AI Code Debugger & Helper CLI")
        parser.add_argument("--model", type=str, default=self.openai_model,
                            help="Name of the OpenAI debugging model to use (default: 'gpt-3.5-turbo-16k')")
        parser.add_argument("--language", type=str, help="Programming language of the code")
        parser.add_argument("--path", type=str, help="Path to the directory containing code files")
        parser.add_argument("--error", type=str, help="Description of the error or issue")
        parser.add_argument("--clear-cache", action='store_true', help="Clear the cache")
        args = parser.parse_args()

        if args.clear_cache:
            self.clear_cache()
            return

        code_dict = self.get_code_from_directory_or_file(args.path)

        if not code_dict:
            print("No code files found.")
            return

        code_content_combined = "".join(code_dict.values())
        code_hash = self.hash_code(code_content_combined)
        cache_data = self.load_cache()

        if code_hash in cache_data:
            cached_code_hash, cached_result = cache_data[code_hash]

            if cached_code_hash == code_hash:
                print("Using cached suggestions:")
                print(cached_result)
                return

        messages = [
            {"role": "system", "content": "You are a detailed code debugger assistant that doesn't miss a single error. You always point out where the error is and what is causing it. If you do not notice an error you tell the user."},
            {"role": "user", "content": f"Debug the following {args.language} code:"}
        ]

        for filename, code_content in code_dict.items():
            messages.append({"role": "assistant", "content": f"File: {filename}\n\n{code_content}"})

        messages.append({"role": "user", "content": args.error})

        self.check_cache(args.model, messages, args.error, code_content_combined)


if __name__ == "__main__":
    debugger = CodeDebugger()
    debugger.main()

