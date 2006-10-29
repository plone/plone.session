from zope.interface import implements
from zope.annotation.interfaces import IAnnotations
from plone.session.interfaces import ISessionSource
import random, hmac, sha

def GenerateSecret(length=16):
    letters ="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    letters+="abcdefghijklmnopqrstuvwxyz"
    letters+="01234567890!@#$%^&*()"

    secret=""
    for i in range(length):
        secret+=random.choice(letters)

    return secret


class HashSession(object):
    implements(ISessionSource)

    def __init__(self, context):
        self.context=context
        anno=IAnnotations(self.context)
	if not anno.has_key("plone.session.plugins.hash.secret"):
            anno["plone.session.plugins.hash.secret"]=GenerateSecret()


    def getSecret(self):
        anno=IAnnotations(self.context)
        return anno["plone.session.plugins.hash.secret"]


    def signUserid(self, userid):
        return hmac.new(self.getSecret(), userid, sha).digest()


    def createIdentifier(self, userid):
        signature=self.signUserid(userid)

        return "%s %s" % (signature, userid)


    def splitIdentifier(self, identifier):
        index=identifier.rfind(" ")
        if index==-1:
            raise ValueError

        return (identifier[:index], identifier[index+1:])


    def verifyIdentifier(self, identifier):
        try:
            (signature, userid)=self.splitIdentifier(identifier)
        except ValueError:
            return False
        else:
            return signature==self.signUserid(userid)


    def extractUserid(self, identifier):
        (signature, userid)=self.splitIdentifier(identifier)
        return userid


    def invalidateSession(self, principal):
        pass

