from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import TerminalFormatter

def highlight_code(path: str, code: str) -> None:
    lexer = get_lexer_for_filename(path, stripall=True)
    formatter = TerminalFormatter()
    highlighted_code = highlight(code, lexer, formatter)
    print(highlighted_code)