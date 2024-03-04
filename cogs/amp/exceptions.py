class FailedToLogin(Exception):
    """Raised when the bot fails to login to the AMP API."""
    pass

class NoServer(Exception):
    """Raisedn when the server does not exist."""
    pass

class ServerAlreadyRunning(Exception):
    """Raised when the server is already running."""
    pass

class ServerAlreadyStopped(Exception):
    """Raised when the server is already stopped."""
    pass

class InsufficientRam(Exception):
    """Raised when there is not enough RAM available to start the server."""
    pass

class ServerStartFailed(Exception):
    """Raised when the server fails to start - this is a generic reason."""
    pass