<%@ Language = "Python" %><%
#########################################
# Configuration constants
SECRET = 'abc123'
ALLOWED_SITES = [
    'http://localhost:8080/Plone',
]
DEFAULT_NEXT = 'http://localhost:8080/Plone/logged_in'
MOD_AUTH_TKT = False
#########################################
import tktauth
import binascii
import string
from urlparse import urlparse

Response.CacheControl = "no-cache"
Response.AddHeader("Pragma", "no-cache")
Response.Expires = -1
Response.AddHeader("Content-Type", "text/html; charset=utf-8")

CAME_FROM_NAME = 'came_from'
TICKET_NAME = '__ac'

next_url = DEFAULT_NEXT
next = Request.QueryString('next')
if next and str(next) != 'None':
    _, u_host, u_path, _, _, _ = urlparse(next)
    for external_site in ALLOWED_SITES:
        _, host, path, _, _, _ = urlparse(external_site)
        if not path.endswith('/'):
            path += '/'
        if host == u_host and u_path.startswith(path):
            next_url = next
            break

userid = str(Request.ServerVariables("REMOTE_USER"))
if not userid:
    # Don't process any further without credentials
    raise ValueError("You must not allow anonymous access to this page.")

if '\\' in userid:
    # if we get a domain for the user ignore it
    userid = userid.split('\\')[-1]

ticket = tktauth.createTicket(SECRET, userid, mod_auth_tkt=MOD_AUTH_TKT)
ticket = binascii.b2a_base64(ticket).rstrip()

came_from = Request.QueryString(CAME_FROM_NAME)
if not came_from or str(came_from) == 'None':
    came_from = ''

target = Request.QueryString('target')
if target in ('_parent', '_top', '_blank', '_self'):
    target_attr = 'target="%s"' % target
else:
    target_attr = ''

# An automatic form post is used to prevent the ticket being stored in the
# browser's history.

FORM = string.Template('''
<form action="$action" method="post" name="external_login_form"$target_attr>
<!-- userid: $userid -->
<input type="hidden" name="$ticket_name" value="$ticket" />
<input type="hidden" name="$came_from_name" value="$came_from" />
You do not have javascript enabled. Press button to log in:
<input type="submit" name="login" value="Login" />
</form>
''')
form_html = FORM.substitute(
    action=next_url,
    target_attr=target_attr,
    ticket_name=TICKET_NAME,
    ticket=ticket,
    came_from_name=CAME_FROM_NAME,
    came_from=came_from,
    userid=userid,
    )

%><!DOCTYPE html>
<html lang="en">
<head>
<title>Login</title>
</head>
<body>
<div id="box">
<h1>Login</h1>
<p>Please wait while you are logged in</p>
<%
Response.write(form_html)
%>
<script type="text/javascript">
    external_login_form = document.external_login_form;
    external_login_form.style.display = 'none';
    external_login_form.submit();
</script>
</div>
</body>
</html>
