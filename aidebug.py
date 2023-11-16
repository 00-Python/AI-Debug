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

    def do_exit(self, _):
        '''Exit AIDebug Console'''
        return True

    def do_project(self, line):
        '''Project related commands'''
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

    def do_config(self, line):
        '''Configure specific project details.
        1.config project
            1.1. config project language
                Set the programing languages your project is using ex. python, html and css

            1.2. config project type
                Set project type, i.e is it a Web Development project? Is it a game development project?...

            1.3. config project framework
                Set Frameworks that your project is using ex. Flask, Django...

            1.4. config project run
                Configure the comand that is used to run your project ex. python app.py
                    
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

    def do_debug(self, line):
        '''Debug project with GPT'''

        debug_messages = [
            {"role": "system", "content": "You are a AI coding assistant. That debugs and fixes code."},
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

    def do_feature(self, line):
        '''Request a feature for your project from GPT'''
        pass


if __name__ == "__main__":
    prompt = CodeDebuggerShell()
    # readline.parse_and_bind("tab: complete")

    prompt.prompt = f'{Fore.GREEN}AIDebug{Fore.RESET} {Fore.YELLOW}> {Fore.RESET}'
    prompt.cmdloop(f'''{Fore.BLUE}
  **    ***     *****           *                       
 *  *    *       *   *          *                       
*    *   *       *   *   ****   *       *    *   *** *  
*    *   *       *   *  *    *  * ***   *    *  *   *   
******   *       *   *  ******  *    *  *    *  *   *   
*    *   *       *   *  *       *    *  *    *   ***    
*    *   *       *   *  *    *  **   *  *   **  *       
*    *  ***     *****    ****   * ***    *** *   ****   
________________________________________________*    *___{Fore.RESET}
{Fore.CYAN}By JR Webster-Colby{Fore.RESET}                             {Fore.BLUE} ****  {Fore.RESET} 

Type {Fore.RED}help{Fore.RESET} for a list of commands.
''')
