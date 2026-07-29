"""Unit tests for Min language anonymous lambdas and !match pattern matching."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from min import run


class TestAdvancedFeatures(unittest.TestCase):

    def test_anonymous_lambdas(self):
        # Inline lambda with map
        source_map = '@map([1:2:3:4]: @(x) [* x 10])'
        self.assertEqual(run(source_map), [10, 20, 30, 40])

        # Inline lambda capturing outer scope variable
        source_closure = (
            ':factor 5\n'
            '@map([1:2:3]: @(x) [* x factor])\n'
        )
        self.assertEqual(run(source_closure), [5, 10, 15])

        # Inline lambda with filter
        source_filter = '@filter([1:2:3:4:5:6]: @(x) [= (% x 2) 0])'
        self.assertEqual(run(source_filter), [2, 4, 6])

    def test_pattern_matching(self):
        # Matching exact branch
        source_match_1 = (
            ':val 2\n'
            '!match (val) [\n'
            '  1 ["one"]\n'
            '  2 ["two"]\n'
            '  3 ["three"]\n'
            '  !else ["unknown"]\n'
            ']\n'
        )
        self.assertEqual(run(source_match_1), "two")

        # Fallback to !else
        source_match_else = (
            ':val 99\n'
            '!match (val) [\n'
            '  1 ["one"]\n'
            '  2 ["two"]\n'
            '  !else ["fallback"]\n'
            ']\n'
        )
        self.assertEqual(run(source_match_else), "fallback")


if __name__ == "__main__":
    unittest.main()
