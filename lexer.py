"""Lexer/Tokenizer for the Min language."""

from .tokens import TT, Token, KEYWORDS
from .errors import SyntaxError


class Lexer:
    """Converts source code into tokens."""
    
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
    
    def tokenize(self) -> list[Token]:
        """Tokenize the entire source code."""
        while self.pos < len(self.source):
            char = self.source[self.pos]
            
            # Skip whitespace (except newline)
            if char in (' ', '\t', '\r'):
                self.advance()
                continue
            
            # Newlines
            if char == '\n':
                self.tokens.append(Token(TT.NEWLINE, '\\n', self.line, self.col))
                self.advance()
                self.line += 1
                self.col = 1
                continue
            
            # Booleans and null (#true, #false, #null)
            if char == '#' and self.peek_ahead(1) in ('t', 'f', 'n'):
                self.read_identifier()
                continue
            
            # Skip comments (# to end of line)
            if char == '#':
                while self.pos < len(self.source) and self.source[self.pos] != '\n':
                    self.advance()
                continue
            
            # Strings
            if char == '"':
                self.read_string()
                continue
            
            # Numbers
            if char.isdigit() or (char == '.' and self.peek_ahead(1).isdigit()):
                self.read_number()
                continue
            
            # Identifiers and keywords
            if char.isalpha() or char == '_':
                self.read_identifier()
                continue
            
            # Operators and special characters
            self.read_operator()
        
        self.tokens.append(Token(TT.EOF, None, self.line, self.col))
        return self.tokens
    
    def advance(self) -> str:
        """Advance to next character."""
        char = self.source[self.pos]
        self.pos += 1
        self.col += 1
        return char
    
    def peek_ahead(self, offset: int = 1) -> str:
        """Peek ahead without advancing."""
        pos = self.pos + offset
        if pos < len(self.source):
            return self.source[pos]
        return '\0'
    
    def add_token(self, tt: TT, value=None, col: int | None = None):
        """Add a token to the list."""
        c = col if col is not None else self.col
        self.tokens.append(Token(tt, value, self.line, c))

    def read_string(self):
        """Read a string literal."""
        start_col = self.col
        self.advance()  # skip opening "
        result = []
        
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char == '"':
                self.advance()  # skip closing "
                self.tokens.append(Token(TT.STR, ''.join(result), self.line, start_col))
                return
            if char == '\\':
                self.advance()
                escape = self.source[self.pos] if self.pos < len(self.source) else ''
                if escape == 'n': result.append('\n')
                elif escape == 't': result.append('\t')
                elif escape == '\\': result.append('\\')
                elif escape == '"': result.append('"')
                else: result.append(escape)
            else:
                result.append(char)
            self.advance()
        
        raise SyntaxError("Unterminated string", self.line, start_col)
    
    def read_number(self):
        """Read a number literal."""
        start_col = self.col
        result = []
        has_dot = False
        
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char.isdigit():
                result.append(char)
                self.advance()
            elif char == '.' and not has_dot:
                has_dot = True
                result.append(char)
                self.advance()
            else:
                break
        
        value = float(''.join(result)) if has_dot else int(''.join(result))
        self.tokens.append(Token(TT.NUM, value, self.line, start_col))
    
    def read_identifier(self):
        """Read an identifier or keyword."""
        start_col = self.col
        result = []
        
        while self.pos < len(self.source):
            char = self.source[self.pos]
            if char.isalnum() or char == '_':
                result.append(char)
                self.advance()
            else:
                break
        
        word = ''.join(result)
        
        # Check for booleans
        if word == '#true':
            self.tokens.append(Token(TT.BOOL, True, self.line, start_col))
        elif word == '#false':
            self.tokens.append(Token(TT.BOOL, False, self.line, start_col))
        elif word == '#null':
            self.tokens.append(Token(TT.NULL, None, self.line, start_col))
        else:
            self.tokens.append(Token(TT.IDENT, word, self.line, start_col))
    
    def read_operator(self):
        """Read an operator or special character."""
        char = self.source[self.pos]
        start_col = self.col
        next_char = self.peek_ahead()
        
        # Two-character operators
        if char == '>' and next_char == '=':
            self.advance()
            self.advance()
            self.add_token(TT.GTE, '>=', start_col)
            return
        if char == '<' and next_char == '=':
            self.advance()
            self.advance()
            self.add_token(TT.LTE, '<=', start_col)
            return
        if char == '!' and next_char == '=':
            self.advance()
            self.advance()
            self.add_token(TT.NEQ, '!=', start_col)
            return
        
        # Single-character operators
        op_map = {
            '+': TT.PLUS, '-': TT.MINUS, '*': TT.STAR,
            '/': TT.SLASH, '%': TT.PERCENT,
            '=': TT.EQ, '>': TT.GT, '<': TT.LT,
            '&': TT.AND, '|': TT.OR,
            '(': TT.LPAREN, ')': TT.RPAREN,
            '[': TT.LBRACKET, ']': TT.RBRACKET,
            '{': TT.LBRACE, '}': TT.RBRACE,
            '@': TT.AT, ':': TT.COLON, '.': TT.DOT,
            '?': TT.QUESTION, '~': TT.TILDE,
        }
        
        if char in op_map:
            self.advance()
            self.add_token(op_map[char], char, start_col)
            return
        
        # Check for keywords starting with !
        if char == '!':
            word = '!'
            self.advance()
            while self.pos < len(self.source) and (self.source[self.pos].isalpha() or self.source[self.pos] == '_'):
                word += self.source[self.pos]
                self.advance()
            
            if word in KEYWORDS:
                self.add_token(KEYWORDS[word], word, start_col)
            elif word == '!':
                self.add_token(TT.BANG, '!', start_col)
            else:
                raise SyntaxError(f"Unknown keyword: {word}", self.line, start_col)
            return
        
        raise SyntaxError(f"Unexpected character: {char}", self.line, start_col)


def tokenize(source: str) -> list[Token]:
    """Convenience function to tokenize source code."""
    return Lexer(source).tokenize()
