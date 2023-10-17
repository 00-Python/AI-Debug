from typing import Dict, List, Tuple, Union, Callable
import os
import sys
import time
import pickle
import hashlib
import tempfile
import argparse
import tiktoken
import openai

from lsdir.lsdir import Lsdir


timer_switch = False


def function_timer(func: Callable) -> Callable:
    """
    A decorator that prints the function execution time in seconds. When applied to a function, this decorator 
    adds functionality to calculate the start and end time of execution, then it calculates the difference 
    between these which results in the time taken to execute the function. 
  
    Usage:
        @function_timer
        def test_function():
            ...
    
    Parameters:
        func (Callable): The function to time.

    Returns:
        Callable: The wrapped function. This function behaves exactly like the input function 'func', 
                  but with an additional printing of its execution time in seconds.
    """

    def wrapper(*args, **kwargs):
        # Reference the global switch
        global timer_switch 
        if timer_switch: # Check if timers should be active
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            print(
                f"Function {func.__name__} took {end_time - start_time} seconds to execute.")
            return result
        else: 
            return func(*args, **kwargs)  # If switch is off, execute the function without timing
    return wrapper



class CodeDebugger:
    """
    The CodeDebugger class is responsible for debugging code by leveraging OpenAI models.

    Attributes:
        openai_model (str): Name of the OpenAI model to be used for debugging.
        model_temperature (float): Temperature to control randomness of the model's response.
        max_output_tokens (int): Maximum number of output tokens desired in the model's response.
        tmp_cache_dir (str): Directory to store temporary cache.
        messages (List[Dict[str,str]]): Messages exchanged with the API.
        encoder (object): Encoder object to convert string to tokens.
    """

    @function_timer
    def __init__(self, model: str = "gpt-3.5-turbo-16k", model_temperature: float = 1, max_output_tokens: int = 0):
        """
        Initializes CodeDebugger with model parameters and API details.

        Parameters:
            model (str): Name of the OpenAI model to be used for debugging. It should be a string and must be one of the available models.
            model_temperature (float): Temperature to control randomness of the model's response. It should be a float between 0 and 1. Higher values will make the outcome more random.
            max_output_tokens (int): Maximum number of output tokens desired in the model's response. It should be a positive integer. If it exceeds the model's limit, it could result in an error.
        """
        self.openai_model = model
        self.model_temperature = model_temperature
        # self.max_output_tokens = {"gpt-3.5-turbo": 4096, "gpt-4": 8192, "gpt-4-32k": 32768, "gpt-3.5-turbo-16k": 16384}.get(self.openai_model, None)
        self.max_output_tokens = max_output_tokens
        cache_file_name = 'cache.pickle'
        self.tmp_cache_dir = os.path.join(
            tempfile.gettempdir(), cache_file_name)
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        self.messages = [
            {"role": "system", "content": "You are a detailed code debugger that doesn't miss a single error. You explain Where the errors are, what is causing them and how to fix them."},
            {"role": "system", "content": "You also help with refactoring and optimization."},
            {"role": "system", "content": "You provide guidance on improving security."},
            {"role": "system", "content": "You also provide general improvement suggestions."},
            {"role": "system", "content": "You also help with Documentation of the project."},
        ]
        self.encoder = tiktoken.encoding_for_model(self.openai_model)

    @function_timer
    def get_directory_contents(self, path: str, max_depth: int, current_depth: int = 0):
        """
        Fetches the directory contents and returns a dictionary

        Parameters:
            path (str): Directory path from which to fetch files
            max_depth (int): Maximum recursion depth
            current_depth (int): Current recursion depth (default is 0 for the start)

        Returns:
            Dict[str, str]: A dictionary where each key-value pair represents a relative file path and its content, respectively.
        """

        ignore_dirs = {"env", "venv", "__pycache__", ".git"}
        files_dict = {}
        if not os.path.isdir(path):
            print("Invalid path provided.")
            return files_dict
        for root, dirs, files in os.walk(path, topdown=True):
            # Check recursion depth
            if current_depth > max_depth:
                return files_dict

            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

            for dir in dirs:
                rel_path = os.path.relpath(root + '/' + dir, path)
                files_dict[rel_path] = "Directory"

            for file in files:
                # get relative file path
                rel_path = os.path.relpath(root + '/' + file, path)
                try:
                    with open(os.path.join(root, file), 'rb') as f:
                        content = f.read().decode('utf-8', errors='replace')
                    files_dict[rel_path] = content
                except Exception as e:
                    print(f"Failed to process file: {os.path.join(root, file)}. Error: {str(e)}")
                    continue
            current_depth += 1

        return files_dict

    @function_timer
    def get_directory_contents_depth(self, path: str, levels: int) -> Dict[str, str]:
        ignore_dirs = {"env", "venv", "__pycache__", ".git", "static", "assets", "media"}
        files_dict = {}

        if not os.path.isdir(path):
            print("Invalid path provided.")
            return files_dict

        for directory in os.listdir(path):
            newPath = os.path.join(path, directory)
            if directory in ignore_dirs or directory.startswith('.'):
                continue

            if(levels > 0 and os.path.isdir(newPath)):
                files_dict.update(self.get_directory_contents_depth(newPath, levels-1))
            elif(os.path.isfile(newPath)):
                with open(newPath, 'rb') as f:
                    content = f.read().decode('utf-8', errors='replace')
                rel_path = os.path.relpath(newPath, path)
                files_dict[rel_path] = content

        return files_dict

    @function_timer
    def display_directory_contents(self, files_dict: Dict[str, str]) -> None:
        """
        Display all available files and directories on stdout.
        """

        for i, (filepath, content) in enumerate(files_dict.items()):
            if content == "Directory":
                print(f"{i+1}. {filepath} (Directory)")
            else:
                print(f"{i+1}. {filepath} (File)")

    @function_timer
    def get_user_file_selection(self, files_dict: Dict[str, str]) -> Dict[str, str]:
        """
        Takes user input to select a subset of files.

        Parameters:
            files_dict (Dict[str, str]): User file selection.
        """

        file_choices = input(
            "Choose files by typing the corresponding numbers (separated by a space for multiple files). You can also choose directories to select all files within that directory: "
        ).split()
        file_choices = [int(choice) for choice in file_choices]
        chosen_files = {}

        file_keys = list(files_dict.keys())

        for choice in file_choices:
            if 0 < choice <= len(file_keys):
                chosen_files[file_keys[choice-1]
                             ] = files_dict[file_keys[choice-1]]
            else:
                print(f"Invalid choice ({choice}). Please try again.")

        return chosen_files

    @function_timer
    def count_tokens(self, data: str) -> int:
        """
        Counts the number of tokens present in the provided string.
        This function uses the encoder object of the class that's
        created for the selected OpenAI model and counts the total encoder
        token count of the provided string.

        Parameters:
            data (str): The string which needs its tokens to be counted.
                        It can be a single line or multiline string.

        Returns:
            int: The total count of tokens present in the provided 'data'.
        """
        encoding = self.encoder.encode(data)
        return len(encoding)

    @function_timer
    def calculate_cost(self, tokens: int) -> Tuple[Union[None, float], Union[None, float]]:
        """
        Calculates the cost of the token usage based on the OpenAI model
        used and returns the costs for both input and output tokens.

        The function uses a dictionary to store the cost per token for input/output
        for different OpenAI models. After finding the corresponding model's cost,
        it multiplies the input token cost with the total token count and output
        token cost with the maximum output tokens.

        Parameters:
            tokens (int): The total count of the tokens.

        Returns:
            Tuple[Union[None, float], Union[None, float]]: A tuple containing
            the costs for input and output tokens. If the model's cost data
            doesn't exist in the 'prices' dictionary, it returns (None, None).
        """
        prices = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-32K": {"input": 0.06, "output": 0.12},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
            "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
        }

        for model_name, price_data in prices.items():
            if self.openai_model == model_name:
                cost_input = (price_data["input"] * tokens) / 1000
                cost_output = (price_data["output"]
                               * self.max_output_tokens) / 1000
                return cost_input, cost_output

        return None, None

    @function_timer
    def format_cost(self, cost: float, decimals: int) -> str:
        """
        Formats the cost in a more human-readable string format using the specified number of decimal places.

        Parameters:
            cost (float): The cost to be formatted. It should be a float representing the raw cost.
            decimals (int): The number of decimal places to use in the output string. It should be a non-negative integer.

        Returns:
            str: A formatted string representing the cost, prefixed by the '£' symbol and with the specified number of decimal places.
        """
        return f"£{cost:.{decimals}f}"
    
    @function_timer
    def print_tokens_and_costs(self, code_dict: Dict[str, str]) -> None:
        """
        Print the total number of tokens in the given code and the associated cost of using those tokens with the active OpenAI model.
        This function doesn't return anything; instead, it prints the calculated values to stdout.

        Parameters:
            code_dict (Dict[str, str]): A dictionary mapping file paths to source code. The tokens of this code will be counted and the costs will be calculated.
        """
        code_content_combined = "".join(code_dict.values())
        input_tokens = self.count_tokens(str(self.messages))
        print(f"Total tokens in data: {input_tokens}")
        input_cost, output_cost = self.calculate_cost(input_tokens)
        print(f"Total cost: {self.format_cost(input_cost+output_cost, 4)} (Input tokens cost: {self.format_cost(input_cost, 9)}, Output tokens cost: {self.format_cost(output_cost, 5)})")


    @function_timer
    def save_cache(self, cache_data: any) -> None:
        """
        Saves the cache data to a pickle file.

        Parameters:
        - cache_data: The cache data to save
        """
        with open(self.tmp_cache_dir, 'wb') as file:
            pickle.dump(cache_data, file)

    @function_timer
    def load_cache(self) -> Dict:
        """
        Tries to load the cached data from a pickle file.

        Returns: The loaded cache data if the file existed and was valid, otherwise an empty dictionary.
        """
        if os.path.exists(self.tmp_cache_dir):
            with open(self.tmp_cache_dir, 'rb') as file:
                try:
                    return pickle.load(file)
                except (pickle.PickleError, EOFError):
                    pass
        return {}

    @function_timer
    def clear_cache(self) -> None:
        """
        Deletes the cache file if it exists.
        """
        if os.path.exists(self.tmp_cache_dir):
            os.remove(self.tmp_cache_dir)
            print("Cache cleared.")
        else:
            print("Cache is already empty.")

    @function_timer
    def hash_code(self, code_content: str) -> str:
        hash_object = hashlib.md5(code_content.encode())
        return hash_object.hexdigest()

    @function_timer
    def check_cache(self, model: str, messages: List[Dict[str, str]], error: str, code_content: str) -> None:
        """
        Check if the error's solution already exists in the cache. If it does, print the cached result.
        If it doesn't, get new suggestions from the OpenAI model and cache them for future use.

        Parameters:
        - model: The key string identifying the OpenAI model to use
        - messages: List of message-role-content dicts that is the log of messages to send to the OpenAI model for debugging
        - error: Description of the error to check in the cache or ask the OpenAI model to debug if not in cache
        - code_content: The content of the code that needs debugging. This is used along with the error to form a unique key in the cache
        """
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

    @function_timer
    def get_suggestions_from_openai(self, model: str, messages: List[Dict[str, str]]) -> str:
        """
        Make a chat completion with the provided model and messages.

        Parameters:
        - model: The key string identifying the OpenAI model to use
        - messages: List of message-role-content dicts encompassing a chat log

        Returns: The content of the response message
        """
        if self.max_output_tokens != 0:
            response = openai.ChatCompletion.create(
                model=model, max_tokens=self.max_output_tokens, temperature=self.model_temperature, messages=messages)
        else:
            response = openai.ChatCompletion.create(
                model=model, temperature=self.model_temperature, messages=self.messages)

        return response.choices[0].message["content"].strip()

    @function_timer
    def construct_messages(self, language: str, code_dict: Dict[str, str], error: str) -> List[Dict[str, str]]:
        """
        Constructs the messages to send to the openAI model.

        Parameters:
        - language:  The programming language of the code
        - code_dict: Dictionary where the keys are relative file paths and the values are corresponding file contents
        - error: Description of the error to ask the OpenAI model to debug

        Returns: List of message-role-content dictionaries that can be directly sent to the OpenAI model
        """
        self.messages.append(
            {"role": "user", "content": f"Debug the following {language} code:"})

        for rel_filepath, code_content in code_dict.items():
            self.messages.append(
                {"role": "user", "content": f" File={rel_filepath}  Content=```{language}\n{code_content}```"})

        self.messages.append(
            {"role": "user", "content": f"Encountered Problem/Error: {error}"})

        return self.messages


@function_timer
def parse_command_line_arguments():
    parser = argparse.ArgumentParser(
        description="AI Code Debugger & Helper CLI")
    parser.add_argument("-m", "--model", type=str, default="gpt-3.5-turbo-16k",
                        help="Name of the OpenAI model to use (default: 'gpt-3.5-turbo-16k' Others: 'gpt-4', 'gpt-3.5-turbo')")
    parser.add_argument("-t", "--temperature", type=float, default=1,
                        help="Temperature of response (Default is 1, can be between 0 and 2)")
    parser.add_argument("-o", "--max-output-tokens", type=int, default=0,
                        help="Maximum output tokens in response (Default: GPT-3.5 Turbo: 4096 tokens, GPT-3.5-Turbo 16k: 16,384 tokens, GPT-4: 8192 tokens, GPT-4 32K: 32768 tokens)")
    parser.add_argument("-l", "--language", type=str,
                        help="Programming language of the code")
    parser.add_argument("-ft", "--function-timer", type=bool,
                        help="Function execution timer")
    parser.add_argument("-p", "--path", type=str,
                        help="Path to the directory containing codebase")
    parser.add_argument("-e", "--error", type=str,  nargs='?',
                        help="Specific error message or description of the error or issue")

    # parser.add_argument("--clear-cache", action='store_true',
    #                     help="Clear the cache")
    return parser.parse_args()

@function_timer
def args_handler(args):
    if args.error is None:
    # if -e is not used, try to use piped input
        if not sys.stdin.isatty():
            args.error = sys.stdin.read().strip()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    # if args.clear_cache:
    #     cache_debugger = CodeDebugger()
    #     cache_debugger.clear_cache()
    #     return
    
    return args


@function_timer
def get_input_confirmation():
    if input('Continue? (y/n) ').lower() == 'n':
        sys.exit()


@function_timer
def run_debugger():
    args = parse_command_line_arguments()
    args_handler(args)
    
    debugger = CodeDebugger(
        str(args.model), args.temperature, int(args.max_output_tokens))

    code_dict = debugger.get_directory_contents(args.path, 1)
    debugger.display_directory_contents(code_dict)
    code_dict = debugger.get_user_file_selection(code_dict)

    if not code_dict:
        print("No code files found.")
        return

    # New checks for piped `sys.stdin` input
    error = args.error
    if error is None:
        if not sys.stdin.isatty():  # If data is available in a pipeline
            error = sys.stdin.read().strip()

    if not error:
        print("No error provided for debugging. Please provide an error description through -e argument or by piping in.")
        return

    # Combine code content and create hash
    # code_content_combined = "".join(code_dict.values())
    # code_hash = debugger.hash_code(code_content_combined)

    # cache_data = debugger.load_cache()
    # if code_hash in cache_data:
    #     cached_code_hash, cached_result = cache_data[code_hash]
    #     if cached_code_hash == code_hash:
    #         print("Using cached suggestions:")
    #         print(cached_result)
    #         return

    constructed_messages = debugger.construct_messages(
        args.language, code_dict, args.error)

    input_tokens = debugger.count_tokens(str(debugger.messages))
    print(f"Total tokens in data: {input_tokens}")

    input_cost, output_cost = debugger.calculate_cost(input_tokens)
    print(f"Total cost: {debugger.format_cost(input_cost+output_cost, 4)} (Input tokens cost: {debugger.format_cost(input_cost, 9)}, Output tokens cost: {debugger.format_cost(output_cost, 5)})")

    # Confirm and print result
    get_input_confirmation()
    print()

    # debugger.check_cache(args.model, debugger.messages,
    #                      args.error, code_content_combined)

    print(debugger.get_suggestions_from_openai(args.model, debugger.messages))


if __name__ == "__main__":
    run_debugger()
    # files = Lsdir()
    # data = files.scan_cwd()

    # levels = files.count_levels(data)
    # print(levels)
    # files.print_tree(data, max_levels=2)  

    # while True:

    #     id = int(input("File: "))

    #     data2 = files.find_item_by_id(id, data)
    #     print(id)
    #     print(data2)
