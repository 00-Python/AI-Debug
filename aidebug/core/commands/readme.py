def readme_command(self, line):
    feature_messages = [
        {"role": "system", "content": "You are a AI Code Documentation Creator. You Create & Update README files for the projects Github page."},
        # {"role": "user", "content": f"" },
    ]

    if self.project_framework:
        new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language} and {self.project_framework} framework."}
        feature_messages.append(new_message)
    else:
        new_message = {"role": "user", "content": f"This is a {self.project_type} project, the project uses {self.project_language}."}
        feature_messages.append(new_message)

    codebase_message = [
        {"role": "user", "content": "Here is the relevant codebase, if there are any new features you should add them to the current README.md:"},]

    for file in self.files_and_content:
        for path, content in file.items():
            print(path)
            message = {"role": "user", "content": f"File: {path} Content: {content}"}
            codebase_message.append(message)
    
    if line:
        user_message = {"role": "user", "content": f"User Request: {line}"}
        codebase_message.append(user_message)


    for message in codebase_message:
        feature_messages.append(message)

    for completion in self.client.get_completion(list(feature_messages), model=self.openai_model, temperature=self.openai_model_temperature):
        print(completion, end='')
    print()