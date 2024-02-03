#!/usr/bin/env python

"""Check supported image formats."""

import unittest

# build-in modules
import warnings

# own modules
import io_

# third-party modules

# path changes


# information
__author__ = "Oskar Maier"
__version__ = "r0.1.1, 2013-09-16"
__email__ = "oskar.maier@googlemail.com"
__status__ = "Release"
__description__ = "Check supported image formats."


# code
def main():
    # load io tests
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        suite_io = unittest.TestSuite()
        suite_io.addTests(
            unittest.TestLoader().loadTestsFromTestCase(io_.TestIOFacilities)
        )
        suite_io.addTests(
            unittest.TestLoader().loadTestsFromTestCase(io_.TestMetadataConsistency)
        )

        # execute tests
        unittest.TextTestRunner(verbosity=2).run(suite_io)


if __name__ == "__main__":
    main()
