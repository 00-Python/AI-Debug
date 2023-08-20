# AI Code Debugger

This script utilizes OpenAI's models to assist in debugging code by providing suggestions for identifying and fixing errors in your code.

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
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key as an environment variable:

   ```bash
   export OPENAI_API_KEY=your-api-key
   ```

## Usage

Run the script using the following command:

```bash
python main.py --language <programming_language> --path <path_to_code_directory or file> --error "<error_description>"
```

Replace the placeholders with appropriate values:

- `<programming_language>`: The programming language of the code you want to debug.
- `<path_to_code_directory or file>`: The path to the directory containing your code files or path to the single file.
- `<error_description>`: A description of the error or issue you are facing.

Example:

```bash
python main.py --language Python --path /path/to/your/code/directory/or/file --error "Code is throwing an IndexError."
```

### Available Arguments

- `--language`: The programming language of the code to be debugged.
- `--path`: Path to the directory containing code files or path to single file.
- `--error`: Description of the error or issue you're facing.
- `--model`: Name of the OpenAI debugging model to use (default: 'gpt-3.5-turbo-16k').

Example:

```bash
python main.py --language Python --path /path/to/code/directory/or/single/file --error "IndexError" --model "gpt-3.5-turbo-16k"
```

The script will analyze the code files in the specified directory or a single file and provide AI-powered suggestions to debug the issue.

## License

This project is licensed under the GNU v3.0 - see the [LICENSE](LICENSE) file for details.