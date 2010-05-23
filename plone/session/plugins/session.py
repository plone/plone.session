from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.requestmethod import postonly
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins \
        import IExtractionPlugin, IAuthenticationPlugin, \
                ICredentialsResetPlugin, ICredentialsUpdatePlugin
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from plone.keyring.interfaces import IKeyManager
from plone.session import tktauth
from plone.session.interfaces import ISessionPlugin
from zope.component import getUtility, queryUtility

import binascii
import datetime


manage_addSessionPluginForm = PageTemplateFile('session', globals())


def manage_addSessionPlugin(dispatcher, id, title=None, path='/',
                            REQUEST=None):
    """Add a session plugin."""
    sp=SessionPlugin(id, title=title, path=path)
    dispatcher._setObject(id, sp)

    if REQUEST is not None:
        REQUEST.RESPONSE.redirect('%s/manage_workspace?'
                               'manage_tabs_message=Session+plugin+created.' %
                               dispatcher.absolute_url())


def cookie_expiration_date(days):
    dt = datetime.datetime.utcnow() + datetime.timedelta(days)
    # format string from http://docs.python.org/library/time.html
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


class SessionPlugin(BasePlugin):
    """Session authentication plugin.
    """

    meta_type = "Plone Session Plugin"
    security = ClassSecurityInfo()

    cookie_name = "__ac"
    cookie_lifetime = 0
    cookie_domain = ''
    mod_auth_tkt = False
    timeout = 12*60*60 # 12h. Default is 2h in mod_auth_tkt
    external_ticket_name = 'ticket'
    secure = False
    _shared_secret = None

    # These mod_auth_tkt options are not yet implemented
    #ignoreIP = True # you always want this on the public internet
    #timeoutRefresh = 0 # default is 0.5 in mod_auth_tkt

    _properties = (
            {
                 "id": "timeout",
                 "label": "Cookie validity timeout (in seconds)",
                 "type": "int",
                 "mode": "w",
             },
            {
                 "id": "mod_auth_tkt",
                 "label": "Use mod_auth_tkt compatabile hashing algorithm",
                 "type": "boolean",
                 "mode": "w",
             },
            {
                "id": "cookie_name",
                "label": "Cookie name",
                "type": "string",
                "mode": "w",
            },
            {
                "id": "cookie_lifetime",
                "label": "Cookie lifetime (in days)",
                "type": "int",
                "mode": "w",
            },
            {
                 "id": "cookie_domain",
                 "label": "Cookie domain (blank for default)",
                 "type": "string",
                 "mode": "w",
            },
            {
                 "id": "path",
                 "label": "Cookie path",
                 "type": "string",
                 "mode": "w",
            },
            {
                "id": "secure",
                "label": "Only Send Cookie Over HTTPS",
                "type": "boolean",
                "mode": "w",
            },
            )

    manage_options = (
        dict(label='Manage secrets', action='manage_secret'),
        ) + BasePlugin.manage_options

    def __init__(self, id, title=None, path="/"):
        self._setId(id)
        self.title=title
        self.path=path

    def _getSigningSecret(self):
        if self._shared_secret is not None:
            return self._shared_secret
        manager=getUtility(IKeyManager)
        return manager.secret()

    # ISessionPlugin implementation
    def _setupSession(self, userid, response):
        cookie = tktauth.createTicket(
            self._getSigningSecret(), userid, mod_auth_tkt=self.mod_auth_tkt)
        self._setCookie(cookie, response)

    def _setCookie(self, cookie, response):
        cookie=binascii.b2a_base64(cookie).rstrip()
        options = dict(path=self.path, secure=self.secure, http_only=True)
        if self.cookie_domain:
            options['domain'] = self.cookie_domain
        if self.cookie_lifetime:
            options['expires'] = cookie_expiration_date(self.cookie_lifetime)
        response.setCookie(self.cookie_name, cookie, **options)

    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        creds={}

        if not self.cookie_name in request:
            return creds

        try:
            creds["cookie"]=binascii.a2b_base64(request.get(self.cookie_name))
        except binascii.Error:
            # If we have a cookie which is not properly base64 encoded it
            # can not be ours.
            return creds

        creds["source"]="plone.session" # XXX should this be the id?

        return creds

    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.get("source", None)=="plone.session":
            return None

        ticket=credentials["cookie"]
        if self._shared_secret is not None:
            ticket_data = tktauth.validateTicket(self._shared_secret, ticket,
                timeout=self.timeout, mod_auth_tkt=self.mod_auth_tkt)
        else:
            ticket_data = None
            manager = queryUtility(IKeyManager)
            if manager is None:
                return None
            for secret in manager[u"_system"]:
                if secret is None:
                    continue
                ticket_data = tktauth.validateTicket(secret, ticket,
                    timeout=self.timeout, mod_auth_tkt=self.mod_auth_tkt)
                if ticket_data is not None:
                    break
        if ticket_data is None:
            return None

        (digest, userid, tokens, user_data, timestamp) = ticket_data
        pas=self._getPAS()
        info=pas._verifyUser(pas.plugins, user_id=userid)
        if info is None:
            return None

        # XXX Should refresh the ticket if after timeout refresh.
        return (info['id'], info['login'])

    # ICredentialsUpdatePlugin implementation
    def updateCredentials(self, request, response, login, new_password):
        pas=self._getPAS()
        info=pas._verifyUser(pas.plugins, login=login)
        if info is not None:
            # Only setup a session for users in our own user folder.
            self._setupSession(info["id"], response)

    # ICredentialsResetPlugin implementation
    def resetCredentials(self, request, response):
        response=self.REQUEST["RESPONSE"]
        if self.cookie_domain:
            response.expireCookie(
                self.cookie_name, path=self.path, domain=self.cookie_domain)
        else:
            response.expireCookie(self.cookie_name, path=self.path)

    manage_secret = PageTemplateFile("secret.pt", globals())

    security.declareProtected(ManageUsers, 'manage_clearSecrets')
    @postonly
    def manage_clearSecrets(self, REQUEST):
        """Clear all secrets from this source. This invalidates all current
        sessions and requires users to login again.
        """
        manager=getUtility(IKeyManager)
        manager.clear()
        manager.rotate()
        response = REQUEST.RESPONSE
        response.redirect('%s/manage_secret?manage_tabs_message=%s' %
            (self.absolute_url(), 'All+secrets+cleared.'))

    security.declareProtected(ManageUsers, 'manage_createNewSecret')
    @postonly
    def manage_createNewSecret(self, REQUEST):
        """Create a new (signing) secret.
        """
        manager=getUtility(IKeyManager)
        manager.rotate()
        response = REQUEST.RESPONSE
        response.redirect('%s/manage_secret?manage_tabs_message=%s' %
            (self.absolute_url(), 'New+secret+created.'))

    security.declareProtected(ManageUsers, 'haveSharedSecret')
    def haveSharedSecret(self):
        return self._shared_secret is not None

    security.declareProtected(ManageUsers, 'manage_removeSharedSecret')
    @postonly
    def manage_removeSharedSecret(self, REQUEST):
        """Clear the shared secret. This invalidates all current sessions and
        requires users to login again.
        """
        self._shared_secret = None
        response = REQUEST.RESPONSE
        response.redirect('%s/manage_secret?manage_tabs_message=%s' %
            (self.absolute_url(), 'Shared+secret+removed.'))

    security.declareProtected(ManageUsers, 'manage_setSharedSecret')
    @postonly
    def manage_setSharedSecret(self, REQUEST):
        """Set the shared secret.
        """
        secret = REQUEST.get('shared_secret')
        response = REQUEST.RESPONSE
        if not secret:
            response.redirect('%s/manage_secret?manage_tabs_message=%s' %
                (self.absolute_url(), 'Shared+secret+must+not+be+blank.'))
            return
        self._shared_secret = secret
        response.redirect('%s/manage_secret?manage_tabs_message=%s' %
            (self.absolute_url(), 'New+shared+secret+set.'))

    security.declarePublic('external_login')
    def external_login(self, REQUEST):
        """Set the cookie from a form variable and redirect
        """
        request = REQUEST
        response = REQUEST.RESPONSE
        if self._shared_secret is None:
            raise ValueError("No shared secret set")
        try:
            ticket = binascii.a2b_base64(
                request.form.get(self.external_ticket_name, None))
        except (binascii.Error, TypeError):
            raise ValueError("Badly formed ticket")
        ticket_data = tktauth.validateTicket(self._shared_secret, ticket,
            timeout=self.timeout, mod_auth_tkt=self.mod_auth_tkt)
        if ticket_data is None:
            raise ValueError("Invalid ticket")
        (digest, userid, tokens, user_data, timestamp) = ticket_data
        pas = self._getPAS()
        info = pas._verifyUser(pas.plugins, user_id=userid)
        if info is None:
            return ValueError("Unknown user '%s'" % userid)
        self._setCookie(ticket, response)
        came_from = request.form.get('came_from', None)
        if came_from is None:
            # XXX we want the portal url but cannot depend on CMF
            came_from = pas.aq_parent.absolute_url()
        response.redirect(came_from)
        return None

classImplements(SessionPlugin, ISessionPlugin,
                IExtractionPlugin, IAuthenticationPlugin,
                ICredentialsResetPlugin, ICredentialsUpdatePlugin)
