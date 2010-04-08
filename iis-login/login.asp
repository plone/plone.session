<%@ Language = "Python" %><%
#########################################
# Configuration constants
SECRET = 'abc123'
PLONE_URL = 'http://localhost:8080/Plone'
MOD_AUTH_TKT = False
#########################################
import tktauth
import binascii
import string

Response.CacheControl = "no-cache"
Response.AddHeader("Pragma", "no-cache")
Response.Expires = -1
Response.AddHeader("Content-Type", "text/html; charset=utf-8")

CAME_FROM_NAME = 'came_from'
TICKET_NAME = 'ticket'
NEXT_URL = PLONE_URL + '/acl_users/session/external_login'

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

# An automatic form post is used to prevent the ticket being stored in the
# browser's history.

FORM = string.Template('''
<form action="$action" method="post" name="login_form">
<!-- userid: $userid -->
<input type="hidden" name="$ticket_name" value="$ticket" />
<input type="hidden" name="$came_from_name" value="$came_from" />
You do not have javascript enabled. Press button to log in:
<input type="submit" name="login" value="Login" />
</form>
''')
form_html = FORM.substitute(
    action=NEXT_URL,
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
<script language="javascript">
form = document.login_form;
form.style.display = 'none';
form.submit();
</script>
</div>
</body>
</html>
