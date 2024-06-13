import re
import os
import cmd
import sys
import subprocess
import platform

# Platform specific imports
if platform.system() == 'Windows':
    import pyreadline
else:
    import readline

from PyQt5.QtWidgets import QApplication
from colorama import Fore, init

from .core.gui.select_dirs import DirectoryBrowser
from .core.utils.files_data import scrape_contents
from .core.utils.error_handler import error_handler
from .core.clientv2.openai_client import OpenAIClient
from .core.clientv2.google_client import GoogleClient

# Initialize colorama
init(autoreset=True)

class CodeDebuggerShell(cmd.Cmd):
    intro = f"""{Fore.BLUE}
      █████████   █████    ██████████            █████
     ███░░░░░███ ░░███    ░░███░░░░███          ░░███
    ░███    ░███  ░███     ░███   ░░███  ██████  ░███████  █████ ████  ███████
    ░███████████  ░███     ░███    ░███ ███░░███ ░███░░███░░███ ░███  ███░░███
    ░███░░░░░███  ░███     ░███    ░███░███████  ░███ ░███ ░███ ░███ ░███ ░███
    ░███    ░███  ░███     ░███    ███ ░███░░░   ░███ ░███ ░███ ░███ ░███ ░███
    █████   █████ █████    ██████████  ░░██████  ████████  ░░████████░░███████
    ░░░░░   ░░░░░ ░░░░░    ░░░░░░░░░░    ░░░░░░  ░░░░░░░░    ░░░░░░░░  ░░░░░███
    ___________________________________________________________________███ ░███___
                                                                       ░░██████{Fore.RESET}
    {Fore.CYAN}By J. Webster-Colby\n    Github: https://github.com/00-Python{Fore.RESET}

    Type {Fore.RED}help{Fore.RESET} for a list of commands.
    """
    prompt = f'{Fore.GREEN}AIDebug{Fore.RESET} {Fore.YELLOW}> {Fore.RESET}'

    def __init__(self):
        super().__init__()
        self.venv_path = ""
        self.venv_name = ""
        self.use_venv = False

        self.files = []
        self.files_and_content = []
        self.project_language = ""
        self.project_type = ""
        self.project_framework = ""
        self.project_base_directory = ""
        self.project_run_command = ""

        self.messages = []

        self.client = None
        self.client_type = "openai"  # Default client type
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = "gpt-4o"
        self.openai_model_temperature = 1.0

        self.configure_client()

    def configure_client(self):
        if self.client_type == "openai":
            self.api_key = os.getenv("OPENAI_API_KEY")

            api_host = os.getenv("OPENAI_API_HOST", "https://api.openai.com")
            self.client = OpenAIClient(api_host, self.api_key)
        elif self.client_type == "google":
            self.api_key = os.getenv("GOOGLE_API_KEY")

            self.client = GoogleClient(self.api_key)
        elif self.client_type == "open_source":
            self.client = OpenSourceClient()
        else:
            raise ValueError("Unknown client type")

    def highlight_code(self, path, code):
        from pygments import highlight
        from pygments.lexers import get_lexer_for_filename
        from pygments.formatters import TerminalFormatter

        lexer = get_lexer_for_filename(path, stripall=True)
        formatter = TerminalFormatter()
        highlighted_code = highlight(code, lexer, formatter)
        print(highlighted_code)

    @error_handler
    def do_update_codebase(self, line):
        """Update the contents of the selected project files.

        Usage:
        update_codebase

        This command reads the contents of each selected file and updates the stored contents.
        The updated contents can be accessed using the 'project files contents' command.
        """
        for file_info in self.files_and_content:
            for path, _ in file_info.items():
                with open(path, 'r') as file:
                    content = file.read()
                file_info[path] = content

    @error_handler
    def preloop(self):
        # Check if a virtual environment is active
        venv_path = os.environ.get("VIRTUAL_ENV")
        if (venv_path):
            self.use_venv = True
            self.venv_path = venv_path
            self.venv_name = re.search(r'\b\w+\b$', self.venv_path).group()
            # Activate virtual environment
            os.system(f"source '{self.venv_path}/bin/activate'")
            self.prompt = f"{Fore.GREEN}AIDebug {Fore.RESET}{Fore.RED}@ {Fore.RESET}{Fore.GREEN}({self.venv_name}) {Fore.RESET}{Fore.YELLOW}> {Fore.RESET}"

    @error_handler
    def default(self, line):
        # Split the command into arguments
        command = line.split()

        if (command[0] == 'cd'):
            # Change the working directory for both the subprocess and the main script
            try:
                os.chdir(command[1])
            except FileNotFoundError:
                print(f"Directory not found: {command[1]}")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            with subprocess.Popen(line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                for stdout_line in iter(process.stdout.readline, ""):
                    print(stdout_line, end="")

                for stderr_line in iter(process.stderr.readline, ""):
                    print(stderr_line, end="")

    @error_handler
    def do_exit(self, _):
        """Exit the AIDebug Console.

        Usage:
        exit

        This command will terminate the AIDebug shell session.
        """
        return True

    @error_handler
    def do_project(self, line):
        """Perform project related operations. Available subcommands include:

        Usage:
        project select       -> Launches directory browser to select files.
        project deselect     -> Launches directory browser to deselect files.
        project run          -> Runs the project using configured run command.
        project files paths  -> Prints selected file paths.
        project files contents -> Prints selected file paths and contents.

        Description:
        - select: Prompts the user with a directory browser to select project files and directories.
        - deselect: Allows users to unselect previously selected files via a directory browser.
        - run: Runs the project using the previously set `project_run_command`.
        - files: Displays the currently selected file paths or file contents.
        """

        line = line.lower().split()

        if line[0] == 'select':
            self.select_project_files()
        elif line[0] == 'deselect':
            self.deselect_project_files()
        elif line[0] == 'run':
            self.run_project()
        elif line[0] == 'files':
            self.display_project_files(line[1])
        else:
            print('Invalid subcommand! Use one of: select, deselect, run, files')

    @error_handler
    def complete_project(self, text, line, begidx, endidx):
        """Tab complete for 'project' subcommands."""
        subcommands = ['select', 'deselect', 'run', 'files']
        if line.startswith('project files'):
            subcommands = ['paths', 'contents']
        completions = [command for command in subcommands if command.startswith(text)]
        return completions

    def select_project_files(self):
        """Select project files and directories."""
        selector = QApplication(sys.argv)
        window = DirectoryBrowser('Select Project Files: ')
        window.show()
        selector.exec_()
        self.files = list(set(window.selected_items))
        if (len(self.files) != 0):
            if (len(self.files) != 1):
                print('Files Selected!')
            else:
                print('File Selected')
        self.files_and_content = scrape_contents(self.files)

    def deselect_project_files(self):
        """Unselect files and directories."""
        deselector = QApplication(sys.argv)
        window = DirectoryBrowser('Select Files to Remove: ')
        window.show()
        deselector.exec_()

        files_to_remove = list(set(window.selected_items))

        if (len(files_to_remove) != 0):
            for file in files_to_remove:
                self.files.remove(file)
            print("Files Removed!")
        else:
            print("No files selected for removal.")
        self.files_and_content = scrape_contents(self.files)

    def run_project(self):
        """Run the project using the configured run command."""
        self.files_and_content = scrape_contents(self.files)
        try:
            # Run the command and capture its output and error messages
            result = subprocess.run(
                self.project_run_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            # Check if the command was successful (return code 0)
            if result.returncode == 0:
                print("Command output:")
                print(result.stdout)
            else:
                print("Command failed with error message:")
                print(result.stderr)

                if input("Debug Code? (y/n): ").strip().lower() == "y":
                    self.do_debug(result.stderr)

        except Exception as e:
            print(f"An error occurred: {e}")

    def display_project_files(self, option: str):
        """Display selected project files.

        Usage:
        project files paths    -> Prints selected file paths.
        project files contents -> Prints selected file paths and contents.

        This command allows displaying either the paths of the selected files or their contents.
        """
        if option == 'paths':
            for indx, file in enumerate(self.files):
                print(f'{indx+1}. {file}')
            print()
        elif option == 'contents':
            print("File Contents:\n")
            for file_dict in self.files_and_content:
                for path, content in file_dict.items():
                    print(f"{Fore.RED}{path}{Fore.RESET}:\n")
                    self.highlight_code(path, content)
                    print()
        else:
            print('Invalid option! Use one of: paths, contents')

    @error_handler
    def do_config(self, line):
        """Configure project and client specifics. Available subcommands include:

        Usage:
        config project language     -> Prompts user to input project language.
        config project type         -> Prompts user to describe the type of project.
        config project framework    -> Prompts user to input the framework used in project.
        config project run          -> Prompts user to input the command to run the project.
        config openai model         -> Sets the OpenAI model.
        config openai temperature   -> Sets model temperature.
        config client type          -> Sets the client type (openai, google, open_source).
        config client api_key       -> Sets the API key for the selected client type (if applicable).

        Description:
        - project: Configure project-specific settings (language, type, framework, run command).
        - openai: Configure OpenAI-specific settings (model, temperature).
        - client: Configure client settings (client type, API key).
        """
        commands = {
            'project language': self.set_project_language,
            'project type': self.set_project_type,
            'project framework': self.set_project_framework,
            'project run': self.set_project_run_command,
            'openai model': self.set_openai_model,
            'openai temperature': self.set_openai_temperature,
            'client type': self.set_client_type,
            'client api_key': self.set_client_api_key,
        }

        line = line.lower().strip()
        if line in commands:
            commands[line]()
        else:
            print("Invalid Command! Use 'config project', 'config openai', or 'config client' followed by the specific option.")

    @error_handler
    def complete_config(self, text, line, begidx, endidx):
        """Tab complete for 'config' subcommands."""
        subcommands = ['project', 'openai', 'client']
        if line.startswith('config project'):
            subcommands = ['language', 'type', 'framework', 'run']
        elif line.startswith('config openai'):
            subcommands = ['model', 'temperature']
        elif line.startswith('config client'):
            subcommands = ['type', 'api_key']
        completions = [command for command in subcommands if command.startswith(text)]
        return completions

    def set_project_language(self):
        """Prompt the user to enter the project language."""
        self.project_language = input('Enter project language: ')

    def set_project_type(self):
        """Prompt the user to describe the type of project."""
        self.project_type = input('What type of project is it? ')

    def set_project_framework(self):
        """Prompt the user to enter the framework used in the project."""
        self.project_framework = input('What framework is your project using? ')

    def set_project_run_command(self):
        """Prompt the user to enter the command to run the project."""
        self.project_run_command = input('Enter command used to run project: ')

    def set_openai_model(self):
        """Prompt the user to set the OpenAI model."""
        self.openai_model = input('Enter OpenAI model: ')

    def set_openai_temperature(self):
        """Prompt the user to set the OpenAI model temperature."""
        while True:
            try:
                self.openai_model_temperature = float(input('Enter model temperature (0.0 - 2.0): '))
                if 0.0 <= self.openai_model_temperature <= 2.0:
                    break
                else:
                    print('Temperature must be between 0.0 and 2.0.')
            except ValueError:
                print('Invalid input. Please enter a numerical value.')

    def set_client_type(self):
        """Prompt the user to set the client type. Valid options are: openai, google, open_source."""
        client_type = input('Enter client type (openai, google, open_source): ').lower()
        if client_type in ['openai', 'google', 'open_source']:
            self.client_type = client_type
            self.configure_client()
        else:
            print('Invalid client type. Choose either "openai", "google", or "open_source".')

    def set_client_api_key(self):
        """Prompt the user to set the API key for the selected client type, if applicable."""
        if self.client_type in ['openai', 'google']:
            self.api_key = input('Enter API key for the selected client: ')
            self.configure_client()
        else:
            print('API key is not required for the selected client type.')

    @error_handler
    def do_debug(self, line):
        """Debug project with GPT. Input the error message as the argument to the debug command.

        Usage:
        debug <error message>

        Description:
        This command allows you to debug the project by providing the relevant error message.
        The AI assistant will analyze the error and provide a detailed explanation along with potential fixes.
        """

        debug_messages = [
            {"role": "system", "content": "You are an AI coding assistant. You debug and fix code. Make sure to explain every error and mistake in the code that you find and fix."},
        ]

        project_details = f"This is a {self.project_type} project, the project uses {self.project_language}."
        if self.project_framework:
            project_details += f" and {self.project_framework} framework."
        debug_messages.append({"role": "user", "content": project_details})

        debug_messages.extend(
            [{"role": "user", "content": f"File: {path} Content: {content}"} for file in self.files_and_content for path, content in file.items()]
        )

        debug_messages.append({"role": "user", "content": f"This is the problem with the code: {line}"})
        if 'openai' in self.client_type:
            for completion in self.client.get_completion(list(debug_messages), model=self.openai_model, temperature=self.openai_model_temperature):
                print(completion, end='')
        else:
            for completion in self.client.get_completion(list(debug_messages)):
                print(completion, end='')
        print()

    @error_handler
    def do_feature(self, line):
        """Request a feature for your project from GPT. Describe the required feature as an argument.

        Usage:
        feature <feature description>

        Description:
        This command allows you to request a new feature for your project. Describe the feature you want,
        and the AI assistant will provide suggestions or code to implement the feature.
        """

        feature_messages = [
            {"role": "system", "content": "You are an AI coding assistant. Upon request you improve code, create features and refactor code."},
        ]

        project_details = f"This is a {self.project_type} project, the project uses {self.project_language}."
        if self.project_framework:
            project_details += f" and {self.project_framework} framework."
        feature_messages.append({"role": "user", "content": project_details})

        feature_messages.extend(
            [{"role": "user", "content": f"File: {path} Content: {content}"} for file in self.files_and_content for path, content in file.items()]
        )

        feature_messages.append({"role": "user", "content": f"Programmer's Request: {line}"})

        if 'openai' in self.client_type:
            for completion in self.client.get_completion(list(feature_messages), model=self.openai_model, temperature=self.openai_model_temperature):
                print(completion, end='')
        else:
            for completion in self.client.get_completion(list(feature_messages)):
                print(completion, end='')
        print()

    @error_handler
    def do_readme(self, line):
        """Request a README.md for your project's Github Repository from GPT.

        Usage:
        readme

        Description:
        This command generates a README.md file for your project's Github repository. The AI assistant
        will analyze your project and create documentation that includes setup instructions, usage,
        features, and other relevant details.
        """


        readme_messages = [
            {"role": "system", "content": "You are a AI Code Documentation Creator. You Create & Update README files for the projects Github Repositories."},
        ]

        project_details = f"This is a {self.project_type} project, the project uses {self.project_language}."
        if self.project_framework:
            project_details += f" and {self.project_framework} framework."
        readme_messages.append({"role": "user", "content": project_details})

        readme_messages.extend(
            [{"role": "user", "content": f"File: {path} Content: {content}"} for file in self.files_and_content for path, content in file.items()]
        )

        if line:
            readme_messages.append({"role": "user", "content": f"User Request: {line}"})

        if 'openai' in self.client_type:
            for completion in self.client.get_completion(list(readme_messages), model=self.openai_model, temperature=self.openai_model_temperature):
                print(completion, end='')
        else:
            for completion in self.client.get_completion(list(readme_messages)):
                print(completion, end='')
        print()

def main():
    prompt = CodeDebuggerShell()

    if platform.system() == 'Windows':
        pyreadline.Readline.parse_and_bind("tab: complete")
    else:
        readline.parse_and_bind("tab: complete")

    prompt.cmdloop()

if __name__ == '__main__':
    main()