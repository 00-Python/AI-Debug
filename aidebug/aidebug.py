import re
import os
import cmd
import sys
import subprocess

import platform
if platform.system() == 'Windows':
    import pyreadline
else:
    import readline


from colorama import Fore, Back, Style, init
from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit.styles import Style as PromptStyle


from .core.utils.error_handler import error_handler
from .core.utils.update_codebase import update_codebase
from .core.clients.openai.clientv2 import OpenAIClient


from .core.commands.project import project_command
from .core.commands.config import config_command
from .core.commands.debug import debug_command
from .core.commands.feature import feature_command

class CodeDebuggerShell(cmd.Cmd):

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.venv_path = ""
        self.venv_name = ""
        self.use_venv = False

        self.files = list()
        self.files_and_content = list()
        self.project_language = ""
        self.project_type = ""
        self.project_framework = ""
        self.project_base_directory = ""
        self.project_run_command = ""

        self.api_host = os.getenv("OPENAI_API_HOST", "https://api.openai.com")
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAIClient(self.api_host, self.api_key)
        self.openai_model: str = "gpt-3.5-turbo-16k"
        self.openai_model_temperature: float = 1
        self.messages = list()
    
    @error_handler
    def preloop(self):
        # Check if a virtual environment is active
        venv_path = os.environ.get("VIRTUAL_ENV")
        if venv_path:
            self.use_venv = True
            self.venv_path = venv_path
            self.venv_name = re.search(r'\b\w+\b$', self.venv_path).group()
            # TODO - Handle errors here!
            os.system(f"source '{self.venv_path}/bin/activate'")
            self.prompt = f"{Fore.GREEN}AIDebug {Fore.RESET}{Fore.RED}@ {Fore.RESET}{Fore.GREEN}({self.venv_name}) {Fore.RESET}{Fore.YELLOW}> {Fore.RESET}"
    
    # Default - Here we configure the shell "passthrough"
    @error_handler
    def default(self, line):
        # Split the command into arguments
        command = line.split()

        if command[0] == 'cd':
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
    
    # Exit Command 
    @error_handler
    def do_exit(self, _):
        '''Exit AIDebug Console'''
        return True

    # Project Command
    @error_handler
    def do_project(self, line):
        '''Perform project related operations. Available subcommands include:

        select: Prompts the user with a directory browser to select project files and directories.
        deselect: Allows users to unselect previously selected files via a directory browser.
        run: Runs the project using the previously set `project_run_command`.
        files: Displays the currently selected file paths or file contents.

        Usage: 
        project select -> Launches directory browser to select files.
        project deselect -> Launches directory browser to deselect files.
        project run -> Runs the project using configured run command.
        project files paths -> Prints selected files paths.
        project files contents -> Prints selected files path and contents.
        '''
        update_codebase(self.files_and_content)
        project_command(self, line)

    # Tab Completion for the project command
    @error_handler
    def complete_project(self, text, line, begidx, endidx):
        """Tab complete for 'project' subcommands."""
        subcommands = ['select', 'deselect', 'run', 'files']
        if line.startswith('project files'):
            subcommands = ['paths', 'contents']
        completions = [command for command in subcommands if command.startswith(text)]
        return completions

    # Config Command
    @error_handler
    def do_config(self, line):
        '''Configure project and OpenAI specifics. Available subcommands include:

        project: Options to set the project language, type, framework and run command.
        openai: Options to set the OpenAI model and temperature.

        Usage: 
        config project language -> Prompts user to input project language.
        config project type -> Prompts to describe the type of project.
        config project framework -> Prompts to input the framework used in project.
        config project run -> Prompts to input the command to run the project.
        config openai model -> Sets the OpenAI model.
        config openai temperature -> Sets model temperature.
        '''
        config_command(self, line)

    # Tab completion for config command
    @error_handler
    def complete_config(self, text, line, begidx, endidx):
        subcommands = ['project', 'openai']
        if line.startswith('config project'):
            subcommands = ['language', 'type', 'framework', 'run']
        elif line.startswith('config openai'):
            subcommands = ['model', 'temperature']
        completions = [command for command in subcommands if command.startswith(text)]
        return completions

    # Debug Command
    @error_handler
    def do_debug(self, line):
        '''
        Debug project with GPT. Input the error message as the argument to the debug command.

        Usage: 
        debug <error message> -> Provide the error message as an argument.
        '''
        update_codebase(self.files_and_content)
        debug_command(self, line)

    # Feature Command
    @error_handler
    def do_feature(self, line):
        '''Request a feature for your project from GPT. Describe the required feature as an argument.

        Usage: 
        feature <feature description> -> Describe the required feature as an argument.
        '''
        update_codebase(self.files_and_content)
        feature_command(self, line)

    # Readme Command
    @error_handler
    def do_readme(self, line):
        '''Request a README.md for your projects Github Repository from GPT.
        '''
        update_codebase(self.files_and_content)
        readme_command(self, line)


def main():
    prompt = CodeDebuggerShell()

    if platform.system() == 'Windows':
        pyreadline.Readline.parse_and_bind("tab: complete")
    else:
        readline.parse_and_bind("tab: complete")

    prompt.prompt = f'{Fore.GREEN}AIDebug{Fore.RESET} {Fore.YELLOW}> {Fore.RESET}'
    prompt.cmdloop(f'''{Fore.BLUE}

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
    ''')

if __name__ == '__main__':
    main()
