import sys
from ..gui.select_dirs import DirectoryBrowser
from ..utils.files_data import scrape_contents
from ..utils.highlight_code import highlight_code

from PyQt5.QtWidgets import QApplication


def project_command(self,line):
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
        if line[1] == 'paths':
            for indx, file in enumerate(self.files):
                print(f'{indx+1}. {file}')
            print()
        elif line[1] == 'content':
            print("File Contents:\n")
            for file_dict in self.files_and_content:
                for path, content in file_dict.items():
                    print(f"{Fore.RED}{path}{Fore.RESET}:\n")
                    highlight_code(path, content)
                    print()
        else:
            print('Wrong Choice.')
