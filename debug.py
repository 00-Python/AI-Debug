import os
import sys
import openai
import pickle
import hashlib
import tempfile
from platform import system as platform_system
import tiktoken
import argparse


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


    def print_tokens_and_costs(self, code_dict):
        code_content_combined = "".join(code_dict.values())
        input_tokens = self.count_tokens(str(self.messages))
        print(f"Total tokens in data: {input_tokens}")
        input_cost, output_cost = self.calculate_cost(input_tokens)
        print(f"Total cost: {self.format_cost(input_cost+output_cost, 4)} (Input tokens cost: {self.format_cost(input_cost, 9)}, Output tokens cost: {self.format_cost(output_cost, 5)})")

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
            response = openai.ChatCompletion.create(model=model, temperature=self.model_temperature, messages=self.messages)

        return response.choices[0].message["content"].strip()


    def construct_messages(self, language, code_dict, error):
        self.messages.append({"role": "user", "content": f"Debug the following {language} code:"})

        for rel_filepath, code_content in code_dict.items():
            self.messages.append({"role": "assistant", "content": f"File: {rel_filepath}\n\n{code_content}"})

        self.messages.append({"role": "user", "content": f"Problem/Error: {error}"})

        return self.messages

def run_debugger():
    # Parsing command line arguments
    parser = argparse.ArgumentParser(description="AI Code Debugger & Helper CLI")
    parser.add_argument("-m", "--model", type=str, default="gpt-3.5-turbo-16k",
                        help="Name of the OpenAI model to use (default: 'gpt-3.5-turbo-16k' Others: 'gpt-4', 'gpt-3.5-turbo')")
    parser.add_argument("-t", "--temperature", type=float, default=1,
                        help="Temperature of response (Default is 1, can be between 0 and 2)")
    parser.add_argument("-o", "--max-output-tokens", type=int, default=0,
                        help="Maximum output tokens in response (Default: GPT-3.5 Turbo: 4096 tokens, GPT-3.5-Turbo 16k: 16,384 tokens, GPT-4: 8192 tokens, GPT-4 32K: 32768 tokens)")
    parser.add_argument("-l", "--language", type=str, help="Programming language of the code")
    parser.add_argument("-p", "--path", type=str, help="Path to the directory containing code files")
    parser.add_argument("-e", "--error", type=str, help="Specific error message or description of the error or issue")
    parser.add_argument("--clear-cache", action='store_true', help="Clear the cache")
    args = parser.parse_args()

    # Creating an debugger instance
    debugger = CodeDebugger(str(args.model), args.temperature, int(args.max_output_tokens))

    if args.clear_cache:
        debugger.clear_cache()
        return

    # Getting code files
    code_dict = debugger.get_files(args.path)

    if not code_dict:
        print("No code files found.")
        return

    # Combine code content and create hash
    code_content_combined = "".join(code_dict.values())
    code_hash = debugger.hash_code(code_content_combined)

    cache_data = debugger.load_cache()
    if code_hash in cache_data:
        cached_code_hash, cached_result = cache_data[code_hash]
        if cached_code_hash == code_hash:
            print("Using cached suggestions:")
            print(cached_result)
            return

    constructed_messages = debugger.construct_messages(args.language, code_dict, args.error)

    input_tokens = debugger.count_tokens(str(debugger.messages))
    print(f"Total tokens in data: {input_tokens}")

    input_cost, output_cost = debugger.calculate_cost(input_tokens)
    print(f"Total cost: {debugger.format_cost(input_cost+output_cost, 4)} (Input tokens cost: {debugger.format_cost(input_cost, 9)}, Output tokens cost: {debugger.format_cost(output_cost, 5)})")

    # Confirm and print result
    if input('Continue? (y/n) ').lower() == 'n':
        sys.exit()
    print()

    debugger.check_cache(args.model, debugger.messages,
                        args.error, code_content_combined)




if __name__ == "__main__":
    run_debugger()
