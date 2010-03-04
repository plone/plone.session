Overview
--------

plone.session implements secure session management for Zope sites.

In its default configuration plone.session uses an HMAC_ SHA-256_ secure
cryptographic hash to authenticate sessions. The hash is generated using the
users login name and a secret stored in the PAS plugin. Otherwise, the cookie
format is identical to that of Apache's mod_auth_tkt_. For single sign on with
the original mod_auth_tkt or another compatible implementation, set the
``mod_auth_tkt`` property to true. This invokes an MD5_ based double hashing
scheme. You will need to use the same secret across all servers.

This has several advantages over other session management systems:

* passwords are not sent to the server in a cookie on every request, as
  is done by the *Cookie Auth Helper* 
* it does not require any ZODB write for sessions, as is needed by the
  *Session Crumbler*. This allows it to scale very well.
* it allows you to invalidate all existing authentication cookies for
  users by updating the secret.
* The cookie is only valid for the period specified by the `timeout` property.

There are some downsides to this approach:

* if a users password is changed or disabled session identifiers will continue
  to work, making it hard to lock out individual users.
* a user must have cookies enabled.

A session cookie is used to track sessions; that means that as long as
a user keeps his browser open (and does not explicitly log out) the session
remains open until the timout limit is reached. This can be changed by setting
the ``timeout`` property of the plugin to the number of seconds the cookie
should remain valid *after the moment of login*. 

`tktauth.py` implements the core mod_auth_tkt functionality. It is
self-contained and may be of useful to other frameworks.

.. _mod_auth_tkt: http://www.openfusion.com.au/labs/mod_auth_tkt/
.. _MD5: http://en.wikipedia.org/wiki/MD5
.. _HMAC: http://en.wikipedia.org/wiki/HMAC
.. _SHA-256: http://en.wikipedia.org/wiki/SHA-256

Using plone.session
-------------------

plone.session only takes care of handling sessions for already authenticated
users. This means it can not be used stand-alone: you need to have another
PAS plugin, such as the standard *Cookie Auth Helper* to take care of
authentication.

After a user has been authenticated plone.session can take over via the
PAS *credentials update* mechanism. 


Configuration options
---------------------

To enable logins between sites or other mod_auth_tkt systems, set the shared
secret through the Zope Management Interface. You can manage the plone.keyring
secrets through the same page.

The following properties may be set through the Properties tab:

  Cookie validity timeout (in seconds)
    After this, the session is invalid and the user must login again. Set to 0
    for the cookie to remain valid indefinitely.

  Use mod_auth_tkt compatabile hashing algorithm
    Compatibility with other implemenations, but at the cost of using a weaker
    hashing algorithm.

  Cookie name
    Which cookie to use. This must also be set on the
    ``credentials_cookie_auth`` plugin.

  Cookie lifetime (in days)
    This makes the cookie persistent across opening and closing the browser.

  Cookie domain (blank for default)
    A cookie may be shared across www1.example.com and www2.example.com by
    setting the cookie domain to ``.example.com``.

  Cookie path
    What path the cookie is set valid (defaults to ``/``.)
