from abc import ABC, abstractmethod

class AbstractPressureSensor(ABC):
    @abstractmethod
    def read_pressure_data(self):
        pass