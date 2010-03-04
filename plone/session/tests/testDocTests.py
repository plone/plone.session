import unittest
from zope.testing import doctest

from plone.session import tktauth

optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocTestSuite(tktauth,
            optionflags=optionflags))

    return suite
