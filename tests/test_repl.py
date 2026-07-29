"""Unit tests for REPL bracket balancing, state persistence, and meta-commands."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from min.__main__ import is_balanced
from min import tokenize, parse, Interpreter


class TestREPLEnhancements(unittest.TestCase):

    def test_is_balanced_bracket_helper(self):
        # Single line balanced
        self.assertTrue(is_balanced(":x 10"))
        self.assertTrue(is_balanced("@add(a b) [:a (+ a b)]"))

        # Unbalanced opening brackets
        self.assertFalse(is_balanced("@add(a b) ["))
        self.assertFalse(is_balanced(":person {name: \"John\""))
        self.assertFalse(is_balanced("(/ 10 (+ 2 3"))

        # String literals containing brackets should be ignored
        self.assertTrue(is_balanced(':str "[unclosed bracket in string"'))
        self.assertTrue(is_balanced(':str "(unclosed paren in string"'))

        # Comments containing brackets should be ignored
        self.assertTrue(is_balanced(":x 10 # [unclosed bracket in comment"))

    def test_repl_state_persistence(self):
        interp = Interpreter(filename="<repl>")

        # Command 1: Define variable x
        ast1 = parse(tokenize(":x 42"), filename="<repl>")
        self.assertEqual(interp.run(ast1), 42)

        # Command 2: Use variable x to compute y
        ast2 = parse(tokenize(":y (+ x 8)"), filename="<repl>")
        self.assertEqual(interp.run(ast2), 50)

        # Command 3: Retrieve y
        ast3 = parse(tokenize("y"), filename="<repl>")
        self.assertEqual(interp.run(ast3), 50)

        # Command 4: Define function using x and y
        fn_code = (
            "@calc(z) [\n"
            "  + (+ x y) z\n"
            "]"
        )
        ast4 = parse(tokenize(fn_code), filename="<repl>")
        interp.run(ast4)

        # Command 5: Call defined function
        ast5 = parse(tokenize("@calc(10)"), filename="<repl>")
        self.assertEqual(interp.run(ast5), 102)


if __name__ == "__main__":
    unittest.main()
