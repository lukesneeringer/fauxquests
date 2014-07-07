from __future__ import absolute_import, unicode_literals
from fauxquests.compat import mock, unittest
import fauxquests
import requests


class IntegrationTests(unittest.TestCase):
    """A set of tests to ensure that the overarching kaboodle works in
    the way we expect.
    """
    def setUp(self):
        self.fs = fauxquests.FauxServer()

    def test_fauxquests(self):
        """Ensure that a standard request registration and mock out
        works as expected.
        """
        with self.fs as fs:
            fs.register('http://www.google.com/', 'blahblah')
            result = requests.get('http://www.google.com/')
            self.assertEqual(result.content.decode('utf8'), 'blahblah')

    def test_unregistered(self):
        """Ensure that an unregistered URL fails in the way we expect,
        with a loud error.
        """
        with self.fs as fs:
            with self.assertRaises(fauxquests.exceptions.UnregisteredURL):
                result = requests.get('http://www.google.com/')

    def test_method_match(self):
        """Ensure that a method-specific registration is honored,
        and only sends back results for that method.
        """
        with self.fs as fs:
            fs.register('http://www.google.com/', 'blah', method='POST')

            # Make sure POST works.
            result = requests.post('http://www.google.com/')
            self.assertEqual(result.content.decode('utf8'), 'blah')

            # Make sure GET doesn't work.
            with self.assertRaises(fauxquests.exceptions.UnregisteredURL):
                result = requests.get('http://www.google.com/')
