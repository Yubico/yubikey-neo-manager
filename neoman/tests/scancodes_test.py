from unittest import TestCase
from neoman.scancodes import to_scancodes


class TestScancodes(TestCase):

    def test_lowercase(self):
        self.assertEqual('\x04\x05\x06', to_scancodes('abc'))

    def test_uppercase(self):
        self.assertEqual('\x84\x85\x9d', to_scancodes('ABZ'))

    def test_specialchars(self):
        self.assertEqual('\xa6\xa4\xa7', to_scancodes('(&)'))