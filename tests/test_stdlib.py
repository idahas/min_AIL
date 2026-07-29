"""Unit tests for Min language expanded standard library functions."""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from min import run
from min.errors import MinError


class TestStandardLibrary(unittest.TestCase):

    def test_file_io(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = os.path.join(tmpdir, "test.txt").replace("\\", "/")
            
            # File exists check (False initially)
            source_exists = f'@file_exists("{test_file}")'
            self.assertFalse(run(source_exists))

            # Write file
            source_write = f'@write_file("{test_file}": "Hello Min File!")'
            self.assertTrue(run(source_write))

            # File exists check (True after write)
            self.assertTrue(run(source_exists))

            # Read file
            source_read = f'@read_file("{test_file}")'
            self.assertEqual(run(source_read), "Hello Min File!")

            # Append file
            source_append = f'@append_file("{test_file}": " More text.")'
            self.assertTrue(run(source_append))
            self.assertEqual(run(source_read), "Hello Min File! More text.")

            # Delete file
            source_delete = f'@delete_file("{test_file}")'
            self.assertTrue(run(source_delete))
            self.assertFalse(run(source_exists))

    def test_math_functions(self):
        self.assertEqual(run("@pow(2: 3)"), 8.0)
        self.assertEqual(run("@floor(3.9)"), 3)
        self.assertEqual(run("@ceil(3.1)"), 4)
        self.assertEqual(run("@round(3.567: 2)"), 3.57)

        rand_val = run("@random()")
        self.assertTrue(0.0 <= rand_val < 1.0)

        rand_int = run("@randint(1: 10)")
        self.assertTrue(1 <= rand_int <= 10)

    def test_getenv(self):
        os.environ["MIN_TEST_VAR"] = "antigravity"
        self.assertEqual(run('@getenv("MIN_TEST_VAR")'), "antigravity")
        self.assertEqual(run('@getenv("NON_EXISTENT_VAR": "default_val")'), "default_val")

    def test_higher_order_functions_with_closure(self):
        # Map with outer variable factor
        source_map = (
            ":factor 3\n"
            "@triple(x) [* x factor]\n"
            "@map([1:2:3:4]: triple)\n"
        )
        self.assertEqual(run(source_map), [3, 6, 9, 12])

        # Filter with outer variable min_val
        source_filter = (
            ":min_val 5\n"
            "@is_above(x) [> x min_val]\n"
            "@filter([2:4:6:8:10]: is_above)\n"
        )
        self.assertEqual(run(source_filter), [6, 8, 10])

        # Reduce with custom accumulator function
        source_reduce = (
            "@sum_sq(acc x) [+ acc (* x x)]\n"
            "@reduce([1:2:3:4]: sum_sq: 0)\n"
        )
        self.assertEqual(run(source_reduce), 30)


if __name__ == "__main__":
    unittest.main()
