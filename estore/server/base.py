import abc

class Collection(abc.ABC):

    @abc.abstractmethod
    def __aiter__(self):
        pass

    @abc.abstractmethod
    def __getitem__(self, index):
        pass
