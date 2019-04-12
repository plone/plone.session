# -*- coding: utf-8 -*-
from zope.interface import implementer
from Products.CMFPlone.interfaces import INonInstallable


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.

        """
        return [
            u'plone.session:uninstall',
            u'plone.session:remove-legacy-resources',
        ]
