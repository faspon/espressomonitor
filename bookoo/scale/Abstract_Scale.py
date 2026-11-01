from abc import ABC, abstractmethod
from enum import Enum

class AbstractScale(ABC):

    @abstractmethod
    def read_scale_data(self):
        pass