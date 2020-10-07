import abc

class Engine(abc.ABC):
    @abc.abstractmethod
    def initialize(self):
        """ Do everything that is needed to initialize the DB"""

    """
    @abc.abstractmethod
    def insert(self, event):

    @abc.abstractmethod
    def query(self):


    @abc.abstractmethod
    def stream(self, stream_id):
        pass

    @abc.abstractmethod
    def stream_snapshot(self, stream_id):
        pass

    @abc.abstractmethod
    def events(self):
        pass

    @abc.abstractmethod
    def create_collection(self, store):
        pass
    """
