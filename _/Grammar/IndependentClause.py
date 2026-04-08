from Identify import *
from _.ExtendedDoc import ExtendedDoc
from _.Grammar.Unit import ExtendedDoc, List, Unit


class Independent_Clauses(Identify):
    def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
        super().__init__(doc, units)
    
    
    def end(self, i: int):
        if i >= len(self.units):
            return True

        if self.units[i].label_has(self.allowed):
            return True
        
        # Here, we check if the unit after
        # the supposed end is a clause. If it
        # is, then we can end at the current unit.
        return bool(
            i + 1 < len(self.units) and 
            self.units[i+1].label_has([
                Unit.COLON,
                Unit.COLON_BREAK,
                Unit.I_CLAUSE,
                Unit.D_CLAUSE
            ])
        )


    def identify(self, allowed: List[int]):
        self.allowed = allowed
        
        i = 0
        
        while i < len(self.units):
            if not self.units[i].label_has(self.allowed):
                i += 1
                continue
            
            # Skip Clause
            if self.units[i].label_has([
                Unit.I_CLAUSE, 
                Unit.D_CLAUSE, 
                Unit.P_PHRASE
            ]):
                i += 1
                continue

            # Create Clause
            self.units[i].labels.add(Unit.I_CLAUSE)
            while not self.end(i+1):
                self.units[i].r = self.units[i+1].r

                # Add Child
                if self.units[i+1].label_has([Unit.BRACKETS, Unit.QUOTE, Unit.P_PHRASE]):
                    self.units[i].children.append(self.units[i+1])
                    
                self.units.pop(i+1)

            i += 1
            
        return self.units