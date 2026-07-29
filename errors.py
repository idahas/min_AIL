"""Error types for the Min language."""

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CallFrame:
    """A single frame in the call stack."""
    fn_name: str
    filename: str
    line: int
    col: int


class MinError(Exception):
    """Base error for all Min errors."""
    
    def __init__(
        self,
        message: str,
        line: int = 0,
        col: int = 0,
        filename: str = "<input>",
        stack_trace: Optional[List[CallFrame]] = None,
        source: Optional[str] = None
    ):
        self.message = message
        self.line = line
        self.col = col
        self.filename = filename
        self.stack_trace = list(stack_trace) if stack_trace else []
        self.source = source
        super().__init__(self._format())
    
    def format_pretty(self, source: Optional[str] = None) -> str:
        """Format error with traceback, line snippet, and caret pointer."""
        src = source if source is not None else self.source
        lines = []
        
        if self.stack_trace:
            lines.append("Traceback (most recent call last):")
            for frame in self.stack_trace:
                lines.append(f'  File "{frame.filename}", line {frame.line}, in {frame.fn_name}')
        
        error_type = self.__class__.__name__
        if self.line:
            loc = f"Line {self.line}:{self.col}"
            lines.append(f"{loc} {error_type}: {self.message}")
        else:
            lines.append(f"{error_type}: {self.message}")
            
        if src and self.line > 0:
            src_lines = src.splitlines()
            if 0 <= self.line - 1 < len(src_lines):
                line_str = src_lines[self.line - 1]
                line_num_str = f"  {self.line} | "
                lines.append(f"{line_num_str}{line_str}")
                
                caret_offset = max(0, self.col - 1)
                caret_line = " " * len(line_num_str) + " " * caret_offset + "^"
                lines.append(caret_line)
                
        return "\n".join(lines)
    
    def _format(self):
        return self.format_pretty()


class SyntaxError(MinError):
    """Syntax/parse error."""
    pass


class RuntimeError(MinError):
    """Runtime execution error."""
    pass


class TypeError(MinError):
    """Type mismatch error."""
    pass


class NameError(MinError):
    """Undefined variable/function error."""
    pass


class IndexError(MinError):
    """Array index out of bounds error."""
    pass


class ImportError(MinError):
    """Module import error."""
    pass


class ArgumentError(MinError):
    """Wrong number of arguments error."""
    pass


class AttributeError(MinError):
    """Invalid attribute access error."""
    pass
