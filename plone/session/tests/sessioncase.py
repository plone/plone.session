from Testing import ZopeTestCase
from Testing.ZopeTestCase.placeless import zcml

import plone.session
from plone.session.plugins.session import SessionPlugin
from plone.session.tests.layer import PloneSession

from OFS.Folder import Folder


class PloneSessionTestCase(ZopeTestCase.ZopeTestCase):

    layer = PloneSession

    def afterSetUp(self):
        zcml.load_config('configure.zcml', plone.session)
        if not self.app.hasObject("folder"):
            self.app._setObject("folder", Folder("folder"))
        if not self.app.folder.hasObject("session"):
            self.app.folder._setObject("session", SessionPlugin("session"))

class FunctionalPloneSessionTestCase(ZopeTestCase.Functional, PloneSessionTestCase):
    pass