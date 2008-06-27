from zope.annotation.interfaces import IAnnotations
from plone.session.sources.base import BaseSource
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from socket import inet_aton
from struct import pack
import random, md5, time


def GenerateSecret(length=64):
    secret=""
    for i in range(length):
        secret+=chr(random.getrandbits(8))

    return secret


class TktAuthSession(BaseSource):
    """A mod_auth_tkt session source implementation.
    
    See: http://www.openfusion.com.au/labs/mod_auth_tkt/
    """

    timeout = 12*60*60 # default is 2h in mod_auth_tkt
    
    # We don't implement these yet
    ignoreIP = True # you always want this on the public internet
    timeoutRefresh = 0 # default is 0.5 in mod_auth_tkt

    manage_options = (
                { 'label':      'TktAuth tools',
                  'action':     '@@tktauth_view/manage_secret' },
                { 'label':      'TktAuth tools',
                  'action':     'manage_secret' },
              )

    def __init__(self, context):
        self.context=context
        anno=IAnnotations(self.context)
        if not anno.has_key("plone.session.plugins.tktauth.secret"):
            self.createNewSecret()

    def createNewSecret(self):
        anno=IAnnotations(self.context)
        anno["plone.session.plugins.tktauth.secret"]=GenerateSecret()

    def setSecret(self, secret):
        anno=IAnnotations(self.context)
        anno["plone.session.plugins.tktauth.secret"]=secret

    def getSecret(self):
        anno=IAnnotations(self.context)
        return anno["plone.session.plugins.tktauth.secret"]

    def createIdentifier(self,
                         userid,
                         tokens=None,
                         user_data=None,
                         timestamp=None,
                         ip=None,
                         secret=None):
        if secret is None:
            secret = self.getSecret()
        if ip is None:
            ip =  "0.0.0.0" # XXX implied by ignoreIp
        if timestamp is None:
            timestamp = int(time.time())
        if tokens is None:
            tokens = ()  # group ids could be useful here
        if user_data is None:
            user_data = ''

        token_list = ','.join(tokens)
        digest0 = md5.new( inet_aton(ip) + pack("!I", timestamp) +
                    '\0'.join((userid, token_list, user_data)) ).hexdigest()
        digest = md5.new(digest0 + secret).hexdigest()
        
        identifier = "%s%08x%s!" % (digest, timestamp, userid) 
        if tokens:
            identifier += tokens_list + '!'
        identifier += user_data
        
        return identifier

    def splitIdentifier(self, identifier):
        digest = identifier[:32]
        timestamp = int(identifier[32:40], 16)
        parts = identifier[40:].split("!")
        
        if len(parts) == 2:
            userid, user_data = parts
            tokens = ()
        elif len(parts) == 3:
            userid, token_list, user_data = parts
            tokens = ','.split(token_list)
        else:
            raise ValueError

        return (digest, userid, tokens, user_data, timestamp)


    def verifyIdentifier(self, identifier):
        (digest, userid, tokens, user_data, timestamp)=self.splitIdentifier(identifier)
        new_identifier = self.createIdentifier(userid, tokens, user_data, timestamp)
        if new_identifier[:32] == digest:
            if timestamp + self.timeout > time.time():
                return True
# XXX Should refresh the ticket if after timeout refresh.

        return False


    def extractUserId(self, identifier):
        (digest, userid, tokens, user_data, timestamp)=self.splitIdentifier(identifier)
        return userid


    manage_secret = ViewPageTemplateFile('tktauth.pt')


