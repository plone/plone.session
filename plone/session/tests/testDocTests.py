import unittest
from zope.testing import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite

from plone.session.tests.sessioncase import FunctionalPloneSessionTestCase

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS


def test_suite():
    tests = [ "adapters.txt",
              "hash.txt",
            ]

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(FunctionalDocFileSuite(test,
                optionflags=optionflags,
                package="plone.session.tests",
                test_class=FunctionalPloneSessionTestCase))

    return suite
