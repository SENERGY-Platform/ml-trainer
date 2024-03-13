import abc

class DataLoader():
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def get_data(self):
        pass