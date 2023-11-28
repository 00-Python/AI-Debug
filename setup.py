from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.1.3'
DESCRIPTION = 'AI Coding Assistant Shell'
LONG_DESCRIPTION = '''AIDebug Console is a Python-based command line application that leverages the power of OpenAI's GPT models to assist with debugging and developing software projects. It provides a user-friendly interface for interacting with your codebase, running your project, and even debugging your code with the help of AI.'''

# Setting up
setup(
    name="aidebug",
    version=VERSION,
    author="00-Python (Joseph Webster)",
    author_email="<rwc.webster@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['PyQt5', 'colorama', 'requests', 'urllib3', 'idna', 'prompt_toolkit', 'pygments', 'pyreadline'],
    keywords=['aidebug', 'ai debug', 'ai debugging', 'debug with AI', 'Code with ai', 'ai programming', 'python', 'AI', 'Coding Assistant', 'AI Coding', 'OpenAI', 'GPT-4', 'GPT'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: Microsoft :: Windows",
    ],
    entry_points={
        'console_scripts': [
            'aidebug = aidebug.aidebug:main',
        ],
    },
)
