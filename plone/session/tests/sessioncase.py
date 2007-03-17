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
    def afterSetUp(self):
        import Products.Five.tests
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('directives.zcml', Products.Five.tests)

        zcml.load_config('configure.zcml', plone.session)

        from plone.session.plugins.session import SessionPlugin
        session=SessionPlugin("session")
        self.folder._setObject("session", session)


