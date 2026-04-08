from Identify import *
from _.ExtendedDoc import ExtendedDoc
from _.Grammar.Unit import ExtendedDoc, List, Unit

class Colons(Identify):
    def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
        super().__init__(doc, units)
    
    
    def identify(self):
        i = 0

        while i < len(self.units):
            if self.units[i].lower()[-1] != ":":
                i += 1
                continue

            self.units[i].labels.add(Unit.COLON_BREAK)

            if i + 1 < len(self.units):
                self.units[i+1].labels.add(Unit.COLON)
                self.units[i+1].r = self.units[-1].r
                self.units = self.units[:i+2]
            
            break

        return self.units        