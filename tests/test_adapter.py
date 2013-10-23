from __future__ import unicode_literals
from fauxquests.adapter import FauxAdapter
from fauxquests.compat import mock, unittest


class AdapterTests(unittest.TestCase):
    """A group of tests for verifying that the FauxAdapter class works
    as it should.
    """
    def test_clear(self):
        """Establish that the clear method does successfully wipe out
        anything registered on the adapter.
        """
        fa = FauxAdapter()
        fa.register_json('foo', { 'bar': 'baz' })
        self.assertEqual(len(fa._registry), 1)
        fa.clear()
        self.assertEqual(len(fa._registry), 0)

    def test_register(self):
        """Establish that the `register` method actually registers
        a URL and response in the way we expect.
        """
        fa = FauxAdapter(url_pattern='http://www.google.com/%s/')
        fa.register('foo', 'bar')
        self.assertEqual(len(fa._registry), 1)
        bar = fa._registry['http://www.google.com/foo/']
        self.assertEqual(bar.read(1000), 'bar'.encode('utf8'))

    def test_register_json(self):
        """Establish that the `register_json` method properly converts
        its input and registers through the plain method.
        """
        fa = FauxAdapter()
        with mock.patch.object(fa, 'register') as m:
            fa.register_json('foo', { 'bar': 'baz' })
            m.assert_called_once_with('foo', '{"bar": "baz"}',
                headers={ 'Content-Type': 'application/json' },
                status_code=200,
            )

    def test_send(self):
        """Establish that the `send` method properly returns back
        a response object.
        """
        fa = FauxAdapter()
        fa.register_json('foo', { 'bar': 'baz' })
        request = mock.MagicMock()
        request.url = 'foo'
        response = fa.send(request)
        self.assertEqual(response.json(), { 'bar': 'baz' })
        response = fa.send(request, stream=True)
        self.assertEqual(response.json(), { 'bar': 'baz' })
