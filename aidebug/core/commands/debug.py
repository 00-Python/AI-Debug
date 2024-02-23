def debug_command(self, line):
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
