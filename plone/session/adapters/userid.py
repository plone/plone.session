from zope.interface import implements
from plone.session.interfaces import ISessionSource

class UserIdSession(object):
    implements(ISessionSource)

    def __init__(self, context):
        self.context=context


    def createIdentifier(self, userid):
        return userid


    def verifyIdentitier(self, identifier):
        return True


    def extractUserid(self, identifier):
        return identifier


    def invalidateSession(self, principal):
        pass

