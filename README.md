# AIDebug Console
[![Downloads](https://static.pepy.tech/badge/aidebug)](https://pepy.tech/project/aidebug)
[![Downloads](https://static.pepy.tech/badge/aidebug/month)](https://pepy.tech/project/aidebug)
[![Downloads](https://static.pepy.tech/badge/aidebug/week)](https://pepy.tech/project/aidebug)

![Alt Text](./images/AIDebug_Help_Menus.png)

AIDebug Console is a Python-based command line application that leverages the power of OpenAI's GPT models to assist with debugging and developing software projects. It provides a user-friendly interface for interacting with your codebase, running your project, and even debugging your code with the help of AI.

## Features
!! Now Supports GOOGLE Geminai!! 
Will soon support Open Source Models

- **Project Management**: Select and deselect project files and directories.
- **Project Configuration**: Configure specific project details such as language, type, framework, and run command.
- **Code Execution**: Run your project directly from the console. (Automatically catches errors and asks user if they want to debug)
- **AI Debugging**: Debug your project with the help of OpenAI's GPT Models.
- **AI Feature Request**: Request a feature for your project from OpenAI's GPT Models.
- **AI Code Documentation**: Get a README.md file for your project's GitHub repository.

## Installation

### Install With Pip

```bash
pip install aidebug
```

### Manual Build and Install

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Install the required Python packages using pip:

```bash
pip install setuptools wheel
```
4. Build the project with setup.py:

```bash
python setup.py sdist bdist_wheel
```
5. Change directory to the built project:

```bash
cd dist
```
6. Install the built .whl file with pip:

```bash
pip install aidebug-0.0.8-py3-none-any.whl
```


## Usage
1. Set the necessary environment variables. You need to provide your OpenAI API or Google AI API key:

```bash
export OPENAI_API_KEY=your_openai_api_key
export GOOGLE_API_KEY=your_GOOGLE_API_KEY
```

2. Run the project:

```bash
aidebug
```

3. **Use the available commands to manage and debug your project:**

- **help**: List all available commands.
- **update_codebase**: Update the contents of the selected project files.
- **project**: Perform project related operations (select, deselect, run, files).
- **config**: Configure project and client specifics.
- **exit**: Exit the AI-Debug console.
- **debug**: Debug project with GPT by providing the relevant error message.
- **feature**: Request a feature for your project from GPT.
- **readme**: Generate a README.md file for your project.

### Commands

- **update_codebase**: Reads the contents of each selected file and updates the stored contents.

- **project select**: Launches a directory browser to select project files and directories.

- **project deselect**: Launches a directory browser to deselect files.

- **project run**: Runs the project using the configured run command.

- **project files paths**: Prints selected file paths.

- **project files contents**: Prints selected file paths and contents.

- **config project language**: Prompts user to input project language.

- **config project type**: Prompts user to describe the type of project.

- **config project framework**: Prompts user to input the framework used in the project.

- **config project run**: Prompts user to input the command to run the project.

- **config openai model**: Sets the OpenAI model.

- **config openai temperature**: Sets model temperature.

- **config client type**: Sets the client type (openai, google, open_source).

- **config client api_key**: Sets the API key for the selected client type (if applicable).

- **debug**: Debug project with GPT. Input the error message as the argument.

- **feature**: Request a feature for your project from GPT. Describe the required feature as an argument.

- **readme**: Generate a README.md file for your project's Github repository.

## Example

Start the AI-Debug shell:

```bash
python -m aidebug
```

Select project files:

```sh
AIDebug > project select
```

Update codebase:

```sh
AIDebug > update_codebase
```

Run the project:

```sh
AIDebug > project run
```

Configure project language:

```sh
AIDebug > config project language
Enter project language: Python
```

Debug project:

```sh
AIDebug > debug <error message>
```

Request a new feature:

```sh
AIDebug > feature <feature description>
```

Generate a README file:

```sh
AIDebug > readme
```
## Running System Commands

AIDebug Console allows you to run native system commands directly from the shell. Simply input the desired command, and it will be executed in the console.

For example, to list the files in the current directory, you can use the command `ls`:

```
> ls
```

This feature provides flexibility and convenience for running various system tasks alongside your project debugging and development.

## Credits

This project has borrowed code from [TheR1D's shell_gpt project](https://github.com/TheR1D/shell_gpt/blob/main/sgpt/client.py). I would like to express my gratitude for the contribution to the open-source community which has greatly aided the development of this project.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GNU v3 GPL-3.0 License. See the [LICENSE](LICENSE) file for details.
