from typing import List, Dict

def update_codebase(files_and_content: List[Dict[str, str]]) -> None:
    """Update the contents of the selected project files."""
    for file_info in files_and_content:
        for path in file_info.keys():
            with open(path, 'r') as file:
                content = file.read()
            file_info[path] = content