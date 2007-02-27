from zope.interface import Interface

class ISessionPlugin(Interface):
    """
    Session handling PAS plugin.
    """

    def setupSession(userid):
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


    def extractUserid(identifier):
        """
        Extract the userid from an identifier.
        """


    def invalidateSession(principal):
        """
        Mark a session for a userid as invalid. 
        """

