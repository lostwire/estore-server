import abc

class Engine(abc.ABC):
    @abc.abstractmethod
    def insert(self, event):
        """Insert event to the database"""

    @abc.abstractmethod
    def query(self):
        """ Factory of queries """

    @abc.abstractmethod
    def initialize(self):
        """ Do everything that is needed to initialize the DB"""
