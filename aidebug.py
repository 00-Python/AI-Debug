#!/usr/bin/env python3
import re
import os
import cmd
import sys
import readline
import subprocess

from colorama import Fore, Back, Style, init
from aidebug.gui.select_dirs import DirectoryBrowser
from aidebug.utils.files_data import scrape_contents
from aidebug.utils.error_handler import error_handler
from aidebug.clientv2.clientv2 import OpenAIClient
from PyQt5.QtWidgets import QApplication


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

    @error_handler
    def do_exit(self, _):
        '''Exit AIDebug Console'''
        return True

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
        project files -> Prompts user to decide between displaying file paths or file contents.
        '''

        line = line.lower().split()

        if line[0] == 'select':
            """Select project files and directories."""
            selector = QApplication(sys.argv)
            window = DirectoryBrowser('Select Project Files: ')
            window.show()
            selector.exec_()
            self.files = list(set(window.selected_items))
            if len(self.files) != 0:
                if len(self.files) != 1:
                    print('Files Selected!')
                else:
                    print('File Selected')
            self.files_and_content = scrape_contents(self.files)

        elif line[0] == 'deselect':
            """Unselect files and directories by id."""
            deselector = QApplication(sys.argv)
            window = DirectoryBrowser('Select Files to Remove: ')
            window.show()
            deselector.exec_()

            files_to_remove = list(set(window.selected_items))

            if len(files_to_remove) != 0:
                for file in files_to_remove:
                    self.files.remove(file)
                print("Files Removed!")
            else:
                print("No files selected for removal.")
            self.files_and_content = scrape_contents(self.files)

        elif line[0] == 'run':
            '''Run project '''
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

                    if input("Debug Code?").lower() == "y":
                        self.do_debug(result.stderr)

            except Exception as e:
                print(f"An error occurred: {e}")

        elif line[0] == 'files':
            answer = int(
                input('1. Paths\n2. Paths and Content\n\n Select 1 or 2: '))
            if answer == 1:
                print(self.files)
            elif answer == 2:
                print(self.files_and_content)
            else:
                print('Wrong Choice.')

    @error_handler
    def complete_project(self, text, line, begidx, endidx):
        """Tab complete for 'project' subcommands."""
        subcommands = ['select', 'deselect', 'run', 'files']
        if not text:
            completions = subcommands[:]
        else:
            completions = [command for command in subcommands if command.startswith(text)]
        return completions

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

        line = line.lower().split()

        if line[0] == 'project':
            if line[1] == 'language':
                self.project_language = line[2]
            elif line[1] == 'type':
                self.project_type = input('What type of project is it? ')
            elif line[1] == 'framework':
                self.project_framework = input(
                    'What framework is your project using? ')
            elif line[1] == 'run':
                run_command = input('Enter command used to run project: ')
                self.project_run_command = str(run_command)
            else:
                print("Invalid Command!")
        elif line[0] == 'openai':
            if line[1] == 'model':
                self.openai_model = line[2]
            elif line[1] == 'temperature':
                self.openai_model_temperature = float(line[2])
            else:
                print("Invalid Command!")
        else:
            print("Invalid Command!")
    
    @error_handler
    def complete_config(self, text, line, begidx, endidx):
        subcommands = ['project', 'openai']
        if line.startswith('config project'):
            subcommands = ['language', 'type', 'framework', 'run']
        elif line.startswith('config openai'):
            subcommands = ['model', 'temperature']
        completions = [command for command in subcommands if command.startswith(text)]
        return completions

    @error_handler
    def do_debug(self, line):
        '''Debug project with GPT. Input the error message as the argument to the debug command.

        Usage: 
        debug <error message> -> Provide the error message as an argument.
        '''

        debug_messages = [
            {"role": "system", "content": "You are a AI coding assistant. That debugs and fixes code. Make sure to explain every error and mistake in the code that you find and fix."},
            # {"role": "user", "content": f"" },
        ]

        if self.project_framework:
            new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language} and {self.project_framework} framework."}
            debug_messages.append(new_message)
        else:
            new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language}."}
            debug_messages.append(new_message)

        codebase_message = [
            {"role": "user", "content": "Here is the relevant codebase:"},]

        for file in self.files_and_content:
            for path, content in file.items():
                message = {"role": "user", "content": f"File: {path} Content: {content}"}
                codebase_message.append(message)
        
        error_message = {"role": "user", "content": f"This is the problem with the code: {line}" }
        codebase_message.append(error_message)

        for message in codebase_message:
            debug_messages.append(message)

        for completion in self.client.get_completion(list(debug_messages), model=self.openai_model, temperature=self.openai_model_temperature):
            print(completion, end='')
        print()

    @error_handler
    def do_feature(self, line):
        '''Request a feature for your project from GPT. Describe the required feature as an argument.

        Usage: 
        feature <feature description> -> Describe the required feature as an argument.
        '''

        feature_messages = [
            {"role": "system", "content": "You are a AI coding assistant. Upon request you imporove code, create features and refactor code."},
            # {"role": "user", "content": f"" },
        ]

        if self.project_framework:
            new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language} and {self.project_framework} framework."}
            feature_messages.append(new_message)
        else:
            new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language}."}
            feature_messages.append(new_message)

        codebase_message = [
            {"role": "user", "content": "Here is the relevant codebase:"},]

        for file in self.files_and_content:
            for path, content in file.items():
                message = {"role": "user", "content": f"File: {path} Content: {content}"}
                codebase_message.append(message)
        
        error_message = {"role": "user", "content": f"Programmer's Request: {line}" }
        codebase_message.append(error_message)

        for message in codebase_message:
            feature_messages.append(message)

        for completion in self.client.get_completion(list(feature_messages), model=self.openai_model, temperature=self.openai_model_temperature):
            print(completion, end='')
        print()

    @error_handler
    def do_readme(self, line):
        '''Request a README.md for your projects Github Repository from GPT.
        '''

        feature_messages = [
            {"role": "system", "content": "You are a AI Code Documentation Creator. You Create README filed for projects Github page."},
            # {"role": "user", "content": f"" },
        ]

        if self.project_framework:
            new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language} and {self.project_framework} framework."}
            feature_messages.append(new_message)
        else:
            new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language}."}
            feature_messages.append(new_message)

        codebase_message = [
            {"role": "user", "content": "Here is the relevant codebase:"},]

        for file in self.files_and_content:
            for path, content in file.items():
                print(path)
                message = {"role": "user", "content": f"File: {path} Content: {content}"}
                codebase_message.append(message)

        for message in codebase_message:
            feature_messages.append(message)

        for completion in self.client.get_completion(list(feature_messages), model=self.openai_model, temperature=self.openai_model_temperature):
            print(completion, end='')
        print()


if __name__ == "__main__":
    prompt = CodeDebuggerShell()
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
{Fore.CYAN}By J. Webster-Colby\nGithub: https://github.com/00-Python{Fore.RESET}

Type {Fore.RED}help{Fore.RESET} for a list of commands.
''')
