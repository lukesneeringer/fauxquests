from __future__ import unicode_literals
from copy import copy
from fauxquests.response import Resp
from fauxquests.utils import URL, Registry
from requests.adapters import HTTPAdapter
from requests.compat import quote
from unittest import TestCase
import json
import six


class FauxAdapter(HTTPAdapter):
    """A subclass to HTTPAdapter that delivers pre-registered
    content in response to a request, or else raises an exception.
    """
    def __init__(self, url_pattern='%s'):
        """Initialize a FauxAdapter.

        This method is explicitly defined in order to **drop** support
        for the keyword arguments supported by HTTPAdapter (which no longer
        make sense in FauxAdapter's case).

        It adds support for a `url_pattern` argument, which if provided
        is used to interpolate URLs sent to `register` (but not `send`).
        """
        super(FauxAdapter, self).__init__()
        self._registry = Registry()
        self._url_pattern = url_pattern
        self.requests = []

    def clear(self):
        self._registry.clear()

    def register(self, url, response, status_code=200, method='GET',
                                      headers=None, **kwargs):
        """Add the given URL to the registry, and assign the response
        to it.

        If keyword arguments are provided, convert them into a query
        string for the URL. Query string keys and values must be present
        in order for a URL to match (but callers can send a superset and
        still match).
        """
        # Interpolate the provided URL pattern.
        # (This defaults to '%s', which will effectively be a no-op.)
        url = self._url_pattern % url

        # Create a URL object from the URL and keyword arguments.
        url = URL(url, method=method.upper(), **kwargs)

        # If the response is a string object, convert it to a bytes object.
        if isinstance(response, six.text_type):
            response = response.encode('utf8')

        # Add this response to the registry.
        headers = headers or {}
        self._registry[url] = Resp(response, status_code, headers)

    def register_json(self, url, response, status_code=200,
                            method='GET', headers=None, **kwargs):
        """Dump the response to JSON, add the appropriate headers to match,
        and register the URL as normal.
        """
        # Properly state that JSON will be sent down.
        headers = headers or {}
        headers['Content-Type'] = 'application/json'

        # Dump the response to a JSON string.
        response = json.dumps(response)

        # Perform the registration.
        return self.register(url, response, status_code=status_code,
                             method=method.upper(), headers=headers, **kwargs)

    def send(self, request, stream=False, **kwargs):
        """Return the appropriate pre-registered response when a request
        is made.

        If the URL is not matched, the registry raises UnregisteredURL.
        """
        # Get the pre-registered response from our registry.
        url = URL(request.url, method=request.method)
        response = copy(self._registry[url])

        # Use requests to build the response object.
        r = self.build_response(request, response)

        # If this isn't a streaming request, pre-load the content.
        #
        # This is taken from `requests_testadapter`; I'm blindly assuming
        # he has a good reason.
        if not stream:
            r.content

        # Track information about this call, so that asserts can be made
        # against what was done on this object.
        self.requests.append(request)

        # Return the response object
        return r
