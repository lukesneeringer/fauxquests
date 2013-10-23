from __future__ import unicode_literals
from fauxquests.compat import unittest
from fauxquests.exceptions import UnregisteredURL
from fauxquests.utils import Registry, URL
import six


class RegistryTests(unittest.TestCase):
    def test_getitem_where_exists(self):
        """Establish that we can successfully retrieve an item where
        the item does exist in the dictionary.
        """
        reg = Registry()
        reg['foo'] = 'bar'
        self.assertEqual(reg['foo'], 'bar')

    def test_getitem_where_superset(self):
        """Establish that we can successfully retrieve an item when
        sent an exact superset of that item.
        """
        reg = Registry()
        reg['foo'] = 'bar'
        self.assertEqual(reg['foo?baz=eggs'], 'bar')

    def test_getitem_with_url_object(self):
        """Establish that we can successfully retrieve an item when
        sending a URL object.
        """
        reg = Registry()
        reg['foo'] = 'bar'
        self.assertEqual(reg[URL('foo?baz=eggs')], 'bar')

    def test_getitem_from_blank_registry(self):
        """Establish that we get the error we expect when trying to
        get a key that is not found because the registry is empty.
        """
        reg = Registry()
        with self.assertRaises(UnregisteredURL):
            reg['foo']

    def test_getitem_not_found(self):
        """Establish that we get the error we expect when trying to
        retrieve a key that is not actually in the registry.
        """
        reg = Registry()
        reg['foo'] = 'bar'
        reg['spam'] = 'eggs'
        with self.assertRaises(UnregisteredURL):
            reg['baz']


class URLTests(unittest.TestCase):
    def test_url_creation(self):
        """Establish that we can instantiate a URL object succesfully,
        and that it looks the way we expect.
        """
        url = URL('http://foo/?bar=baz&bar=eggs&spam=eggs')
        self.assertEqual(url.qs['spam'], 'eggs')
        self.assertEqual(url.qs['bar'], {'baz', 'eggs'})

    def test_equality(self):
        """Establish that a URL object can be compared against another
        URL object with expected results.
        """
        url = URL('http://foo/?bar=baz&bar=eggs&spam=eggs')
        url2 = URL('http://foo/?bar=baz&bar=eggs&spam=eggs')
        self.assertEqual(url, url2)

    def test_inequality(self):
        url = URL('http://foo/?bar=baz&bar=eggs&spam=eggs')
        url2 = URL('http://foo/?eggs=bacon')
        self.assertNotEqual(url, url2)

    def test_uncomparable(self):
        url = URL('http://foo/?bar=baz&bar=eggs&spam=eggs')
        url2 = object()
        with self.assertRaises(TypeError):
            url == url2

    def test_str(self):
        url = URL('http://foo/?bar=eggs&bar=baz&spam=eggs')
        self.assertEqual(
            six.text_type(url),
            'http://foo/?bar=baz&bar=eggs&spam=eggs'
        )

    def test_superset_uncomparable(self):
        url = URL('http://foo/?bar=eggs&bar=baz&spam=eggs')
        url2 = object()
        with self.assertRaises(TypeError):
            url.is_exact_superset_of(url2)

    def test_superset_missing_key(self):
        url = URL('http://foo/')
        self.assertFalse(url.is_exact_superset_of('http://foo/?bar=baz'))

    def test_superset_value_mismatch(self):
        url = URL('http://foo/?bar=baz')
        self.assertFalse(url.is_exact_superset_of('http://foo/?bar=eggs'))

    def test_superset_when_true(self):
        url = URL('http://foo/?bar=baz&spam=eggs')
        self.assertTrue(url.is_exact_superset_of('http://foo/?spam=eggs'))
