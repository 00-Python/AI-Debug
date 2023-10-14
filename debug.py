import argparse
import os
import sys
from system import CodeDebugger

def main():
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
    parser.add_argument("-p", "--path", type=str,
                        help="Path to the directory containing code files")
    parser.add_argument("-e", "--error", type=str,
                        help="Specific error message or description of the error or issue")
    parser.add_argument(
        "--clear-cache", action='store_true', help="Clear the cache")
    args = parser.parse_args()

    debugger = CodeDebugger(str(args.model), args.temperature, int(args.max_output_tokens))    


    if args.clear_cache:
        debugger.clear_cache()
        return

    code_dict = debugger.get_files(args.path)


    if not code_dict:
        print("No code files found.")
        return

    code_content_combined = "".join(code_dict.values())
    code_hash = debugger.hash_code(code_content_combined)
    cache_data = debugger.load_cache()

    if code_hash in cache_data:
        cached_code_hash, cached_result = cache_data[code_hash]

        if cached_code_hash == code_hash:
            print("Using cached suggestions:")
            print(cached_result)
            return

    debugger.messages.append(
        {"role": "user", "content": f"Debug the following {args.language} code:"})

    for rel_filepath, code_content in code_dict.items():
        debugger.messages.append(
            {"role": "assistant", "content": f"File: {rel_filepath}\n\n{code_content}"})

    debugger.messages.append({"role": "user", "content": args.error})


    input_tokens = debugger.count_tokens(str(debugger.messages))
    print(f"Total tokens in data: {input_tokens}")

    input_cost, output_cost = debugger.calculate_cost(input_tokens)
    print(f"Total cost: {debugger.format_cost(input_cost+output_cost, 4)} (Input tokens cost: {debugger.format_cost(input_cost, 9)}, Output tokens cost: {debugger.format_cost(output_cost, 5)})")

    if input('Continue? (y/n) ').lower() == 'n':
        sys.exit()
    print()
    
    debugger.check_cache(args.model, debugger.messages,
                        args.error, code_content_combined)

if __name__ == "__main__":
    main()
