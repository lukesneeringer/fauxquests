import os
import sys

# Ensure that the torch directory is part of our Python path.
APP_ROOT = os.path.realpath(os.path.dirname(__file__) + '/../')
sys.path.append(APP_ROOT)

from fauxquests.compat import unittest

# Find tests.
def load_tests(loader, standard_tests, throwaway):
    return loader.discover('tests')

# Run the tests.
if __name__ == '__main__':
    unittest.main()
