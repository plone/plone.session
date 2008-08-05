#!/bin/python
"""
Example mod_auth_tkt cookie authentication
==========================================

See: http://www.openfusion.com.au/labs/mod_auth_tkt/

This is a python doctest, you may run this file to execute the test with the
command `python tktauth.py`. No output indicates success.

The protocol depends on a secret string shared between servers. From time to
time this string should be changed, so store it in a configuration file.

  >>> SECRET = 'abcdefghijklmnopqrstuvwxyz0123456789'

The tickets are only valid for a limited time. Here we will use 12 hours

  >>> TIMEOUT = 12*60*60


Cookie creation
---------------

You should not need to implement this, but we need something to test.

  >>> userid = 'jbloggs'

We first set the timestamp that the user logged in, for the purposes of this
test 2008-07-22 11:00:

  >>> timestamp = 1216720800

In the simplest case no extra data is supplied.

  >>> tkt = createTicket(userid, timestamp=timestamp, secret=SECRET)
  >>> tkt
  'c7c7300ac5cf529656444123aca345294885afa0jbloggs!'

The cookie itself is base64 encoded.

  >>> import Cookie, binascii
  >>> cookie = Cookie.SimpleCookie()
  >>> cookie['auth_tkt'] = binascii.b2a_base64(tkt).strip()
  >>> print cookie
  Set-Cookie: auth_tkt=YzdjNzMwMGFjNWNmNTI5NjU2NDQ0MTIzYWNhMzQ1Mjk0ODg1YWZhMGpibG9nZ3Mh...


Cookie validation
-----------------

First the ticket has to be read from the cookie and unencoded:

  >>> tkt = binascii.a2b_base64(cookie['auth_tkt'].value)
  >>> tkt
  'c7c7300ac5cf529656444123aca345294885afa0jbloggs!'

Splitting the data reveals the contents (note the unicode output):

  >>> splitTicket(tkt)
  ('c7c7300ac5cf529656444123aca34529', u'jbloggs', (), u'', 1216720800)

We will validate it an hour after it was created:

  >>> NOW = timestamp + 60*60
  >>> validateTicket(tkt, timeout=TIMEOUT, secret=SECRET, now=NOW)
  True

After the timeout the ticket is no longer valid

  >>> LATER = NOW + TIMEOUT
  >>> validateTicket(tkt, timeout=TIMEOUT, secret=SECRET, now=LATER)
  False


Tokens and user data
--------------------

The format allows for optional user data and tokens. We will store the user's
full name in the user data field. We are not yet using tokens, but may do so in
the future.

  >>> user_data = 'Joe Bloggs'
  >>> tokens = ['foo', 'bar']
  >>> tkt = createTicket(userid, tokens, user_data, timestamp=timestamp, secret=SECRET)
  >>> tkt
  'eea3630e98177bdbf0e7f803e1632b7e4885afa0jbloggs!foo,bar!Joe Bloggs'
  >>> cookie['auth_tkt'] = binascii.b2a_base64(tkt).strip()
  >>> print cookie
  Set-Cookie: auth_tkt=ZWVhMzYzMGU5ODE3N2JkYmYwZTdmODAzZTE2MzJiN2U0ODg1YWZhMGpibG9nZ3MhZm9vLGJhciFKb2UgQmxvZ2dz...
  >>> splitTicket(tkt)
  ('eea3630e98177bdbf0e7f803e1632b7e', u'jbloggs', (u'foo', u'bar'), u'Joe Bloggs', 1216720800)
  >>> validateTicket(tkt, timeout=TIMEOUT, secret=SECRET, now=NOW)
  True

"""

import time
import md5
from socket import inet_aton
from struct import pack

SECRET = 'abcdefghijklmnopqrstuvwxyz0123456789'


def createTicket(userid, tokens=[], user_data=u'', ip='0.0.0.0', timestamp=None, secret=SECRET, encoding='utf8'):
    # ip address is part of the format, we set it to 0.0.0.0 to be ignored
    ip = inet_aton(ip)

    if timestamp is None:
        timestamp = int(time.time())

    userid = userid.encode(encoding)
    token_list = ','.join(tokens).encode(encoding)
    user_data = user_data.encode(encoding)

    # pack is used to convert timestamp from an unsigned integer to 4 bytes
    # in network byte order.
    digest0 = md5.new( ip + pack("!I", timestamp) + secret +
                '\0'.join((userid, token_list, user_data)) ).hexdigest()
    
    digest = md5.new(digest0 + secret).hexdigest()

    # digest + timestamp as an eight character hexadecimal + userid + !
    ticket = "%s%08x%s!" % (digest, timestamp, userid) 
    if tokens:
        ticket += token_list + '!'
    ticket += user_data

    return ticket


def splitTicket(ticket, encoding='utf8'):
    digest = ticket[:32]
    timestamp = int(ticket[32:40], 16) # convert from hexadecimal
    parts = ticket[40:].decode(encoding).split("!")

    if len(parts) == 2:
        userid, user_data = parts
        tokens = ()
    elif len(parts) == 3:
        userid, token_list, user_data = parts
        tokens = tuple(token_list.split(','))
    else:
        raise ValueError

    return (digest, userid, tokens, user_data, timestamp)


def validateTicket(ticket, ip='0.0.0.0', timeout=None, secret=SECRET, now=None, encoding='utf8'):
    """
    To validate, a new ticket is created from the data extracted from cookie
    and the shared secret. The two digests are compared and timestamp checked.
    """
    (digest, userid, tokens, user_data, timestamp) = splitTicket(ticket)
    new_ticket = createTicket(userid, tokens, user_data, ip, timestamp, secret, encoding)
    if new_ticket[:32] == digest:
        if timeout is None:
            return True
        if now is None:
            now = time.time()
        if timestamp + timeout > now:
            return True
    return False


# doctest runner
def _test():
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)

if __name__ == "__main__":
    _test()
