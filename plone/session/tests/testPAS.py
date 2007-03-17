from plone.session.interfaces import ISessionPlugin, ISessionSource
import plone.session
from sessioncase import PloneSessionTestCase


class TestOpenIdExtraction(PloneSessionTestCase):

    def testInterfaces(self):
        session = self.app.folder.session
        self.assertEqual(ISessionPlugin.providedBy(session), True)
        source = session.source
        self.assertEqual(ISessionSource.providedBy(source), True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdExtraction))
    return suite
