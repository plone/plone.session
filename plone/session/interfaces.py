from zope.interface import Interface

class ISessionPlugin(Interface):
    """
    Session handling PAS plugin.
    """

    def setupSession(userid, response):
        """
        Start a new session for a userid. The session will last until
        PAS indicates that the user has logged out.
        """


class ISessionSource(Interface):
    """
    A session source is an object which creates a session identified and
    can verify if session is still valid.
    """

    def createIdentifier(userid):
        """
        Return an identifier for a userid. An identifier is a standard python
        string object.
        """


    def verifyIdentifier(identifier):
        """
        Verify if an identity corresponds to a valid session. Returns
        a boolean indicating if the identify is valid.
        """


    def extractUserId(identifier):
        """
        Extract the user id from an identifier.
        """


    def invalidateSession(principal=None):
        """
        Mark a session for a principal as invalid. A source may not support
        this, in which case it should return False.
        """



