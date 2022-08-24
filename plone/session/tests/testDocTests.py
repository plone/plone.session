# coding=utf-8
from plone.session import tktauth

import doctest
import re
import unittest


optionflags = doctest.ELLIPSIS


class Py23DocChecker(doctest.OutputChecker):
    def check_output(self, want, got, optionflags):
        want = re.sub("u'(.*?)'", "'\\1'", want)
        return doctest.OutputChecker.check_output(self, want, got, optionflags)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(
        doctest.DocTestSuite(
            tktauth,
            optionflags=optionflags,
            checker=Py23DocChecker(),
        )
    )
    return suite
