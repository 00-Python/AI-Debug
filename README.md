# Python AI Code Debugger

Welcome! This Python project offers you a remarkable debugging assistant powered by OpenAI's advanced machine learning models.

## :star2: Features

**Suggests Bug Fixes:** The AI suggests potential bug fixes for your code, so you can simply focus on development.

**Token Count and Costs:** The application helps you estimate the tokens used in sending requests to the OpenAI API and provides a cost estimation as well!

**Cache Facilities:** Not want to waste tokens on repeated issues? The application can save suggestions for earlier seen issues in a cache file.

## :fast_forward: Quick Start

1. **Get the files**

   Clone the repo with this command:
   ```bash
   git clone https://github.com/Your_User_Name/AI-Code-Debugger.git
   ```

2. **Change directory**

   Change to the `AI-Code-Debugger` directory:
   ```bash
   cd AI-Code-Debugger
   ```

3. **Setup**

   Install required dependencies using pip:

   ```bash
   pip install -r requirements.txt
   ```

   Next, export the OpenAI API key as an environment variable:

   ```bash
   export OPENAI_API_KEY='your_api_key'
   ```

4. **Run**

   Now, you're ready for debugging:

   ```bash
   python debug.py -l Python -p /path/to/your/code -e "Error message here"
   ```

## :whale: Detailed Usage

The Python AI Code Debugger is designed to be highly flexible and customizable to accommodate various debugging needs.

You can launch the Python Debugger with various options to control its behavior:

```bash
python debug.py -m gpt-3.5-turbo -t 1.0 -o 500 -l Python -p your_code_dir -e "Your error message"
```

Where:
- `-m, --model`: OpenAI Model to use for debugging assistance. Defaults to `gpt-3.5-turbo`. (supported: 'gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-32k')
- `-t, --temperature`: The creative force of the prediction. Increase for more diverse output. Default is `1` and acceptable range is `0 - 2`.
- `-o, --max-output-tokens`: The maximum tokens that the model will use to produce the output. Default is model specific.
- `-l, --language`: The programming language of the debugging code. Currently supported: Python, Javascript, Java, C/C++, C#.
- `-p, --path`: Path to the directory containing the codebase.
- `-e, --error`: Error message or a description of the issue.

**Note:** You can always use the `-h` or `--help` argument to see all available options for the Python Code Debugger.

## :ticket: Need Help?

If you're stuck at any point, be sure to post the issue to the repository's Issue Tracker. We're here to help.

Or better yet, contribute and open a pull request with your fixes for the community! We're always looking out for folks who want to help out.

## :heart: Contributing

We'd love to welcome contributors who can help make this project better.

## :bookmark: License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE.md) file for more information.

## :clap: Join the Community

Don't forget to star the repo if you like what you see, and watch for new updates.
