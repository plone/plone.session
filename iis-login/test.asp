<%@ Language = "Python" %>
<html>
<head>
<title>Integrated Windows Authentication test page</title>
</head>
<body>
<h1>Integrated Windows Authentication test page</h1>
<ul>
<%
results = []
errors = 0
try:
    import tktauth
except ImportError:
    results.append("ERROR: Unable to import the tktauth module.")
    errors += 1
else:
    results.append("Successfully imported the tktauth module.")

userid = str(Request.ServerVariables("REMOTE_USER"))
if not userid:
    results.append("ERROR: No user information available. Check server configuration and disallow anonymous access.")
    errors += 1
else:
    if '\\' in userid:
        # if we get a domain for the user ignore it
        userid = userid.split('\\')[-1]
    results.append("Successfully found user information (%s)." % userid)

Response.write('\r\n'.join('<li>%s</li>' % r for r in results))
%>
</ul>

<%
if not errors:
    Response.write('''\
    <p>Test completed successfully, the login page should work correctly. If you
    were prompted with a login box, check that Integrated Windows Authentication
    is enabled in IIS and that your browser security are correct.</p>
    ''')
else:
    Response.write('''\
    <p><b>Test failed</b></p>
    ''')
%>
</body>
</html>
