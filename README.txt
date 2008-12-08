Overview
--------

plone.session implements secure session management for Zope sites. It
can be used directly, or be used as a base for custom session management
strategies.

In its default configuration plone.sessions uses a secure cryptographic
hash based on HMAC_ SHA-1_ to authenticate sessions. The hash is generated
using the users login name and a secret stored in the PAS plugin. This has
several advantages over other session management systems:

* passwords are not send to the server in a cookie on every request, as
  is done by the *Cookie Auth Helper* 
* it does not require any ZODB write for sessions, as is needed by the
  *Session Crumbler*. This allows it to scale very well.
* it allows you to invalidate all existing authentication cookies for
  users by updating the secret.

Normally a session cookie is used to track sessions; that means that as long as
a user keeps his browser open (and does not explicitly log out) the session
remains opens. This can be changed by setting the ``cookie_lifetime`` property
of the plugin to the number of seconds the cookie should remain valid *after
the moment of login*. 

.. _HMAC: http://en.wikipedia.org/wiki/HMAC
.. _SHA-1: http://en.wikipedia.org/wiki/SHA-1

Using plone.session
-------------------

plone.session only takes care of handling sessions for already authenticated
users. This means it can not be used stand-alone: you need to have another
PAS plugin, such as the standard *Cookie Auth Helper* to take care of
authentication.

After a user has been authenticated plone.session can take over via the
PAS *credentials update* mechanism. 


Using custom session authentication
-----------------------------------

plone.session delegates the generation and verification of sessions to
an ISessionSource adapter. This adapter adapts the PAS plugin and
implements four methods:

createIdentifier
    Return an identifier for a userid. An identifier is a standard python
    string object.

verifyIdentifier
    Verify if an identity corresponds to a valid session. Returns
    a boolean indicating if the identify is valid.

extractLoginName
    Extract the login name from an identifier.

invalidateSession
    Mark a session for a principal as invalid. A source may not support this,
    in which case it should return False.

plone.session ships with two example adapers: hash and userid.

The userid adapter is a trivial example which uses the userid as session
identifier.  This is very insecure since there is no form of verification at
all. DO NOT USE THIS ADAPTER IN YOUR SITE!

The hash plugin creates a random secret string which is stored as an attribute
on your plugin. It uses this secret to create a SHA1 signature for the user id
with the secret as session identifier. This approach has several good qualities:

* it allows us to verify that a session identifier was created by this site
* there is no need to include passwords in the session idenfitier
* it does not need to store anything in Zope itself. This means it works
  as-is in ZEO setups and can scale very well.

There are a few downsides to this approach:

* if a users password is changed or disabled session identifiers will continue
  to work, making it hard to lock out users

