Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

4.0.1 (2023-01-30)
------------------

Internal:


- Update code to current Plone meta standards.
  [gforcada, maurits] (#1)


4.0.0 (2022-12-02)
------------------

Bug fixes:


- Final release for Plone 6.0.0 (#600)


4.0.0b2 (2022-08-31)
--------------------

New features:


- Creating per-user keyrings in order to have session invalidation on log-out (server-side logout). [david-batranu] (#26)
- Cookie attribute SameSite is set to "Lax". (#29)


4.0.0b1 (2022-07-22)
--------------------

Bug fixes:


- Update the plone-session bundle to depend on the plone bundle instead of the jquery bundle, which no longer exists.
  [davisagli] (#27)


4.0.0a1 (2022-04-08)
--------------------

Breaking changes:


- Register single resource bundle for Plone 6 for our optional refresh support.
  An upgrade step for this is in plone.app.upgrade, otherwise we leave partial bundles behind.
  Removed our own upgrade step and profile, as they are not needed when migrating from Plone 5.2.
  [maurits] (#24)


3.7.5 (2020-06-24)
------------------

Bug fixes:


- Fix hard dependency indirection with Products.CMFPlone (plone.session must not import from it).
  [jensens] (#20)
- Only setup a session when the current user is the requested user.
  [maurits] (#57)


3.7.4 (2020-04-22)
------------------

Bug fixes:


- Minor packaging updates. (#1)


3.7.3 (2019-04-29)
------------------

Bug fixes:


- Fix nameclash resulting in ImportWarning by renaming ``profiles.py`` to ``hiddenprofiles.py``. [jensens] (#16)


3.7.2 (2019-02-13)
------------------

Bug fixes:


- Remove last traces of ZopeTestCase. [gforcada] (#14)


3.7.1 (2018-09-28)
------------------

Bug fixes:

- Python3 compatibility [ale-rt, pbauer]


3.7.0 (2018-04-03)
------------------

New features:

- Use Resource Registry for JS/CSS registration
  [jensens]

Bug fixes:

- Fixes #11: Pseudo CSS-file is not loaded anymore in merged legacy bundle.
  Now optional JS based auto-refresh support is working again.
  [jensens]

- Modernize README.
  [jensens]


3.6.2 (2018-02-02)
------------------

Bug fixes:

- Hardening default timeout of session.
  This solves Plone security internal issue #126 (severity low, non-critical).
  Session timeout is now the same as in mod_auth_tkt: 2h.
  This follows the recommendation of the German BSI (federal office for security in the information technology).
  See https://www.bsi.bund.de/SharedDocs/Downloads/DE/BSI/Internetsicherheit/isi_web_server_checkliste_Plone.pdf
  For existing sites this can be adjusted at https://HOST/acl_users/session/manage_propertiesForm
  The Plone Security Team follows the BSI and recommends administrators to change the setting in their existing Plone sites.
  [jensens]

- Add Python 2 / 3 compatibility
  [vincero]


3.6.1 (2016-12-02)
------------------

Bug fixes:

- Hide uninstall profile in install listings.
  [jensens]


3.6.0 (2016-05-26)
------------------

New:

- Added uninstall profile.  [maurits]


3.5.6 (2015-07-27)
------------------

- Cleanup: Pep8, plone style conventions, better readbility.
  [jensens]


3.5.5 (2015-04-29)
------------------

- Default encoding for createTicket to be compatible with unicode
  user_id [puittenbroek]


3.5.4 (2015-03-21)
------------------

- Move tests from PloneTestCase to plone.app.testing.
  [tomgross]


3.5.3 (2013-03-05)
------------------

- Revert accidental change to default encoding for validateTicket.
  [davisagli]

3.5.2 (2012-12-09)
------------------

- Use constant time comparison when validating tickets. This is part of the fix
  for https://plone.org/products/plone/security/advisories/20121106/23
  [davisagli]

3.5.1 - 2012-11-02
------------------

- Handle encoded strings for userids.
  [elro]

- Add MANIFEST.in.
  [WouterVH]

- Fix for Python 2.4 under 64bit Mac OS generating incorrect mod_auth_tkt
  digests
  [MatthewWilkes]


3.5 - 2011-03-19
----------------

- Disable secure cookie in development mode, to ease local testing.
  [hannosch]


3.4 - 2011-03-02
----------------

- Added metadata.xml to the default profile.
  [vincentfretin]


3.3 - 2010-12-30
----------------

- Update login.asp to match Plone 4.1 SSO login form functionality.
  [elro]

- Fix remove.
  [elro]


3.2 - 2010-12-14
----------------

- Remove ``external_login`` method, the normal ``logged_in`` script can be
  used instead.
  [elro]

- Fix refresh.
  [elro]


3.1 - 2010-11-11
----------------

- Remove ``SessionPlugin.validate(ticket)`` method, it was not required.
  [elro]


3.1b1 - 2010-10-18
------------------

- Session refresh.
  [elro]

- ``SessionPlugin.validate(ticket)`` method.
  [elro]

- Close <input> tags properly (chameleon compatibility)
  [swampmonkey]


3.0 - 2010-07-18
----------------

- Update package metadata.
  [hannosch]


3.0b5 - 2010-06-13
------------------

- Make sure to load the right meta ZCML.
  [hannosch]

- Avoid deprecation warnings under Zope 2.13.
  [hannosch]

- Removed dependency on GPL licensed Products.PloneTestCase.
  [hannosch]


3.0b4 - 2010-05-23
------------------

- Make the ``secure`` option of cookies configurable. This allows to restrict
  cookies to HTTPS connections alone. This closes
  http://dev.plone.org/plone/ticket/7897.
  [pfurman, hannosch]

- Use the standard libraries doctest module, instead of the deprecated one
  from zope.testing.
  [hannosch]

- Marked the session cookie as ``HTTPOnly``.
  [hannosch]

- PEP8 cleanup.
  [hannosch]

- Relicense as BSD following PF Board decision.
  http://lists.plone.org/pipermail/membership/2010-April/001123.html
  [elro]


3.0b3 - 2010-04-09
------------------

- Example IIS login form and documentation. This builds on work by Hanno and I
  at Jarn for Centrepoint.
  [elro]

- Support authentication by an external form, perhaps one running on an IIS
  server with Integrated Windows Authentication.
  [elro]


3.0b2 - 2010-03-09
------------------

- Prefix setupSession with underscore, the method should be unavailable TTW.
  [elro]

- Catch a ComponentLookupError in authenticateCredentials.
  [elro]


3.0b1 - 2010-03-05
------------------

- Add back the hash management UI with added functionality to set shared
  secret.
  [elro]

- Add properties for cookie domain and ticket validity timeout.
  [elro]

- Use mod_auth_tkt format cookies to give us a session validity timeout.
  By default we use a more secure HMAC SHA-256 hashing scheme. An MD5 based
  scheme compatible with other mod_auth_tkt implementations is optional.
  [elro]

- Remove the source component indirection.
  [elro]


3.0a2 - 2009-11-13
------------------

- Remove hash management UI which had been accidentally re-merged.
  [davisagli]


3.0a1 - 2009-04-04
------------------

- Avoid deprecation warning for the sha module in Python 2.6.
  [hannosch]

- Declare test dependencies in an extra.
  [hannosch]

- Specify package dependencies.
  [hannosch]

- Fixed the remaining tests to work with the new keyring backend.
  [hannosch]

- Fixed a component lookup call in the HashSession source.
  [davisagli, hannosch]

- Update default (hash) session source to use plone.keyring to manage the secrets.
  [wichert]


2.1 - 2009-02-04
----------------

- Protect the setupSession call with the ManageUsers permission.
  Fixes possible privilege escalation.
  [maurits]

- Make the cookie lifetime configurable. Patch by Rok Garbas.
  Fixes http://dev.plone.org/plone/ticket/7248
  [wichert, garbas]


2.0 - 2008-07-08
----------------

- Fix CSRF protection for managing server secrets via the Plone session
  plugin for PAS. Fixes http://dev.plone.org/plone/ticket/8176
  [witsch]


1.2 - 2007-02-15
----------------

- Use the binascii base64 methods to encode/decode the session cookie. This
  prevents newlines being inserted in long cookies.
  [wichert]


1.1 - 2007-09-11
----------------

- Use the userid instead of the login name in session identifiers. This has the
  side-effect of working around a bug in PAS which caused us to mix up users when
  the login name used was an inexact match for another login name.
  [wichert]


1.0 - 2007-08-15
----------------

- First stable release
  [wichert]
