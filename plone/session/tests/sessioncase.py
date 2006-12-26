from Testing import ZopeTestCase
from Testing.ZopeTestCase.placeless import setUp, tearDown
from Testing.ZopeTestCase.placeless import zcml
import Products.Five.tests
import plone.session
from plone.session.plugins.session import SessionPlugin

class PloneSessionTestCase(ZopeTestCase.ZopeTestCase):

    def afterSetUp(self):
        setUp()
        zcml.load_config('meta.zcml', Products.Five)
        zcml.load_config('permissions.zcml', Products.Five)
        zcml.load_config('directives.zcml', Products.Five.tests)
        zcml.load_config('configure.zcml', plone.session)
        self.app._setObject("session", SessionPlugin("session"))

    def beforeTearDown(self):
        tearDown()
