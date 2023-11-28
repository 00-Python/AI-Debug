import os


def scrape_contents(files):
    files_and_content = list()
    for file in files:
        if file.endswith(('.py', '.md', '.html', '.css', 'scss', 'java', 'xml', 'c', 'cpp', 'h', 'lock', 'toml', 'rs', 'json')) and os.path.isfile(file):
            with open(file, 'r', errors='ignore') as f:
                contents = f.read().strip()

            data = {file: contents}

            files_and_content.append(data)

    # output is a list of dictionaries. the dictionaries have the key as the path of the file and the value the contents
    return files_and_content
