#!/usr/bin/env python3
"""Min language - REPL and file runner."""

import sys
import os

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from min import run
from min.errors import MinError
from min.tokens import KEYWORDS


class Color:
    """ANSI terminal colors."""
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def is_balanced(code: str) -> bool:
    """Check if all brackets [, {, ( in code are balanced."""
    stack = []
    in_string = False
    escape = False

    for char in code:
        if in_string:
            if escape:
                escape = False
            elif char == '\\':
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == '#':
            break
        elif char in ('[', '{', '('):
            stack.append(char)
        elif char in (']', '}', ')'):
            if not stack:
                return True
            top = stack[-1]
            if (char == ']' and top == '[') or (char == '}' and top == '{') or (char == ')' and top == '('):
                stack.pop()

    return len(stack) == 0


def setup_readline(interp):
    """Setup readline autocompletion."""
    try:
        import readline
        
        def completer(text, state):
            keywords = list(KEYWORDS.keys()) + [
                "!vars", "!help", "!clear", "!exit", "!quit"
            ]
            env_vars = list(interp.global_env.vars.keys())
            candidates = sorted(list(set(keywords + env_vars)))
            
            matches = [c for c in candidates if c.startswith(text)]
            if state < len(matches):
                return matches[state]
            return None

        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
    except Exception:
        pass


def show_help():
    """Display REPL help cheatsheet."""
    help_text = f"""
{Color.BOLD}Min Language Quick Reference:{Color.RESET}
  {Color.CYAN}:var val{Color.RESET}             Define / assign variable
  {Color.CYAN}@func(a b) [body]{Color.RESET}    Define function
  {Color.CYAN}(@func a: b){Color.RESET}          Call function
  {Color.CYAN}!class Name [body]{Color.RESET}   Define class
  {Color.CYAN}!print expr{Color.RESET}          Print output
  {Color.CYAN}? cond [then] [else]{Color.RESET} Conditional
  {Color.CYAN}!while cond [body]{Color.RESET}   While loop
  {Color.CYAN}!import "module"{Color.RESET}     Import module

{Color.BOLD}REPL Meta Commands:{Color.RESET}
  {Color.YELLOW}!vars{Color.RESET}   List session variables & functions
  {Color.YELLOW}!help{Color.RESET}   Show this help message
  {Color.YELLOW}!clear{Color.RESET}  Reset REPL environment
  {Color.YELLOW}!exit{Color.RESET}   Quit REPL
"""
    print(help_text)


def show_vars(interp):
    """Display all user-defined variables and functions in the session."""
    from min.builtins import BUILTINS
    user_vars = {k: v for k, v in interp.global_env.vars.items() if k not in BUILTINS}
    if not user_vars:
        print(f"{Color.YELLOW}No user-defined variables or functions in current session.{Color.RESET}")
        return

    print(f"\n{Color.BOLD}Session Variables & Functions:{Color.RESET}")
    for name, val in sorted(user_vars.items()):
        val_repr = repr(val)
        if len(val_repr) > 60:
            val_repr = val_repr[:57] + "..."
        print(f"  {Color.CYAN}{name}{Color.RESET} = {val_repr}")
    print()


def repl():
    """Interactive REPL with state persistence, multi-line input, and autocompletion."""
    from min.lexer import tokenize
    from min.parser import parse
    from min.interpreter import Interpreter

    interp = Interpreter(filename="<repl>")
    setup_readline(interp)

    print(f"{Color.BOLD}{Color.CYAN}Min v0.1.0 Interactive REPL{Color.RESET}")
    print("Type !help for syntax reference, !vars for session state, !exit to quit\n")

    buffer = []

    while True:
        try:
            prompt = f"{Color.BOLD}{Color.CYAN}min>{Color.RESET} " if not buffer else f"{Color.BOLD}{Color.CYAN}... {Color.RESET} "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Color.YELLOW}Bye!{Color.RESET}")
            break

        stripped = line.strip()
        if not buffer:
            if not stripped:
                continue
            if stripped in ("!exit", "!quit"):
                print(f"{Color.YELLOW}Bye!{Color.RESET}")
                break
            if stripped == "!help":
                show_help()
                continue
            if stripped == "!vars":
                show_vars(interp)
                continue
            if stripped == "!clear":
                interp = Interpreter(filename="<repl>")
                setup_readline(interp)
                print(f"{Color.GREEN}Environment cleared.{Color.RESET}")
                continue

        buffer.append(line)
        full_code = "\n".join(buffer)

        if not is_balanced(full_code):
            continue

        buffer.clear()

        try:
            tokens = tokenize(full_code)
            ast = parse(tokens, filename="<repl>")
            interp.source = full_code
            result = interp.run(ast)
            if result is not None:
                print(f"{Color.GREEN}{result!r}{Color.RESET}")
        except MinError as e:
            print(f"{Color.RED}{e.format_pretty(full_code)}{Color.RESET}")
        except Exception as e:
            print(f"{Color.RED}Error: {e}{Color.RESET}")


def run_file(filename: str):
    """Run a .min file."""
    if not os.path.exists(filename):
        print(f"Error: File not found: {filename}")
        sys.exit(1)
    
    with open(filename, 'r', encoding='utf-8') as f:
        source = f.read()
    
    try:
        run(source, filename)
    except MinError as e:
        print(e.format_pretty(source))
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def main():
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()


if __name__ == "__main__":
    main()
