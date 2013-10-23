from __future__ import unicode_literals
from fauxquests.response import Resp
from fauxquests.compat import mock, unittest


class RespTests(unittest.TestCase):
    """A group of tests to try some of the straggling aspects of
    the Resp class, primarily for the coverage report.
    """
    def test_info(self):
        resp = Resp('foo'.encode('utf8'))
        self.assertEqual(resp.info(), resp)

    def test_release_conn(self):
        resp = Resp('foo'.encode('utf8'))
        with mock.patch.object(resp, 'close') as m:
            resp.release_conn()
            m.assert_called_once()

    def test_get_all(self):
        resp = Resp('foo'.encode('utf8'), headers={ 'bar': 'baz' })
        self.assertEqual(resp.get_all('bar', None), ['baz'])
        self.assertEqual(resp.get_all('spam', None), None)
