"""Min - AI-optimized programming language."""

from .lexer import tokenize, Lexer
from .parser import parse, Parser
from .interpreter import Interpreter
from .ast_nodes import Program
from .errors import MinError

__version__ = "0.1.0"
__all__ = ["run", "tokenize", "parse", "Interpreter", "MinError"]


def run(source: str, filename: str = "<input>"):
    """Run Min source code."""
    tokens = tokenize(source)
    ast = parse(tokens, filename=filename)
    interp = Interpreter(filename=filename, source=source)
    return interp.run(ast)
