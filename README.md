# AI Code Debugger

This script utilizes OpenAI's models to assist in debugging code by providing suggestions for identifying and fixing errors in your code.

## Detailed Explanation

Before generating a debugging suggestion for your code, the script first counts the number of tokens that would be used up with the current request. The number of tokens is directly related to how many bytes of data you're sending and receiving from the API.

The OpenAI API charges you based on these tokens.

After the token count, the script estimates the cost of using the API for the current debugging task. This estimation accounts for the cost of both input tokens (tokens used to send your code and request to the API) and output tokens if output tokens limit is specified by the user (tokens used by the API to generate the response).

You will be presented the cost estimation before the request is sent to the API for processing. This gives you the opportunity to review and minimize charges where necessary.

If the same error occurs in the same code, the script handles this efficiently by using a caching system to store previously generated debugging suggestions. If a cache of the debugging suggestion for the current code and error exists, the script fetches it from the cache instead of sending another request to the API.

## TODO
1. Add the abillity to choose specific files from dir or exclude specific files
1. Map the file structure to make the AI aware of it 

## Installation

1. Clone the repository to your local machine:

   ```bash
   git clone https://github.com/00-Python/AI-Debug.git 
   ```

2. Navigate to the project directory:

   ```bash
   cd AI-Debug
   ```

3. Install the required dependencies using pip:

   ```bash
   pip install openai tiktoken
   ```

4. Set up your OpenAI API key as an environment variable:

   ```bash
   export OPENAI_API_KEY=your-api-key
   ```

## Usage
Check the help menu:

```bash
python debug.py -h
```

Output:
```
usage: debug.py [-h] [-m MODEL] [-t TEMPERATURE] [-o MAX_OUTPUT_TOKENS] [-l LANGUAGE] [-p PATH] [-e ERROR] [--clear-cache]

AI Code Debugger & Helper CLI

options:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        Name of the OpenAI debugging model to use (default: 'gpt-3.5-turbo-16k' Others: 'gpt-4', 'gpt-3.5-turbo')
  -t TEMPERATURE, --temperature TEMPERATURE
                        Temperature of response (Default is 1, can be between 0 and 2)
  -o MAX_OUTPUT_TOKENS, --max-output-tokens MAX_OUTPUT_TOKENS
                        Maximum output tokens in response (Default: GPT-3.5 Turbo: 4096 tokens, GPT-3.5-Turbo 16k: 16,384 tokens, GPT-4: 8192 tokens, GPT-4 32K: 32768 tokens)
  -l LANGUAGE, --language LANGUAGE
                        Programming language of the code
  -p PATH, --path PATH  Path to the directory containing code files
  -e ERROR, --error ERROR
                        Specific error message or description of the error or issue
  --clear-cache         Clear the cache
```

Run the script using the following command:

```bash
python debug.py [--model <openai_model>] [--temperature <model_temperature>] [--max-output-tokens <max_output_tokens>] [--language <programming_language>] --path <path_to_code_directory or file> --error "<error_description>"
```

Replace the placeholders with appropriate values:

- `<openai_model>`: (optional) The OpenAI debugging model to use. Default: 'gpt-3.5-turbo-16k'. Options: 'gpt-4', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo'.
- `<model_temperature>`: (optional) Temperature of response. Default: 1.
- `<max_output_tokens>`: (optional) Maximum output tokens in response.
- `<programming_language>`: (optional) The programming language of the code you want to debug.
- `<path_to_code_directory or file>`: The path to the directory containing your code files or path to the single file.
- `<error_description>`: A description of the error or issue you are facing or the Traceback

Example:

```bash
python debug.py --model gpt-3.5-turbo --language Python --path /path/to/your/code/directory/or/file --error "Code is throwing an IndexError."
```

The script will analyze the code files in the specified directory or a single file and provide AI-powered suggestions to debug the issue. 

If for any reasons, you wanted to clear the previously cached error suggestions, you can do it by using `--clear-cache`:

```bash
python debug.py --clear-cache
```
This will clear all previously cached suggestions.

## License

This project is licensed under the GNU v3.0 - see the [LICENSE](LICENSE) file for details.
