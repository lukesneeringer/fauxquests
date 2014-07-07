from fauxquests.exceptions import UnregisteredURL
from fauxquests.messages import NOT_FOUND
from requests.compat import quote
from sdict import AlphaSortedDict
from six.moves.urllib.parse import parse_qs
import six


class Registry(dict):
    """A dict subclass that understands how to handle URLs with
    keyword argument subsets for lookups.
    """
    def __getitem__(self, key):
        """Return a response corresponding to the given key."""

        # Sanity check: This might be easy.
        # If the URL is an exact match via. the regular `dict` lookup,
        # then just return that.
        no = object()
        super_answer = super(Registry, self).get(key, no)
        if super_answer != no:
            return super_answer

        # Convert the key to a URL object if it is not already one.
        if isinstance(key, (six.text_type, six.binary_type)):
            key = URL(key)

        # It's still possible we have a match.
        # Iterate over each key and see if our key is an exact superset of
        # the given key.  If any are, return its value immediately.
        for contender in self.keys():
            if key.is_exact_superset_of(contender):
                return self[contender]

        # Nope, no match. :(
        # Now, we need to raise an exception.
        # First, Get a list of the registered URLs in a nice format.
        registered_urls = '\n    - '.join(
            [six.text_type(i) for i in six.iterkeys(self)],
        )
        if not registered_urls:
            registered_urls = '(None)'

        # Raise an exception.
        # UnregisteredURL inherits from AssertionError rather than KeyError,
        # which should give more attractive failures in tests.
        raise UnregisteredURL(NOT_FOUND.format(
            registered_urls=registered_urls,
            request_url=key,
        ))


class URL(object):
    """A class for holding a URL, with convenience methods
    for poking at its query string separately from the main URI.
    """
    def __init__(self, url, method='GET', **kwargs):
        # Does the URL string have a query string in it?
        # If so, parse that out into keyword arguments.
        if '?' in url:
            qs = parse_qs(url[url.index('?') + 1:])
            for k, v in qs.items():
                if len(v) == 1:
                    v = v[0]
                else:
                    v = set(v)
                kwargs.setdefault(k, v)
            url = url[:url.index('?')]

        # Store the base URL and the keyword arguments.
        self.method = method.upper()
        self.uri = url
        self.qs = AlphaSortedDict(kwargs)

    def __eq__(self, other):
        # If this is a string of some kind, convert it to a URL.
        if isinstance(other, (six.text_type, six.binary_type)):
            other = self.__class__(other)

        # Type check!
        if not hasattr(other, 'qs') or not hasattr(other, 'uri'):
            raise TypeError('Cannot compare URL with %s.' %
                            other.__class__.__name__)

        # Return whether the URI and QS are the same.
        return all([self.uri == other.uri,
                    self.qs == other.qs,
                    self.method == other.method])

    def __hash__(self):
        return hash(str(self))

    def __str__(self):
        """Return the full URL, as a string."""

        # Start with the basic URI.
        answer = '%s %s' % (self.method, self.uri)

        # Append any keyword arguments to the query-string
        if self.qs:
            qs_list = []
            for key, values in self.qs.items():
                # Convert `values` to a list if it's not one already.
                # This way, we seemlessly address situations where the
                # same key is used multiple times.
                if isinstance(values, (list, tuple, set)):
                    values = list(values)
                    values.sort()
                else:
                    values = [values]

                # Iterate over the values and add each to the answer.
                for value in values:
                    qs_list.append('%s=%s' % (key, quote(str(value))))

            # Append the query string to the answer.
            answer += '?' + '&'.join(qs_list)

        # Return the answer.
        return answer

    def is_exact_superset_of(self, other):
        """Return True if this URL is an exact superset of the URL provided
        by `other`.

        Definition of exact superset is:
          - `self.uri` must exactly match `other.uri`.
          - Every key in `other.qs` must be present in `self.qs` with
            the same value.
        """
        # If this is a string of some kind, convert it to a URL.
        if isinstance(other, (six.text_type, six.binary_type)):
            other = self.__class__(other)

        # Type check!
        if not hasattr(other, 'qs') or not hasattr(other, 'uri'):
            raise TypeError('Cannot compare URL with %s.' %
                            other.__class__.__name__)

        # If the URIs do not exactly match, this is not an exact superset.
        if self.uri != other.uri:
            return False

        # If the methods do not match, this is not an exact superset.
        if self.method.upper() != other.method.upper():
            return False

        # Ensure that every key in `other.qs` exists in `self.qs` with
        # the same value; if any do not, immediately return False.
        for key in other.qs.keys():
            # If the key doesn't exist, return False.
            if key not in self.qs:
                return False

            # If the value does not match, return False.
            if self.qs[key] != other.qs[key]:
                return False

        # Okay, we must have an exact superset!
        return True
