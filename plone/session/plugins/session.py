from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from Products.PluggableAuthService.utils import classImplements
from Products.PluggableAuthService.interfaces.plugins \
        import IExtractionPlugin, IAuthenticationPlugin, \
                ICredentialsResetPlugin
from AccessControl.SecurityInfo import ClassSecurityInfo
from plone.session.interfaces import ISessionPlugin, ISessionSource


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


    def getSource(self):
        return ISessionSource(self)


    # ISessionPlugin implementation
    def setupSession(self, userid):
        source=self.getSource()
        cookie=source.createIdentifier(userid)
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

        source=self.getSource()
        identifier=credentials["cookie"]
        if source.verifyIdentifier(identifier):
            userid=source.extractUserid(identifier)
            return (userid, userid)

    	return None


    # ICredentialsResetPlugin implementation
    def resetCredentials(self, request, response):
        source=self.getSource()
        source.invalidateSession()

        response=self.REQUEST["RESPONSE"]
        response.expireCookie(self.cookie_name, path=self.path)


classImplements(SessionPlugin, ISessionPlugin,
                IExtractionPlugin, IAuthenticationPlugin,
                ICredentialsResetPlugin)

