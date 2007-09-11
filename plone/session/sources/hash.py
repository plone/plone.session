from zope.annotation.interfaces import IAnnotations
from plone.session.sources.base import BaseSource
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
import random, hmac, sha

def GenerateSecret(length=64):
    secret=""
    for i in range(length):
        secret+=chr(random.getrandbits(8))

    return secret


class HashSession(BaseSource):
    """A Hash session source implementation.
    """

    # Number of secrets to keep. The first secret is the current signing key
    secret_count = 5

    manage_options = (
                { 'label':      'Hash tools',
                  'action':     '@@hash_view/manage_secret' },
                { 'label':      'Hash tools',
                  'action':     'manage_secret' },
              )

    def __init__(self, context):
        self.context=context
        anno=IAnnotations(self.context)
        if not anno.has_key("plone.session.plugins.hash.secrets"):
            self.clearSecrets()


    def clearSecrets(self):
        anno=IAnnotations(self.context)
        anno["plone.session.plugins.hash.secrets"]=[]
        self.createNewSecret()


    def createNewSecret(self):
        anno=IAnnotations(self.context)
        anno["plone.session.plugins.hash.secrets"]=[GenerateSecret()] + \
                anno["plone.session.plugins.hash.secrets"][:self.secret_count-1]


    def getSecrets(self):
        anno=IAnnotations(self.context)
        return anno["plone.session.plugins.hash.secrets"]


    def getSigningSecret(self):
        return self.getSecrets()[0]


    def signUserid(self, userid, secret=None):
        if secret is None:
            secret = self.getSigningSecret()

        return hmac.new(secret, userid, sha).digest()


    def createIdentifier(self, userid):
        signature=self.signUserid(userid)

        return "%s %s" % (signature, userid)


    def splitIdentifier(self, identifier):
        index=identifier.rfind(" ")
        if index==-1:
            raise ValueError

        return (identifier[:index], identifier[index+1:])


    def verifyIdentifier(self, identifier):
        for secret in self.getSecrets():
            try:
                (signature, userid)=self.splitIdentifier(identifier)
                if  signature==self.signUserid(userid, secret):
# XXX if the secret is not the current signing secret we should reset the cookie
                    return True
            except (AttributeError, ValueError):
                continue

        return False


    def extractUserId(self, identifier):
        (signature, userid)=self.splitIdentifier(identifier)
        return userid


    manage_secret = ViewPageTemplateFile('hash.pt')


