from DateTime import DateTime
from zope.publisher.browser import TestRequest
from plone.session.interfaces import ISessionPlugin, ISessionSource
import plone.session
from plone.session.tests.sessioncase import FunctionalPloneSessionTestCase


class MockResponse:
    def setCookie(self, name, value, path, expires=None):
        self.cookie=value
        self.cookie_expires=expires


class TestSessionPlugin(FunctionalPloneSessionTestCase):

    def testInterfaces(self):
        session=self.folder.pas.session
        self.assertEqual(ISessionPlugin.providedBy(session), True)
        source=session.source
        self.assertEqual(ISessionSource.providedBy(source), True)


    def makeRequest(self, cookie):
        session=self.folder.pas.session
        return TestRequest(**{session.cookie_name : cookie})


    def testOneLineCookiesOnly(self):
        def createIdentifier(self, *args):
            return "x"*256

        response=MockResponse()
        session=self.folder.pas.session

        klass=session.source.__class__
        org=klass.createIdentifier
        klass.createIdentifier=createIdentifier

        session.setupSession(None, response)

        klass.createIdentifier=org
        self.assertEqual(len(response.cookie.split()), 1)


    def testCookieLifetimeNoExpiration(self):
        response=MockResponse()
        session=self.folder.pas.session
        session.setupSession(None, response)
        self.assertEqual(response.cookie_expires, None)


    def testCookieLifetimeWithExpirationSet(self):
        response=MockResponse()
        session=self.folder.pas.session
        session.cookie_lifetime = 100
        session.setupSession(None, response)
        self.assertEqual(DateTime(response.cookie_expires).strftime('%Y%m%d'),
                        (DateTime()+100).strftime('%Y%m%d'))
        

    def testExtraction(self):
        session=self.folder.pas.session

        request=self.makeRequest("test string".encode("base64"))
        creds=session.extractCredentials(request)
        self.assertEqual(creds["source"], "plone.session")
        self.assertEqual(creds["cookie"], "test string")

        request=self.makeRequest("test string")
        creds=session.extractCredentials(request)
        self.assertEqual(creds, {})


    def testCredentialsUpdate(self):
        session=self.folder.pas.session
        request=self.makeRequest("test string")
        session.updateCredentials(request, request.response, "bla", "password")
        self.assertEqual(request.response.getCookie(session.cookie_name), None)

        session.updateCredentials(request, request.response,
                "our_user", "password")
        self.assertNotEqual(request.response.getCookie(session.cookie_name),
                None)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestSessionPlugin))
    return suite
