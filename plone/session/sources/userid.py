from zope.interface import implements
from plone.session.interfaces import ISessionSource

class UserIdSession(object):
    implements(ISessionSource)

    def __init__(self, context):
        self.context=context


    def createIdentifier(self, userid):
        return userid


    def verifyIdentifier(self, identifier):
        return isinstance(identifier, str)


    def extractUserid(self, identifier):
        return identifier


    def invalidateSession(self, principal):
        pass

