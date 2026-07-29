"""Unit tests for Min language Coroutines/Generators and Object Introspection."""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from min import run


class TestCoroutinesAndIntrospection(unittest.TestCase):

    def test_generator_coroutines(self):
        source = (
            '@range_gen(start end) [\n'
            '  !while (< start end) [\n'
            '    !yield start\n'
            '    :start (+ start 1)\n'
            '  ]\n'
            ']\n'
            ':gen @range_gen(10: 13)\n'
            ':a gen.next()\n'
            ':b gen.next()\n'
            ':c gen.next()\n'
            '+ a + b c\n'
        )
        self.assertEqual(run(source), 33)

    def test_object_introspection(self):
        source = (
            '!class Animal [\n'
            '  :species "Canine"\n'
            '  @speak() ["Woof"]\n'
            ']\n'
            ':a !new Animal()\n'
            ':m @methods(a)\n'
            ':f @fields(a)\n'
            ':is_anim @is_a(a: "Animal")\n'
            ':res [m f is_anim]\n'
            'res\n'
        )
        result = run(source)
        self.assertIn("speak", result[0])
        self.assertEqual(result[1], {"species": "Canine"})
        self.assertTrue(result[2])


if __name__ == "__main__":
    unittest.main()
