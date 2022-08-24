# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone.app.testing import logout
from plone.session.interfaces import ISessionPlugin
from plone.session.testing import PLONE_SEESION_FUNCTIONAL_TESTING
from zope.publisher.browser import TestRequest

import base64
import unittest


class MockResponse(object):
    def setCookie(
        self,
        name,
        value,
        path,
        expires=None,
        secure=False,
        http_only=False,
        same_site=None,
    ):
        self.cookie = value
        self.cookie_expires = expires
        self.cookie_http_only = http_only
        self.cookie_same_site = same_site
        self.secure = secure


class TestSessionPlugin(unittest.TestCase):

    layer = PLONE_SEESION_FUNCTIONAL_TESTING
    userid = "jbloggs"

    def setUp(self):
        self.folder = self.layer["app"]["test_folder_1_"]

    def testInterfaces(self):
        session = self.folder.pas.session
        self.assertEqual(ISessionPlugin.providedBy(session), True)

    def makeRequest(self, cookie):
        session = self.folder.pas.session
        return TestRequest(**{session.cookie_name: cookie})

    def testOneLineCookiesOnly(self):
        longid = "x" * 256
        response = MockResponse()
        session = self.folder.pas.session
        session._setupSession(longid, response)
        self.assertEqual(len(response.cookie.split()), 1)

    def testCookieLifetimeNoExpiration(self):
        response = MockResponse()
        session = self.folder.pas.session
        session._setupSession(self.userid, response)
        self.assertEqual(response.cookie_expires, None)

    def testSecureCookies(self):
        response = MockResponse()
        session = self.folder.pas.session

        session._setupSession(self.userid, response)
        self.assertEqual(response.secure, False)

        setattr(session, "secure", True)
        session._setupSession(self.userid, response)
        self.assertEqual(response.secure, True)

    def testCookieHTTPOnly(self):
        response = MockResponse()
        session = self.folder.pas.session
        session._setupSession(self.userid, response)
        self.assertEqual(response.cookie_http_only, True)

    def testCookieSameSite(self):
        response = MockResponse()
        session = self.folder.pas.session
        session._setupSession(self.userid, response)
        self.assertEqual(response.cookie_same_site, "Lax")

    def testCookieLifetimeWithExpirationSet(self):
        response = MockResponse()
        session = self.folder.pas.session
        session.cookie_lifetime = 100
        session._setupSession(self.userid, response)
        self.assertEqual(
            DateTime(response.cookie_expires).strftime("%Y%m%d"),
            (DateTime() + 100).strftime("%Y%m%d"),
        )

    def testExtraction(self):
        session = self.folder.pas.session
        # We will preapre a request that is equal in Py2 and Py3
        request_body = base64.encodebytes(b"test string").decode()
        self.assertEqual(request_body, "dGVzdCBzdHJpbmc=\n")
        request = self.makeRequest(request_body)
        creds = session.extractCredentials(request)
        self.assertEqual(creds["source"], "plone.session")
        self.assertEqual(creds["cookie"], b"test string")

        request = self.makeRequest("test string")
        creds = session.extractCredentials(request)
        self.assertEqual(creds, {})

    def testCredentialsUpdateUnknownUser(self):
        # We are logged in as test user, which we do not want.
        logout()
        session = self.folder.pas.session
        request = self.makeRequest("test string")
        # The fake PAS in the tests only knows about "our_user",
        # so updating an unknown user does nothing.
        session.updateCredentials(request, request.response, "bla", "password")
        self.assertIsNone(request.response.getCookie(session.cookie_name))

    def testCredentialsUpdateAnonymous(self):
        # We are logged in as test user, which we do not want.
        logout()
        session = self.folder.pas.session
        request = self.makeRequest("test string")
        session.updateCredentials(request, request.response, "our_user", "password")
        self.assertIsNotNone(
            request.response.getCookie(session.cookie_name),
        )

    def testCredentialsUpdateOtherUser(self):
        # We are logged in as test user, which we DO want in this test.
        # The session should not be updated then.
        session = self.folder.pas.session
        request = self.makeRequest("test string")
        session.updateCredentials(request, request.response, "our_user", "password")
        self.assertIsNone(request.response.getCookie(session.cookie_name))

    def testRefresh(self):
        logout()
        session = self.folder.pas.session
        request = self.makeRequest("test string")
        session.updateCredentials(request, request.response, "our_user", "password")
        cookie = request.response.getCookie(session.cookie_name)["value"]
        request2 = self.makeRequest(cookie)
        request2.form["type"] = "gif"
        session.refresh(request2)
        self.assertIsNotNone(request2.response.getCookie(session.cookie_name))

    def testUnicodeUserid(self):
        response = MockResponse()
        session = self.folder.pas.session
        # This step would fail.
        session._setupSession(self.userid, response)

    def testSpecialCharUserid(self):
        unicode_userid = "ãbcdéfghijk"
        response = MockResponse()
        session = self.folder.pas.session
        # This step would fail.
        session._setupSession(unicode_userid, response)

    def testCookieInvalidAfterLogout(self):
        response = MockResponse()
        session = self.folder.pas.session
        session.per_user_keyring = True
        session._setupSession(self.userid, response)

        cookie = response.cookie
        request = self.makeRequest(cookie)

        creds = session.extractCredentials(request)
        auth = session._validateTicket(creds["cookie"])
        self.assertIsNotNone(auth)

        logout()
        session.resetCredentials(request, response)

        creds = session.extractCredentials(request)
        auth = session._validateTicket(creds["cookie"])
        self.assertIsNone(auth)

    def testCookieValidAfterLogout(self):
        """Disable per-user keyrings and test that the session
        is still valid after logout (the usual Plone behavior)."""
        response = MockResponse()
        session = self.folder.pas.session
        session.per_user_keyring = False
        session._setupSession(self.userid, response)

        cookie = response.cookie
        request = self.makeRequest(cookie)

        creds = session.extractCredentials(request)
        auth = session._validateTicket(creds["cookie"])
        self.assertIsNotNone(auth)

        logout()
        session.resetCredentials(request, response)

        creds = session.extractCredentials(request)
        auth = session._validateTicket(creds["cookie"])
        self.assertIsNotNone(auth)
