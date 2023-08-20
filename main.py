import argparse
import os
import openai

# Get your OpenAI API key from the environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

def get_debugging_suggestions(model, messages):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages
    )

    return response.choices[0].message["content"].strip()

def get_code_from_directory_or_file(path):
    code_dict = {}

    if os.path.isfile(path):  # If path is a single file
        filename = os.path.basename(path)
        with open(path, "r") as file:
            code_dict[filename] = file.read()
    elif os.path.isdir(path):  # If path is a directory
        for filename in os.listdir(path):
            filepath = os.path.join(path, filename)
            if os.path.isfile(filepath):
                with open(filepath, "r") as file:
                    code_dict[filename] = file.read()
    else:
        print("Invalid path provided.")

    return code_dict


def main():
    parser = argparse.ArgumentParser(description="Code Debugger CLI")
    parser.add_argument("--model", type=str,  default="gpt-3.5-turbo-16k", help="Name of the OpenAI debugging model to use (default: 'gpt-3.5-turbo-16k')")
    parser.add_argument("--language", type=str, help="Programming language of the code")
    parser.add_argument("--path", type=str, help="Path to the directory containing code files")
    parser.add_argument("--error", type=str, help="Description of the error or issue")
    args = parser.parse_args()

    # Get code content from the directory
    code_dict = get_code_from_directory_or_file(args.path)

    if not code_dict:
        print("No code files found.")
        return

    # Prepare the messages for the AI chat
    messages = [
        {"role": "system", "content": "You are a detailed code debugger assistant that doesn't miss a single error."},
        {"role": "user", "content": f"Debug the following {args.language} code:"}
    ]
    
    # Add code content as assistant messages with filename and line information
    for filename, code_content in code_dict.items():
        messages.append({"role": "assistant", "content": f"File: {filename}\n\n{code_content}"})

    messages.append({"role": "user", "content": args.error})

    # Make the API call using the specified model and messages
    suggestions = get_debugging_suggestions(args.model, messages)
    print("AI Debugging Suggestions:")
    print(suggestions)

if __name__ == "__main__":
    main()
