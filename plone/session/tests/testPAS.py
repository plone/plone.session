import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from plone.session.interfaces import ISessionPlugin, ISessionSource
import plone.session
from sessioncase import PloneSessionTestCase


class TestOpenIdExtraction(PloneSessionTestCase):
    def testInterfaces(self):
        self.assertEqual(ISessionPlugin.providedBy(self.app.session), True)
        source=self.app.session.getSource()
        self.assertEqual(ISessionSource.providedBy(source), True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdExtraction))
    return suite


if __name__ == '__main__':
    framework()


