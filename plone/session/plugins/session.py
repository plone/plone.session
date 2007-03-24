from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins \
        import IExtractionPlugin, IAuthenticationPlugin, \
                ICredentialsResetPlugin, ICredentialsUpdatePlugin
from AccessControl.SecurityInfo import ClassSecurityInfo
from plone.session.interfaces import ISessionPlugin, ISessionSource

try:
    from AccessControl.requestmethod import postonly
except ImportError:
    # For Zope <2.8.9, <2.9.7 and <2.10.3
    def postonly(func):
        return func

# Temporary imports
from Products.PluggableAuthService.permissions import ManageUsers


manage_addSessionPlugin = PageTemplateFile('session', globals())
    

def addSessionPlugin(dispatcher, id, title=None, path='/', REQUEST=None):
    """Add a session plugin."""
    sp=SessionPlugin(id, title=title, path=path)
    dispatcher._setObject(id, sp)

    REQUEST.RESPONSE.redirect( '%s/manage_workspace?'
                               'manage_tabs_message=Session+plugin+created.' %
                               dispatcher.absolute_url())



class SessionPlugin(BasePlugin):
    """Session authentication plugin.
    """

    meta_type = "Session plugin"
    security = ClassSecurityInfo()
    cookie_name = "__ac"

    _properties = (
            {
                "id"    : "title",
                "label" : "Title",
                "type"  : "string",
                "mode"  : "w",
            },
            {
                "id"    : "cookie_name",
                "label" : "Cookie Name root",
                "type"  : "string",
                "mode"  : "w",
            },
            )

    def __init__(self, id, title=None, path="/"):
        self._setId(id)
        self.title=title
        self.path=path

    @property
    def source(self):
        return ISessionSource(self)


    def manage_options(self):
        """Splice in mangae options from our source if it has them."""

        more = getattr(self.source, 'manage_options', ()) 
        if more:
            try:
                more = tuple(more)
            except TypeError:
                more = more()

        return more  + BasePlugin.manage_options


    # ISessionPlugin implementation
    def setupSession(self, userid):
        cookie=self.source.createIdentifier(userid)
        cookie=cookie.encode("base64").strip()

        response=self.REQUEST["RESPONSE"]
        response.setCookie(self.cookie_name, cookie, path=self.path)


    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        creds={}

        if not self.cookie_name in request:
            return creds

        creds["cookie"]=request.get(self.cookie_name).decode("base64")
        creds["source"]="plone.session"

        return creds


    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.get("source", None)=="plone.session":
            return None

        source=self.source
        identifier=credentials["cookie"]
        if source.verifyIdentifier(identifier):
            userid=source.extractUserid(identifier)
            return (userid, userid)

        return None


    # ICredentialsUpdatePlugin implementation
    def updateCredentials(self, request, response, login, new_password):
        self.setupSession(login)


    # ICredentialsResetPlugin implementation
    def resetCredentials(self, request, response):
        source=self.source
        source.invalidateSession()

        response=self.REQUEST["RESPONSE"]
        response.expireCookie(self.cookie_name, path=self.path)

# XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX XXX
# This should be in HashSource !

    manage_secret = PageTemplateFile("../sources/hash.pt", globals())

    security.declareProtected(ManageUsers, 'manage_clearSecrets')
    @postonly
    def manage_clearSecrets(self, REQUEST):
        """Clear all secrets from this source.

        This invalidates all current sessions and requires users to login again.
        """
        self.source.clearSecrets()
        REQUEST.RESPONSE.redirect('%s/manage_secret?manage_tabs_message=%s'
                                     % (self.absolute_url(), 'All+secrets+cleared.'))


    security.declareProtected(ManageUsers, 'manage_createNewSecret')
    @postonly
    def manage_createNewSecret(self, REQUEST):
        """Create a new (signing) secret.
        """
        self.source.createNewSecret()
        REQUEST.RESPONSE.redirect('%s/manage_secret?manage_tabs_message=%s'
                                     % (self.absolute_url(), 'New+secret+created.'))

classImplements(SessionPlugin, ISessionPlugin,
                IExtractionPlugin, IAuthenticationPlugin,
                ICredentialsResetPlugin, ICredentialsUpdatePlugin)

