"""Unit tests for Min language enhanced module system and package loader."""

import unittest
import sys
import os
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from min import run
from min.errors import MinError, AttributeError as MinAttributeError


class TestModuleSystem(unittest.TestCase):

    def test_std_virtual_modules(self):
        # std/math
        source_math = (
            '!import "std/math" !as math\n'
            '! math sqrt 16\n'
        )
        self.assertEqual(run(source_math), 4.0)

        # std/string
        source_str = (
            '!import "std/string" !as str_utils\n'
            '! str_utils upper "hello min"\n'
        )
        self.assertEqual(run(source_str), "HELLO MIN")

        # std/array
        source_arr = (
            '!import "std/array" !as array_utils\n'
            '! array_utils slice [1:2:3:4:5] 1 4\n'
        )
        self.assertEqual(run(source_arr), [2, 3, 4])

    def test_relative_path_imports(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            pkg_dir = os.path.join(tmpdir, "pkg")
            os.makedirs(pkg_dir)

            # Helper module inside pkg/
            helper_path = os.path.join(pkg_dir, "helper.min")
            with open(helper_path, "w", encoding="utf-8") as f:
                f.write('@multiply(a b) [* a b]\n')

            # Main module inside pkg/ importing "helper"
            main_path = os.path.join(pkg_dir, "main.min")
            main_source = (
                '!import "helper"\n'
                '! helper multiply 6 7\n'
            )
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(main_source)

            # Run main.min
            result = run(main_source, filename=main_path)
            self.assertEqual(result, 42)

    def test_explicit_export_filtering(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            mod_path = os.path.join(tmpdir, "mod.min")
            mod_source = (
                ':public_val 100\n'
                ':private_val 999\n'
                '!export public_val\n'
            )
            with open(mod_path, "w", encoding="utf-8") as f:
                f.write(mod_source)

            main_path = os.path.join(tmpdir, "main.min")
            main_source = (
                '!import "mod"\n'
                '(. mod public_val)\n'
            )
            with open(main_path, "w", encoding="utf-8") as f:
                f.write(main_source)

            # Public symbol exists
            self.assertEqual(run(main_source, filename=main_path), 100)

            # Private symbol throws AttributeError when accessed on module object
            fail_source = (
                '!import "mod"\n'
                '(. mod private_val)\n'
            )
            with self.assertRaises(MinError):
                run(fail_source, filename=main_path)


if __name__ == "__main__":
    unittest.main()
