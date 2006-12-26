from Testing import ZopeTestCase
from Testing.ZopeTestCase.placeless import setUp, tearDown
from Testing.ZopeTestCase.placeless import zcml
import Products.Five.tests
import plone.session
from plone.session.plugins.session import SessionPlugin

from OFS.Folder import Folder


class PloneSessionTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        setUp()
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('directives.zcml', Products.Five.tests)
        zcml.load_config('configure.zcml', plone.session)
        if not self.app.hasObject("folder"):
            self.app._setObject("folder", Folder("folder"))
        if not self.app.folder.hasObject("session"):
            self.app.folder._setObject("session", SessionPlugin("session"))

    def beforeTearDown(self):
        tearDown()
