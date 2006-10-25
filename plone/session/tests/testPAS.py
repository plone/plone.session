import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase
from Testing.ZopeTestCase.placeless import setUp, tearDown
from Testing.ZopeTestCase.placeless import zcml
from plone.session.plugins.session import SessionPlugin
from plone.session.interfaces import ISessionPlugin, ISessionSource
import Products.Five.tests
import plone.session


class TestOpenIdExtraction(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        setUp()
	zcml.load_config('meta.zcml', Products.Five)
	zcml.load_config('permissions.zcml', Products.Five)
	zcml.load_config('directives.zcml', Products.Five.tests)
	zcml.load_config('configure.zcml', plone.session)
        self.app._setObject("session", SessionPlugin("session"))


    def beforeTeearDown():
        tearDown()


    def testInterfaces(self):
        self.assertEqual(ISessionPlugin.providedBy(self.app.session), True)
        source=self.app.session.getSource()
        self.assertEqual(ISessionSource.providedBy(source), True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite=TestSuite()
    suite.addTest(makeSuite(TestOpenIdExtraction))
    return suite


if __name__ == '__main__':
    framework()


