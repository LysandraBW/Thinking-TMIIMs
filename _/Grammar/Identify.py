from Unit import *
from ExtendedDoc import *
from abc import ABC, abstractmethod

class Identify(ABC):
    def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
        self.doc = doc
        self.units = units

    @abstractmethod
    def identify(self, *args, **kwargs) -> List[Unit]:
        pass

