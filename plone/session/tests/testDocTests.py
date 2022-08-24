# coding=utf-8
from plone.session import tktauth

import doctest
import unittest


optionflags = doctest.ELLIPSIS


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite(
            tktauth,
            optionflags=optionflags,
        )
    )
    return suite
