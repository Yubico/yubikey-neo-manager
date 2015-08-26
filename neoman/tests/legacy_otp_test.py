from unittest import TestCase
from neoman.legacy_otp import split_password


class TestStaticPassword(TestCase):

    def test_splitting_short_password(self):
        self.assertTupleEqual(('abc', '', ''), split_password('abc'))

    def test_splitting_long_password(self):
        self.assertTupleEqual(('abcdefghijklmnop', 'qrstuv', 'xyz'),
                              split_password('abcdefghijklmnopqrstuvxyz'))

    def test_splitting_too_long_password(self):
        with self.assertRaises(Exception):
            split_password('this text is longer than thirty-eight characters')