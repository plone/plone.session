from zope.interface import implements
from plone.session.interfaces import ISessionSource

class BaseSource(object):
    implements(ISessionSource)

    def __init__(self, context):
        self.context=context


    def createIdentifier(self, userid):
        raise NotImplemented


    def verifyIdentifier(self, identifier):
        raise NotImplemented


    def extractLoginName(self, identifier):
        raise NotImplemented


    def invalidateSession(self, principal):
        return False

