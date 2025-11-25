from abc import ABC, abstractmethod

class BaseDriver(ABC):
    def __init__(self, device):
        self.device = device

    @abstractmethod
    def get_config(self):
        pass
