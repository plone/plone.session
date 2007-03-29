from zope.publisher.browser import TestRequest
from plone.session.interfaces import ISessionPlugin, ISessionSource
import plone.session
from sessioncase import PloneSessionTestCase


class TestSessionPlugin(PloneSessionTestCase):

    def testInterfaces(self):
        session = self.app.folder.session
        self.assertEqual(ISessionPlugin.providedBy(session), True)
        source = session.source
        self.assertEqual(ISessionSource.providedBy(source), True)


    def makeRequest(self, cookie):
        session = self.app.folder.session
        return TestRequest(**{session.cookie_name : cookie})


    def testExtraction(self):
        session = self.app.folder.session

        request=self.makeRequest("test string".encode("base64"))
        creds=session.extractCredentials(request)
        self.assertEqual(creds["source"], "plone.session")
        self.assertEqual(creds["cookie"], "test string")
        
        request=self.makeRequest("test string")
        creds=session.extractCredentials(request)
        self.assertEqual(creds, {})


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestSessionPlugin))
    return suite
