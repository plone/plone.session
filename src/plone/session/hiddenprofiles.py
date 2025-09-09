from plone.base.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles:
    def getNonInstallableProfiles(self):
        """Prevents uninstall profile from showing up in the profile list
        when creating a Plone site.

        """
        return [
            "plone.session:uninstall",
        ]
