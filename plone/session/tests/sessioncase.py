from Testing import ZopeTestCase
from Products.Five import zcml

import plone.session
from plone.session.plugins.session import SessionPlugin
from plone.session.tests.layer import PloneSession

from OFS.Folder import Folder


class PloneSessionTestCase(ZopeTestCase.ZopeTestCase):

    layer = PloneSession

    def afterSetUp(self):
        zcml.load_config('configure.zcml', plone.session)
        self.folder._setObject("session", SessionPlugin("session"))


class FunctionalPloneSessionTestCase(ZopeTestCase.Functional, PloneSessionTestCase):
    pass

