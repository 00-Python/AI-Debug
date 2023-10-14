import os
import sys
import openai
import pickle
import hashlib
import tempfile
from platform import system as platform_system
import tiktoken


class CodeDebugger:
    def __init__(self, model, model_temperature, max_output_tokens):
        self.openai_model = model
        self.model_temperature = model_temperature
        # self.max_output_tokens = {"gpt-3.5-turbo": 4096, "gpt-4": 8192, "gpt-4-32k": 32768, "gpt-3.5-turbo-16k": 16384}.get(self.openai_model, None)
        self.max_output_tokens = max_output_tokens
        cache_file_name = 'cache.pickle'
        self.tmp_cache_dir = os.path.join(
            tempfile.gettempdir(), cache_file_name)
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        self.messages = [
            {"role": "system", "content": "You are a detailed code debugger assistant that doesn't miss a single error. You always point out where the error is and what is causing it."}
        ]
        self.encoder = tiktoken.encoding_for_model(self.openai_model)

    def get_files(self, path):
        ignore_dirs = {"env", "venv", "__pycache__", ".git"}
        files_dict = {}
        file_and_dir_list = []

        # Check if the path is a valid directory
        if not os.path.isdir(path):
            print("Invalid path provided.")
            return files_dict

        # Create a list of files and directories
        for root, dirs, files in os.walk(path, topdown=True):
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            for file in files:
                filepath = os.path.join(root, file)
                file_and_dir_list.append(filepath)
            for dir in dirs:
                dirpath = os.path.join(root, dir)
                file_and_dir_list.append(dirpath)

        # Print out all available files and directories with paths relative to 'path'
        for i, file_or_dir_path in enumerate(file_and_dir_list):
            rel_path = os.path.relpath(file_or_dir_path, path)
            if os.path.isdir(file_or_dir_path): # check if path is a directory
                rel_path += "/" # append a '/' to the end of the path
            print(f"{i+1}. {rel_path}")

        file_choices = input(
            "Choose files by typing the corresponding numbers (separated by a space for multiple files). You can also choose directories to select all files within that directory: "
        ).split()
        file_choices = [int(choice) for choice in file_choices]

        # Check if the choices are valid
        for choice in file_choices:
            if 0 < choice <= len(file_and_dir_list):
                file_or_dir_path = file_and_dir_list[choice - 1]
                if os.path.isfile(file_or_dir_path):  # If it's a file
                    with open(file_or_dir_path, "r") as file:
                        rel_path = os.path.relpath(file_or_dir_path, path)
                        files_dict[rel_path] = file.read()
                else:  # If it's a directory
                    for root, dirs, files in os.walk(file_or_dir_path):
                        for file in files:
                            filepath = os.path.join(root, file)
                            rel_path = os.path.relpath(filepath, path)
                            with open(filepath, "r") as file:
                                files_dict[rel_path] = file.read()
            else:
                print(f"Invalid choice ({choice}). Please try again.")

        return files_dict



    # Token & Price Counter Methods
    def count_tokens(self, data):
        encoding = self.encoder.encode(data)
        return len(encoding)

    def calculate_cost(self, tokens):

        # token price is per 1k tokens
        prices = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-32K": {"input": 0.06, "output": 0.12},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
        }

        for model_name, price_data in prices.items():            
            if self.openai_model == model_name:
                cost_input = (price_data["input"] * tokens) / 1000
                cost_output = (price_data["output"] * self.max_output_tokens)  / 1000
                return cost_input, cost_output

        return None, None


    # Convert cost to human-readable format
    def format_cost(self, cost, decimals):
        return f"£{cost:.{decimals}f}"

    # Cache methods

    def save_cache(self, cache_data):
        with open(self.tmp_cache_dir, 'wb') as file:
            pickle.dump(cache_data, file)

    def load_cache(self):
        if os.path.exists(self.tmp_cache_dir):
            with open(self.tmp_cache_dir, 'rb') as file:
                try:
                    return pickle.load(file)
                except (pickle.PickleError, EOFError):
                    pass
        return {}

    def clear_cache(self):
        if os.path.exists(self.tmp_cache_dir):
            os.remove(self.tmp_cache_dir)
            print("Cache cleared.")
        else:
            print("Cache is already empty.")

    def hash_code(self, code_content):
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

    # Debug Methods

    def get_suggestions_from_openai(self, model, messages):
        if self.max_output_tokens != 0:
            response = openai.ChatCompletion.create(model=model,max_tokens=self.max_output_tokens, temperature=self.model_temperature, messages=messages)
        else:
            response = openai.ChatCompletion.create(model=model, temperature=self.model_temperature, messages=messages)

        return response.choices[0].message["content"].strip()



if __name__ == "__main__":
    pass
