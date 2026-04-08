from Identify import *
from _.ExtendedDoc import ExtendedDoc
from _.Grammar.Unit import ExtendedDoc, List, Unit

class Quotes(Identify):
    def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
        super().__init__(doc, units)
    

    def is_quote(self, i: int):
        return i < len(self.units) and self.units[i].lower() == "\""
    

    def identify(self):
        i = 0
        
        while i < len(self.units):
            if not self.is_quote(i):
                i += 1
                continue
            
            self.units[i].labels.add(Unit.QUOTE)
            
            while not self.is_quote(i+1):
                self.units[i].r = self.units[i+1].r
                self.units.pop(i+1)
            
            if self.is_quote(i+1):
                self.units[i].r = self.units[i+1].r
                self.units.pop(i+1)

        return self.units