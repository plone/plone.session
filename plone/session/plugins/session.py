# -*- coding: utf-8 -*-
from AccessControl.requestmethod import postonly
from AccessControl.SecurityInfo import ClassSecurityInfo
from AccessControl.SecurityManagement import getSecurityManager
from App.config import getConfiguration
from email.utils import formatdate
from plone.keyring.interfaces import IKeyManager
from plone.keyring.keyring import Keyring
from plone.session import tktauth
from plone.session.interfaces import ISessionPlugin
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PluggableAuthService.interfaces.plugins import IAuthenticationPlugin
from Products.PluggableAuthService.interfaces.plugins import ICredentialsResetPlugin
from Products.PluggableAuthService.interfaces.plugins import ICredentialsUpdatePlugin
from Products.PluggableAuthService.interfaces.plugins import IExtractionPlugin
from Products.PluggableAuthService.permissions import ManageUsers
from Products.PluggableAuthService.plugins.BasePlugin import BasePlugin
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer

import binascii
import time


EMPTY_GIF = (
    "GIF89a\x01\x00\x01\x00\xf0\x01\x00\xff\xff\xff"
    "\x00\x00\x00!\xf9\x04\x01\n\x00\x00\x00"
    ",\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
)

manage_addSessionPluginForm = PageTemplateFile("session", globals())


def manage_addSessionPlugin(dispatcher, id, title=None, path="/", REQUEST=None):
    """Add a session plugin."""
    sp = SessionPlugin(id, title=title, path=path)
    dispatcher._setObject(id, sp)

    if REQUEST is not None:
        REQUEST.response.redirect(
            "{0}/manage_workspace?"
            "manage_tabs_message=Session+plugin+created.".format(
                dispatcher.absolute_url()
            )
        )


def cookie_expiration_date(days):
    expires = time.time() + (days * 24 * 60 * 60)
    return formatdate(expires, usegmt=True)


@implementer(
    ISessionPlugin,
    IExtractionPlugin,
    IAuthenticationPlugin,
    ICredentialsResetPlugin,
    ICredentialsUpdatePlugin,
)
class SessionPlugin(BasePlugin):
    """Session authentication plugin."""

    meta_type = "Plone Session Plugin"
    security = ClassSecurityInfo()

    cookie_name = "__ac"
    cookie_lifetime = 0
    cookie_domain = ""
    mod_auth_tkt = False
    timeout = 2 * 60 * 60  # 2h - same as default in mod_auth_tkt
    refresh_interval = 1 * 60 * 60  # -1 to disable
    external_ticket_name = "ticket"
    secure = False
    _shared_secret = None
    secret_prefix = "_plone.session_"
    per_user_keyring = False

    # These mod_auth_tkt options are not yet implemented (by intent)
    # ignoreIP = True # you always want this on the public internet
    # timeoutRefresh = 0 # default is 0.5 in mod_auth_tkt

    _properties = (
        {
            "id": "timeout",
            "label": "Cookie validity timeout (in seconds)",
            "type": "int",
            "mode": "w",
        },
        {
            "id": "refresh_interval",
            "label": "Refresh interval (in seconds, -1 to disable refresh)",
            "type": "int",
            "mode": "w",
        },
        {
            "id": "mod_auth_tkt",
            "label": "Use mod_auth_tkt compatible hashing algorithm",
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
        {
            "id": "per_user_keyring",
            "label": (
                "Create a keyring for each user. "
                "Enables server-side logout."
                'Toggle this from the "Manage secrets" tab.'
            ),
            "type": "boolean",
            "mode": "r",
        },
    )

    manage_options = (
        dict(label="Manage secrets", action="manage_secret"),
    ) + BasePlugin.manage_options

    def __init__(self, id, title=None, path="/"):
        self._setId(id)
        self.title = title
        self.path = path

    def _getSecretKey(self, userid):
        return "{}{}".format(self.secret_prefix, userid)

    def _getSigningSecret(self, userid):
        if self._shared_secret is not None:
            return self._shared_secret
        manager = getUtility(IKeyManager)
        if self.per_user_keyring:
            # Setup a new keyring for the logged-in user.
            # This will be invalidated on logout.
            secret_key = self._getSecretKey(userid)
            if secret_key not in manager:
                manager[secret_key] = Keyring(1)
                manager[secret_key].fill()
            return manager.secret(ring=secret_key)
        return manager.secret()

    # ISessionPlugin implementation
    def _setupSession(self, userid, response, tokens=(), user_data=""):
        cookie = tktauth.createTicket(
            secret=self._getSigningSecret(userid),
            userid=userid,
            tokens=tokens,
            user_data=user_data,
            mod_auth_tkt=self.mod_auth_tkt,
        )
        self._setCookie(cookie, response)

    def _setCookie(self, cookie, response):
        cookie = binascii.b2a_base64(cookie).rstrip()
        # disable secure cookie in development mode, to ease local testing
        if getConfiguration().debug_mode:
            secure = False
        else:
            secure = self.secure
        options = dict(path=self.path, secure=secure, http_only=True, same_site="Lax")
        if self.cookie_domain:
            options["domain"] = self.cookie_domain
        if self.cookie_lifetime:
            options["expires"] = cookie_expiration_date(self.cookie_lifetime)
        response.setCookie(self.cookie_name, cookie, **options)

    # IExtractionPlugin implementation
    def extractCredentials(self, request):
        creds = {}

        if self.cookie_name not in request:
            return creds

        try:
            creds["cookie"] = binascii.a2b_base64(request.get(self.cookie_name))
        except binascii.Error:
            # If we have a cookie which is not properly base64 encoded it
            # can not be ours.
            return creds

        creds["source"] = "plone.session"  # XXX should this be the id?
        return creds

    # IAuthenticationPlugin implementation
    def authenticateCredentials(self, credentials):
        if not credentials.get("source", None) == "plone.session":
            return None

        ticket = credentials["cookie"]
        ticket_data = self._validateTicket(ticket)
        if ticket_data is None:
            return None
        (digest, userid, tokens, user_data, timestamp) = ticket_data
        pas = self._getPAS()
        info = pas._verifyUser(pas.plugins, user_id=userid)
        if info is None:
            return None

        # XXX Should refresh the ticket if after timeout refresh.
        return (info["id"], info["login"])

    def _validateTicket(self, ticket, now=None):
        _, userid, _, _, _ = tktauth.splitTicket(ticket)

        if now is None:
            now = time.time()

        if self._shared_secret is not None:
            ticket_data = tktauth.validateTicket(
                self._shared_secret,
                ticket,
                timeout=self.timeout,
                now=now,
                mod_auth_tkt=self.mod_auth_tkt,
            )
        else:
            ticket_data = None
            manager = queryUtility(IKeyManager)
            if manager is None:
                return None

            secret_key = self._getSecretKey(userid)
            if secret_key in manager:
                secrets = manager[secret_key]
            else:
                secrets = manager["_system"]

            for secret in secrets:
                if secret is None:
                    continue
                ticket_data = tktauth.validateTicket(
                    secret,
                    ticket,
                    timeout=self.timeout,
                    now=now,
                    mod_auth_tkt=self.mod_auth_tkt,
                )
                if ticket_data is not None:
                    break
        return ticket_data

    # ICredentialsUpdatePlugin implementation
    def updateCredentials(self, request, response, login, new_password):
        pas = self._getPAS()
        info = pas._verifyUser(pas.plugins, login=login)
        if info is None:
            # User is not in our own user folder, so we do not setup a session.
            return
        user_id = info["id"]
        # Only setup a session when the current user is the requested user.
        # Otherwise you are logged in as Manager Jane, reset the password of Joe,
        # and are afterwards logged in as Joe.
        # See https://github.com/plone/Products.PlonePAS/issues/57
        authenticated_user = getSecurityManager().getUser()
        if authenticated_user is not None:
            authenticated_id = authenticated_user.getId()
            # For anonymous, the id is empty
            if authenticated_id and authenticated_id != user_id:
                return
        self._setupSession(user_id, response)

    # ICredentialsResetPlugin implementation
    def resetCredentials(self, request, response):
        if self.per_user_keyring:
            # Sometimes (found during testing) the __ac cookie is not
            # set by this plugin, and fails the base64 decode.
            # Using extractCredentials again as it safely gets the decoded
            # cookie.
            creds = self.extractCredentials(request)
            if "cookie" in creds:
                _, userid, _, _, _ = tktauth.splitTicket(creds["cookie"])
                secret_key = self._getSecretKey(userid)
                manager = getUtility(IKeyManager)
                if manager[secret_key]:
                    manager.clear(ring=secret_key)
                    manager.rotate(ring=secret_key)
        response = self.REQUEST["RESPONSE"]
        if self.cookie_domain:
            response.expireCookie(
                self.cookie_name, path=self.path, domain=self.cookie_domain
            )
        else:
            response.expireCookie(self.cookie_name, path=self.path)

    manage_secret = PageTemplateFile("secret.pt", globals())

    @security.protected(ManageUsers)
    @postonly
    def manage_clearSecrets(self, REQUEST):
        """Clear all secrets from this source. This invalidates all current
        sessions and requires users to login again.
        """
        manager = getUtility(IKeyManager)
        for ring in manager:
            if ring.startswith(self.secret_prefix) or ring == "_system":
                manager.clear(ring=ring)
                manager.rotate(ring=ring)
        response = REQUEST.response
        response.redirect(
            "%s/manage_secret?manage_tabs_message=%s"
            % (self.absolute_url(), "All+secrets+cleared.")
        )

    @security.protected(ManageUsers)
    @postonly
    def manage_createNewSecret(self, REQUEST):
        """Create a new (signing) secret."""
        manager = getUtility(IKeyManager)
        for ring in manager:
            if ring.startswith(self.secret_prefix) or ring == "_system":
                manager.rotate(ring=ring)
        response = REQUEST.response
        response.redirect(
            "%s/manage_secret?manage_tabs_message=%s"
            % (self.absolute_url(), "New+secret+created.")
        )

    @security.protected(ManageUsers)
    @postonly
    def manage_togglePerUserKeyring(self, REQUEST):
        """Toggle per-user keyrings."""
        self.per_user_keyring = not self.per_user_keyring
        response = REQUEST.response
        action = "enabled" if self.per_user_keyring else "disabled"
        response.redirect(
            "%s/manage_secret?manage_tabs_message=%s"
            % (self.absolute_url(), "Per-user+keyrings+%s." % (action,))
        )

    @security.protected(ManageUsers)
    def haveSharedSecret(self):
        return self._shared_secret is not None

    @security.protected(ManageUsers)
    @postonly
    def manage_removeSharedSecret(self, REQUEST):
        """Clear the shared secret. This invalidates all current sessions and
        requires users to login again.
        """
        self._shared_secret = None
        response = REQUEST.response
        response.redirect(
            "%s/manage_secret?manage_tabs_message=%s"
            % (self.absolute_url(), "Shared+secret+removed.")
        )

    @security.protected(ManageUsers)
    @postonly
    def manage_setSharedSecret(self, REQUEST):
        """Set the shared secret."""
        secret = REQUEST.get("shared_secret")
        response = REQUEST.response
        if not secret:
            response.redirect(
                "%s/manage_secret?manage_tabs_message=%s"
                % (self.absolute_url(), "Shared+secret+must+not+be+blank.")
            )
            return
        self._shared_secret = secret
        response.redirect(
            "%s/manage_secret?manage_tabs_message=%s"
            % (self.absolute_url(), "New+shared+secret+set.")
        )

    def _refreshSession(self, request, now=None):
        # Refresh a ticket. Does *not* check the user is in the use folder
        if self.cookie_name not in request:
            return None
        try:
            ticket = binascii.a2b_base64(request.get(self.cookie_name))
        except binascii.Error:
            return None
        if now is None:
            now = time.time()
        ticket_data = self._validateTicket(ticket, now)
        if ticket_data is None:
            return None
        (digest, userid, tokens, user_data, timestamp) = ticket_data
        self._setupSession(userid, request.response, tokens, user_data)
        return True

    def _refresh_content(self, REQUEST):
        setHeader = REQUEST.response.setHeader
        type = REQUEST.get("type")
        if type == "gif":
            setHeader("Content-Type", "image/gif")
            return EMPTY_GIF
        elif type == "css":
            setHeader("Content-Type", "text/css")
            return ""
        elif type == "js":
            setHeader("Content-Type", "text/javascript")
            return ""

    @security.public
    def refresh(self, REQUEST):
        """Refresh the cookie"""
        setHeader = REQUEST.response.setHeader
        # Disable HTTP 1.0 Caching
        setHeader("Expires", formatdate(0, usegmt=True))
        if self.refresh_interval < 0:
            return self._refresh_content(REQUEST)
        now = time.time()
        refreshed = self._refreshSession(REQUEST, now)
        if not refreshed:
            # We have an unauthenticated user
            setHeader(
                "Cache-Control",
                "public, must-revalidate, max-age=%d, s-max-age=86400"
                % self.refresh_interval,
            )
            setHeader("Vary", "Cookie")
        else:
            setHeader(
                "Cache-Control",
                "private, must-revalidate, proxy-revalidate, max-age=%d, "
                "s-max-age=0" % self.refresh_interval,
            )
        return self._refresh_content(REQUEST)

    @security.public
    def remove(self, REQUEST):
        """Remove the cookie"""
        self.resetCredentials(REQUEST, REQUEST.response)
        setHeader = REQUEST.response.setHeader
        # Disable HTTP 1.0 Caching
        setHeader("Expires", formatdate(0, usegmt=True))
        setHeader(
            "Cache-Control", "public, must-revalidate, max-age=0, s-max-age=86400"
        )
        return self._refresh_content(REQUEST)
