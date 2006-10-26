plone.session Package
=====================

Overview
--------

This package implements a framework for PAS plugins that want to use
session authentication. It implements everything that is needed to
handle sessions; you only need to call it after authentication to allow
it to initialize the session.


plone.session concepts
----------------------

plone.session is meant to be used as a base class for PAS plugins which
want to use session based authentication. plone.session is acts as an
intermediary between three things:

 * PAS itself
 * a PAS plugin (the derived class) which takes care of initial authentication
 * an ISessionSource adapter which generates and verifies session identifiers

Making a PAS plugin
-------------------

Since plone.session takes care of most of the PAS bindings making
plugins using it is very simple. For most situations you only need write
a very simple credential extraction and credetential authentication
method.

If the credential extraction methods supplied by the standard PAS plugins
do not suffice you can write your own. The only requirement is that there
has to be a fallback to SessionPlugin.extractCredentials to allow plone.session
to extract the session identifier from the request. 

The procedure for custom authenticateCredentials is similar: you need to
call SessionPlugin.authenticateCredentials to allow plone.session to
authenticate the session identifier. 

There are two methods to initialize a session after succesful authentication:

 * call SessionPlugin.setupSession on succesful authentication
 * call the PAS updateCredentials method


ISessionSource adapters
-----------------------
plone.sesion ships with two example adapers: hash and userid.

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

Creating adapters is very simple: an adapter needs to implement the
plone.session.interfaces.ISessionSource interface and has to be registered
with the component architecture.

