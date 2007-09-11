from zope.interface import implements
from plone.session.interfaces import ISessionSource
from plone.session.sources.base import BaseSource

class UserIdSession(BaseSource):
    implements(ISessionSource)

    def createIdentifier(self, userid):
        return userid


    def verifyIdentifier(self, identifier):
        return isinstance(identifier, str)


    def extractUserId(self, identifier):
        return identifier
