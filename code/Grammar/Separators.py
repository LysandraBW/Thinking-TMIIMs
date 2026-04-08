from Identify import *
from _.ExtendedDoc import ExtendedDoc
from _.Grammar.Unit import ExtendedDoc, List, Unit

class Separators(Identify):
    def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
        super().__init__(doc, units)
    

    def is_break(self, i: int):
        if i >= len(self.units):
            return False
        
        if self.units[i].lower() not in [";", ","]:
            return False

        # Breaks cannot have a following conjunction.
        # Else, it would be an end and not a break.
        return not bool(
            i + 1 < len(self.units) and 
            self.units[i+1].size() == 1 and 
            self.units[i+1].span()[0].pos_ in ["CCONJ"]
        )

    
    def is_end(self, i: int):
        if i >= len(self.units):
            return False
        
        if self.units[i].lower() not in [";", ","]:
            return False
        
        return not self.is_break(i)


    def identify(self):
        i = 0

        while i < len(self.units):
            # Break
            if self.is_break(i):
                self.units[i].labels.add(Unit.BREAK)
                i += 1

            # End
            elif self.is_end(i):
                conj = self.units[i+1].start().lower_

                if conj in ["and", "or"]:
                    self.units[i].labels.add(Unit.AND_OR_END)
                else:
                    self.units[i].labels.add(Unit.END)
                
                self.units[i].r += 1
                self.units.pop(i+1)

            elif self.units[i].start().pos_ == "CCONJ":
                self.units[i].labels.add(Unit.CONJ)
                i += 1

            else:
                i += 1
                
        return self.units