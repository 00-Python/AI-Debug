def config_command(self, line):
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
