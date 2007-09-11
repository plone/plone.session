from Testing import ZopeTestCase
from Products.Five import zcml

import plone.session
from plone.session.plugins.session import SessionPlugin
from plone.session.tests.layer import PloneSession

from OFS.Folder import Folder


class FakePAS(Folder):
    plugins = None

    def updateCredentials(self, request, response, userid, password):
        self.credentials=(userid, password)


    def _verifyUser(self, plugin, user_id=None, login=None):
        assert user_id is None
        if login=='our_user':
            return dict(id=user_id, login=user_id, pluginid="session")
        return None


class PloneSessionTestCase(ZopeTestCase.ZopeTestCase):

    layer = PloneSession

    def afterSetUp(self):
        zcml.load_config('configure.zcml', plone.session)
        self.folder._setObject("pas", FakePAS("pas"))
        self.folder.pas._setObject("session", SessionPlugin("session"))


class FunctionalPloneSessionTestCase(ZopeTestCase.Functional, PloneSessionTestCase):
    pass

