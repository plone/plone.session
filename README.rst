Overview
========

*plone.session* implements secure session management for Zope sites.

In its default configuration *plone.session* uses an HMAC_ SHA-256_ secure cryptographic hash to authenticate sessions.
The hash is generated using the userid and a secret stored in the PAS plugin.
Otherwise, the cookie format is identical to that of Apache's mod_auth_tkt_.
For single sign on with the original mod_auth_tkt or another compatible implementation, set the ``mod_auth_tkt`` property to true.
This invokes an MD5_ based double hashing scheme.
You will need to use the same secret across all servers.

This has several advantages over other session management systems:

* passwords are not sent to the server in a cookie on every request, as is done by the *Cookie Auth Helper*
* it does not require any ZODB write for sessions, as is needed by the *Session Crumbler*.
  This allows it to scale very well.
* it allows you to invalidate all existing authentication cookies for users by updating the secret.
* The cookie is only valid for the period specified by the ``timeout`` property.

There are some downsides to this approach:

* if a user's password is changed or disabled session identifiers will continue to work, making it hard to lock out individual users.
* a user must have cookies enabled.

A session cookie is used to track sessions;
that means that as long as a user keeps his browser open (and does not explicitly log out) the session remains open until the timeout limit is reached.
This can be changed by setting the ``timeout`` property of the plugin to the number of seconds the cookie should remain valid *after the moment of login*.

*plone.session* does **not** excuse you from setting up TLS (aka HTTPS) for your site.

``tktauth.py`` implements the core mod_auth_tkt functionality.
It is self-contained and may be of useful to other frameworks.

.. _mod_auth_tkt: http://www.openfusion.com.au/labs/mod_auth_tkt/
.. _MD5: http://en.wikipedia.org/wiki/MD5
.. _HMAC: http://en.wikipedia.org/wiki/HMAC
.. _SHA-256: http://en.wikipedia.org/wiki/SHA-256


Using plone.session
===================

*plone.session* only takes care of handling sessions for already authenticated users.
This means it can not be used stand-alone: you need to have another PAS plugin, such as the standard *Cookie Auth Helper* to take care of authentication.

After a user has been authenticated *plone.session* can take over via the PAS *credentials update* mechanism.


Configuration options
=====================

To enable logins between sites or other mod_auth_tkt systems, set the shared secret through the Zope Management Interface.
You can manage the ``plone.keyring`` secrets through the same page.

The following properties may be set through the ``Properties`` tab:

Cookie validity timeout (in seconds)
    After this, the session is invalid and the user must login again.
    Set to 0 for the cookie to remain valid indefinitely.
    Note that when the user folder has caching enabled, cookie validity may not be checked on every request.

Refresh interval (in seconds, -1 to disable refresh)
    This controls the refresh CSS max-age (see below.)

Use mod_auth_tkt compatible hashing algorithm
    Compatibility with other implementations, but at the cost of using a weaker hashing algorithm.

Cookie name
    Which cookie to use. This must also be set on the ``credentials_cookie_auth`` plugin.

Cookie lifetime (in days)
    This makes the cookie persistent across opening and closing the browser.

Cookie domain (blank for default)
    A cookie may be shared across www1.example.com and www2.example.com by setting the cookie domain to ``.example.com``.

Cookie path
    What path the cookie is set valid (defaults to ``/``).


Ticket refresh
==============

To enable short validity timeouts you must ensure that the cookie is regularly updated.
One option is to put mod_auth_tkt in front of your site and set a ``TktAuthTimeoutRefresh``.
As of *plone.session 3.1*, an independent javascript solution is also supplied, installable as an optional add-on in Plone.

Theory of operation
-------------------

The optional add-on installs a css resource which updates the cookie when loaded.
This allows the cookie to be updated every time a page is loaded.
While this CSS cannot cached by proxy servers, it may be cached for a time on the client.
By controlling the ``max-age`` of the CSS resource, it is possible to control how often the browser actually fetches the CSS and hence how often the cookie is updated.

With short timeouts (15 or 30 minutes say), a user may not have loaded a new page before their cookie becomes invalid.
A javascript is included which polls the cookie refresh CSS periodically while the user is active on the page (key presses or mouse moves.)
If the refresh CSS max-age has passed, then the browser will refetch the CSS and the cookie will be updated.
The poll interval may be configured on the refresh CSS query string ``minutes`` parameter, with the default being 5 minutes.


Ticket removal
==============

When login sessions are shared across domains, it can be helpful to log users out of all domains when they log out of a Plone site.
Load the pseudo CSS ``http://example.com/portal_path/acl_users/session/remove?type=css`` on the ``/logged_out`` page for ticket removal.


Single Sign On with IIS
=======================

For intranet setups with users on a Windows domain, it's possible to configure IIS with `Integrated Windows Authentication` to act as an external login provider, even for sites running on Linux/Unix servers.


Requirements
------------

- You need a Microsoft Windows Server running IIS.
  Preferably Windows Server 2003 or a later version.

- The server must be a member of the Windows domain you want to authenticate users for.
  It does not need to be an Active Directory server itself.

- You site should use pas.plugins.ldap_ to use the same Active Directory as a user source.

.. _pas.plugins.ldap: http://pypi.python.org/pypi/pas.plugins.ldap


Python
------

- The Windows server needs to have `Python 2.7 <http://www.python.org/download/>`_ and the `Python Win 32 extensions build >=216 <http://sourceforge.net/projects/pywin32/files/>`_ installed.

- Place a copy of ``tktauth.py`` (from plone/session of this package) into::

    C:\Python26\Lib\site-packages\

- Follow these `instructions on how to configure Python for IIS <http://support.microsoft.com/kb/276494>`_.
  In bullet point 2.d. use::

    Executable: "C:\Python27\python.exe -u %s %s"

  instead.
  This will ensure files are opened in universal newline mode.
  You can choose to only configure these settings for the specific web site and not the entire IIS.
  Adjust settings accordingly and create the web site first as detailed in the next chapter.


IIS
---

- Find and open the IIS management console.

- Create a new `Web Site`, by going into the ``Web Sites`` folder and using the right-click menu.
  You should get a wizard asking you for various questions::

    Description: SSO login service

    TCP port: 80

    Path: c:\Inetpub\sso

    Allow anonymous access to this Web site: <not checked>

    Permissions: Read, Run scripts, Execute

- If you are running IIS 6, you need to go to the ``Web Service Extensions`` folder and change ``Active Server Pages`` to be ``Allowed``.
  Otherwise you will get rather unhelpful ``404 Not Found`` errors for the asp scripts.


IIS script
----------

- Copy the ``login.asp`` and ``test.asp`` scripts (from the iis-login folder of this package) into root path of the web site (for example C:\Inetpub\sso).

- You need to modify the ``SECRET`` constant found in the ``login.asp`` to the same shared secret set on *plone.session's* ``Manage secrets`` tab.

- Modify the ``ALLOWED_SITES`` constant in ``login.asp`` to include the URLs of your Plone sites.

- Modify the ``DEFAULT_NEXT`` constant in ``login.asp`` to refer the the URL of ``logged_in`` on one of your Plone sites.

- Access ``http://LOGONSERVER/test.asp`` to confirm access permissions are correctly configured.


Configuring browsers to allow automatic logon
---------------------------------------------

Browsers must be configured to *trust* the logon server for user authentication data to be sent automatically.

By default, Internet Explorer sends logon information to servers within the *Intranet Zone*, so long as the site is accessed using it's intranet name (``http://LOGONSERVER/login.asp``).
If the site is accessed using a fully qualified domain name or IP address, it must be explicitly added to the list of `trusted sites <http://support.microsoft.com/kb/174360>`_.

Firefox configuration information may be found in this `article <http://support.mozilla.com/en-US/kb/Firefox+asks+for+user+name+and+password+on+internal+sites>`_.


Configuring your Plone site
---------------------------

Ensure that you have setup authentication to Active Directory and that you can login with the your current Windows user name.

Set the following configuration options through the Zope interface:

- In ``/Plone/acl_users/session``. On the ``Manage secrets`` tab set a shared secret.

- In ``/Plone/portal_properties/site_properties`` set ``external_login_url`` to ``http://LOGONSERVER/login.asp``.

- In ``/Plone/portal_properties/site_properties`` set ``external_login_iframe`` to true.

Note for developers testing this under Windows XP
-------------------------------------------------

- IIS may be installed as an additional component using the Windows XP installation CD.

- The IIS management console can be located at::

    Start -> Control Panel -> Administrative Tools -> Internet Information Services

- The pywin32 installer setup IIS sufficiently for me not to need to follow the *instructions on how to configure Python for IIS*.

- I could not find how to setup a separate site, so placed the asp scripts directly in ``C:\Inetpub\wwwroot`` - the *Default Web Site*

- From the IIS management console, select "Default Web Site".
  You should see ``login.asp`` and ``test.asp`` in the right hand pane.
  With each file, right-click Properties.
  On the `File Security` tab click Edit... on ``Anonymous access and authentication control``.
  Uncheck ``Anonymous access`` and check ``Basic authentication`` (to be used as a fallback) and ``Integrated Windows authentication``.

- Access ``http://localhost/test.asp`` to confirm IIS authentication works as expected.

- Set the secret in ``login.asp`` and ``Manage secrets`` of *plone.session*.

- Set SITE_URL in ``login.asp`` to ``http://localhost:8080/Plone`` (or whatever the address of your site is).

- Add a Plone user with the same name as your Windows login name (e.g. *Administrator*), this avoids setting up Active Directory.

- Follow the section above to configure your Plone site, but set ``Login Form``  to ``http://localhost/login.asp``.
