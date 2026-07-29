"""Token types for the Min language."""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any


class TT(Enum):
    """Token Types."""
    # Literals
    NUM = auto()        # 42, 3.14
    STR = auto()        # "hello"
    BOOL = auto()       # #true, #false
    NULL = auto()       # #null
    
    # Identifiers & Keywords
    IDENT = auto()      # variable names
    AT = auto()         # @ function/class
    COLON = auto()      # : assignment
    DOT = auto()        # . dot access
    
    # Grouping
    LPAREN = auto()     # (
    RPAREN = auto()     # )
    LBRACKET = auto()   # [
    RBRACKET = auto()   # ]
    LBRACE = auto()     # {
    RBRACE = auto()     # }
    
    # Operators
    PLUS = auto()       # +
    MINUS = auto()      # -
    STAR = auto()       # *
    SLASH = auto()      # /
    PERCENT = auto()    # %
    BANG = auto()       # ! commands
    QUESTION = auto()   # ? if
    TILDE = auto()      # ~ return
    
    # Comparison
    EQ = auto()         # =
    GT = auto()         # >
    LT = auto()         # <
    GTE = auto()        # >=
    LTE = auto()        # <=
    NEQ = auto()        # !=
    
    # Logical
    AND = auto()        # &
    OR = auto()         # |
    
    # Special
    NEWLINE = auto()    # newline
    EOF = auto()        # end of file
    
    # Keywords (prefixed with !)
    IF = auto()         # !if
    ELSE = auto()       # !else
    WHILE = auto()      # !while
    FOR = auto()        # !for
    BREAK = auto()      # !break
    CONTINUE = auto()   # !continue
    RETURN = auto()     # !return
    IMPORT = auto()     # !import
    EXPORT = auto()     # !export
    AS = auto()         # !as
    TRY = auto()        # !try
    CATCH = auto()      # !catch
    THROW = auto()      # !throw
    PRINT = auto()      # !print
    INPUT = auto()      # !input
    CLASS = auto()      # !class
    NEW = auto()        # !new
    THIS = auto()       # !this
    EXTENDS = auto()    # !extends
    MATCH = auto()      # !match
    YIELD = auto()      # !yield


KEYWORDS = {
    "!if": TT.IF,
    "!else": TT.ELSE,
    "!while": TT.WHILE,
    "!for": TT.FOR,
    "!break": TT.BREAK,
    "!continue": TT.CONTINUE,
    "!return": TT.RETURN,
    "!import": TT.IMPORT,
    "!export": TT.EXPORT,
    "!as": TT.AS,
    "!try": TT.TRY,
    "!catch": TT.CATCH,
    "!throw": TT.THROW,
    "!print": TT.PRINT,
    "!input": TT.INPUT,
    "!class": TT.CLASS,
    "!new": TT.NEW,
    "!this": TT.THIS,
    "!extends": TT.EXTENDS,
    "!match": TT.MATCH,
    "!yield": TT.YIELD,
}


@dataclass
class Token:
    """A single token."""
    type: TT
    value: Any
    line: int
    col: int
    
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, L{self.line}:C{self.col})"
