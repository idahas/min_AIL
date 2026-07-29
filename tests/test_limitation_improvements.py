"""Unit tests for Min language limitation improvements (string interpolation, default/variadic args, destructuring, list comprehensions, threading)."""

import unittest
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from min import run


class TestLimitationImprovements(unittest.TestCase):

    def test_string_interpolation(self):
        source = (
            ':name "Alice"\n'
            ':x 10\n'
            ':greeting "Hello {name}, 10 + 5 = {+ x 5}"\n'
            'greeting\n'
        )
        self.assertEqual(run(source), "Hello Alice, 10 + 5 = 15")

    def test_default_optional_arguments(self):
        source = (
            '@greet(name prefix="Hello") ["{prefix} {name}!"]\n'
            '@greet("Bob")\n'
        )
        self.assertEqual(run(source), "Hello Bob!")

        source_custom = (
            '@greet(name prefix="Hello") ["{prefix} {name}!"]\n'
            '@greet("Bob": "Hi")\n'
        )
        self.assertEqual(run(source_custom), "Hi Bob!")

    def test_variadic_rest_parameters(self):
        source = (
            '@sum_all(...items) [\n'
            '  @reduce(items: @(acc x) [+ acc x]: 0)\n'
            ']\n'
            '@sum_all(10: 20: 30: 40)\n'
        )
        self.assertEqual(run(source), 100)

    def test_destructuring_assignment(self):
        source = (
            '[:a :b] [100: 200]\n'
            '[+ a b]\n'
        )
        self.assertEqual(run(source), 300)

    def test_list_comprehension(self):
        # Basic list comprehension
        source_basic = '[for x [1:2:3:4] (* x 10)]'
        self.assertEqual(run(source_basic), [10, 20, 30, 40])

        # List comprehension with filtering condition
        source_filtered = '[for x [1:2:3:4:5:6] ? (> x 3) (* x 2)]'
        self.assertEqual(run(source_filtered), [8, 10, 12])

    def test_threading(self):
        source = (
            ':counter 0\n'
            '@increment() [\n'
            '  :counter (+ counter 1)\n'
            ']\n'
            '@thread(increment)\n'
        )
        t = run(source)
        t.join(timeout=1.0)
        self.assertIsNotNone(t)


if __name__ == "__main__":
    unittest.main()
