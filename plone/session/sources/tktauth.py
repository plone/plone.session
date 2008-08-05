from zope.annotation.interfaces import IAnnotations
from plone.session.sources.base import BaseSource
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from socket import inet_aton
from struct import pack
import random, md5, time

import mod_auth_tkt

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
                         user_data=None,
                         timestamp=None):
        if timestamp is None:
            timestamp = int(time.time())
        if user_data is None:
            user_data = ''

        return mod_auth_tkt.createTicket(userid, (), user_data, '0.0.0.0', timestamp, self.getSecret())
        
    def verifyIdentifier(self, identifier):
        (digest, userid, tokens, user_data, timestamp) = mod_auth_tkt.splitTicket(identifier)
        new_identifier = self.createIdentifier(userid, user_data, timestamp)
        if new_identifier[:32] == digest:
            if timestamp + self.timeout > time.time():
                return True
        # XXX Should refresh the ticket if after timeout refresh.
        return False


    def extractUserId(self, identifier):
        (digest, userid, tokens, user_data, timestamp) = mod_auth_tkt.splitTicket(identifier)
        return userid


    manage_secret = ViewPageTemplateFile('tktauth.pt')


