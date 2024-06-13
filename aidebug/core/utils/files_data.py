import os
from typing import Dict, List

def scrape_contents(files: List[str]) -> List[Dict[str, str]]:
    files_and_content = []
    for file in files:
        if not file.endswith('.pyc') and os.path.isfile(file):
            with open(file, 'r', errors='ignore') as f:
                contents = f.read().strip()
            files_and_content.append({file: contents})

    return files_and_content