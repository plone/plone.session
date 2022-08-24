# -*- coding: utf-8 -*-
from AccessControl.Permissions import access_contents_information
from AccessControl.Permissions import view
from OFS.Folder import Folder
from OFS.Folder import manage_addFolder
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from plone.session.plugins.session import SessionPlugin

import doctest


folder_name = "test_folder_1_"
user_name = "test_user_1_"
user_password = "secret"
user_role = "test_role_1_"
standard_permissions = [access_contents_information, view]


class FakePAS(Folder):
    plugins = None

    def updateCredentials(self, request, response, userid, password):
        self.credentials = (userid, password)

    def _verifyUser(self, plugin, user_id=None, login=None):
        assert user_id is None
        if login == "our_user":
            return dict(id=login, login=login, pluginid="session")
        return None


class PloneSessionLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.session
        import plone.session.tests

        self.loadZCML(package=plone.session, name="meta.zcml")
        self.loadZCML(package=plone.session)
        self.loadZCML(package=plone.session.tests)

        self._create_folder(app)
        self._create_structure()

    def _create_folder(self, app):
        manage_addFolder(app, folder_name)
        self.folder = getattr(app, folder_name)
        self.folder._addRole(user_role)
        self.folder.manage_role(user_role, standard_permissions)

    def _create_structure(self):
        self.folder._setObject("pas", FakePAS("pas"))
        self.folder.pas._setObject("session", SessionPlugin("session"))


PLONE_SESSION_FIXTURE = PloneSessionLayer()

PLONE_SESSION_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_SESSION_FIXTURE,), name="PloneSessionLayer:Integration"
)
PLONE_SEESION_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_SESSION_FIXTURE,),
    name="PloneSessionLayer:Functional",
)

optionflags = (
    doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
)
