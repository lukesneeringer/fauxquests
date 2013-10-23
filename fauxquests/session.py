from __future__ import unicode_literals
from collections import namedtuple
from fauxquests.adapter import FauxAdapter
from fauxquests.compat import mock
from requests.compat import OrderedDict
from requests.sessions import Session
from sdict import AlphaSortedDict


class FauxServer(Session):
    """A class that can register certain endpoints to have false
    responses returned.
    """
    def __init__(self, adapter_class=FauxAdapter, url_pattern='%s'):
        """Create a new Fauxquests instance, which knows how to
        mock out requests.session.Session and insert itself.

        If a `url_pattern` is provided, then all URLs registered
        are interpolated through the `url_pattern`.
        """
        # Initialize this object.
        super(FauxServer, self).__init__()
        self.patcher = mock.patch('requests.sessions.Session',
                                  return_value=self)
        self.adapters = OrderedDict()

        # Write settings to this object.
        self.adapter_class = adapter_class
        self.url_pattern = url_pattern

        # Save a list of registrations to apply to any FauxAdapter
        # that this FauxServer creates.
        self.registrations = {}

    def __enter__(self):
        """Mock out `requests.session.Session`, replacing it with this
        object.
        """
        return self.start()

    def __exit__(self, type, value, traceback):
        return self.stop()

    def register(self, url, response, status_code=200, headers=None, **kwargs):
        """Register a given URL and response with this FauxServer.

        Internally, this object's context manager creates and returns a
        FauxAdapters, so regisrations within a context manager go away
        when the context manager is exited.

        This method, however, is run before the context manager is applied,
        and applies universally to all adapters this object creates.
        """
        self.registrations[url] = Registration('', response, status_code,
                                              headers, kwargs)

    def register_json(self, url, response, status_code=200,
                      headers=None, **kwargs):
        """Register a given URL and response with this FauxServer.

        Internally, this object's context manager creates and returns a
        FauxAdapters, so regisrations within a context manager go away
        when the context manager is exited.

        This method, however, is run before the context manager is applied,
        and applies universally to all adapters this object creates.
        """
        self.registrations[url] = Registration('json', response, status_code,
                                               headers, kwargs)

    def start(self):
        """Institute the patching process, meaining requests sent to
        requests (how meta) are caught and handled by our adapter instead.
        """
        # Mount the Fauxquests adapter, which handles delivery of
        # responses based on the provided URL.
        adapter = self.adapter_class(url_pattern=self.url_pattern)
        self.mount('https://', adapter)
        self.mount('http://', adapter)

        # Iterate over any registrations that are saved as part of this
        # FauxServer object and register them to the Adapter.
        for url, reg in self.registrations.items():
            # Is this a plain registration or a JSON registration?
            method_name = 'register'
            if reg.type:
                method_name += '_' + reg.type

            # Forward the registration to the adapter.
            getattr(adapter, method_name)(url, reg.response, reg.status_code,
                                          reg.headers, **reg.kwargs)

        # Start the patcher.
        self.patcher.start()

        # Return the adapter object, which can accept registred
        # URLs with responses
        return adapter

    def stop(self):
        """Undo the patching process set up in `self.start`, and also
        set this object back to having no adapters.
        """
        self.patcher.stop()
        self.adapters = OrderedDict()


Registration = namedtuple('Registration', ['type', 'response', 'status_code',
                                           'headers', 'kwargs'])
