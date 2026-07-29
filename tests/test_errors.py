"""Unit tests for error handling, AST line/column tracking, and call stack trace formatting in Min."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from min import run, tokenize, parse, Interpreter
from min.errors import MinError, SyntaxError, RuntimeError, NameError, CallFrame


class TestErrorDiagnostics(unittest.TestCase):

    def test_syntax_error_location(self):
        source = ":x 10\n:y 20\n!unknown_command"
        try:
            run(source, "test_syntax.min")
            self.fail("Expected SyntaxError")
        except MinError as e:
            self.assertIsInstance(e, SyntaxError)
            self.assertEqual(e.line, 3)
            self.assertEqual(e.col, 1)

    def test_zero_division_runtime_error(self):
        source = ":a 10\n:b 0\n:c (/ a b)"
        try:
            run(source, "test_divzero.min")
            self.fail("Expected RuntimeError for division by zero")
        except MinError as e:
            self.assertIsInstance(e, RuntimeError)
            self.assertEqual(e.line, 3)
            self.assertIn("Division by zero", e.message)
            pretty = e.format_pretty(source)
            self.assertIn("Line 3:5 RuntimeError: Division by zero", pretty)
            self.assertIn("3 | :c (/ a b)", pretty)
            self.assertIn("^", pretty)

    def test_undefined_variable_name_error(self):
        source = ":a 5\n:b (+ a undefined_var)"
        try:
            run(source, "test_name_error.min")
            self.fail("Expected NameError")
        except MinError as e:
            self.assertIsInstance(e, NameError)
            self.assertEqual(e.line, 2)
            self.assertIn("Undefined: undefined_var", e.message)

    def test_nested_call_stack_trace(self):
        source = (
            "@deep_fail(x) [\n"
            "  / x 0\n"
            "]\n"
            "@outer(val) [\n"
            "  @deep_fail(val)\n"
            "]\n"
            "@outer(42)\n"
        )
        try:
            run(source, "test_stack.min")
            self.fail("Expected RuntimeError in deep function call")
        except MinError as e:
            self.assertIsInstance(e, RuntimeError)
            self.assertEqual(e.line, 2)
            self.assertTrue(len(e.stack_trace) >= 2)
            # Verify call stack frames order
            self.assertEqual(e.stack_trace[0].fn_name, "@outer")
            self.assertEqual(e.stack_trace[1].fn_name, "@deep_fail")
            pretty = e.format_pretty(source)
            self.assertIn("Traceback (most recent call last):", pretty)
            self.assertIn('File "test_stack.min", line 7, in @outer', pretty)
            self.assertIn('File "test_stack.min", line 5, in @deep_fail', pretty)
            self.assertIn("Line 2:3 RuntimeError: Division by zero", pretty)
            self.assertIn("2 |   / x 0", pretty)

    def test_try_catch_recovers_from_runtime_error(self):
        source = (
            ":err_msg \"\"\n"
            "!try [\n"
            "  :x (/ 10 0)\n"
            "] !catch (e) [\n"
            "  :err_msg e\n"
            "]\n"
            "err_msg\n"
        )
        result = run(source, "test_try_catch.min")
        self.assertEqual(result, "Division by zero")

    def test_ast_node_locations(self):
        source = ":x 100\n:y 200"
        tokens = tokenize(source)
        ast = parse(tokens, "test_ast.min")
        self.assertEqual(ast.statements[0].line, 1)
        self.assertEqual(ast.statements[0].col, 1)
        self.assertEqual(ast.statements[1].line, 2)
        self.assertEqual(ast.statements[1].col, 1)


if __name__ == "__main__":
    unittest.main()
