class Error(Exception):
    pass

class AlreadyExists(Error):
    pass

class DoesNotExist(Error):
    pass
