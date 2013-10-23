from __future__ import unicode_literals

# Import mock from the unittest module in the stdlib if it's there
# (Python 3.3), otherwise import the pip package, which is required
# in Python 2.
try:
    from unittest import mock
except ImportError:
    import mock

# Import unittest2 if we have it (required on Python 2.6),
# otherwise just use the stdlib unittest.
try:
    from unittest2 import unittest
except ImportError:
    import unittest
