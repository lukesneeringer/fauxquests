from __future__ import unicode_literals
from fauxquests import FauxServer
from fauxquests.adapter import FauxAdapter
from fauxquests.compat import unittest


class FauxServerTests(unittest.TestCase):
    """Establish that the FauxServer objcet works as expected."""

    def test_server_context(self):
        """Establish that the FauxServer context manager works
        as expected.
        """
        faux_server = FauxServer()
        with faux_server as fs:
            self.assertIsInstance(fs, FauxAdapter)

    def test_server_registration(self):
        """Establish that if a URL is registered by a FauxServer, that
        it is automatically registered by the adapters that the FauxServer
        creates.
        """
        # Create a FauxServer and register something.
        faux_server = FauxServer()
        faux_server.register('http://foo/', 'bar baz')

        # Run the context manager, register something else, and verify
        # that we have two registered things.
        with faux_server as fs:
            fs.register('http://bar/', 'spam eggs')
            self.assertEqual(len(fs._registry), 2)

        # Assert that our server still has only one registrant.
        self.assertEqual(len(faux_server.registrations), 1)

    def test_server_json_registration(self):
        """Establish that a URL registered by a FauxServer with a JSON
        response is automatically registered by an adapter.
        """
        # Create a FauxServer and register something.
        faux_server = FauxServer()
        faux_server.register_json('foo', { 'apple': 'pie' })

        # Run the context manager and determine that we have one
        # registered item.
        with faux_server as fs:
            self.assertEqual(len(fs._registry), 1)
