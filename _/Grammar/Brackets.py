from Identify import *
from _.ExtendedDoc import ExtendedDoc
from _.Grammar.Unit import ExtendedDoc, List, Unit

class Brackets(Identify):
    MATCHES = {"[": "]",  "(": ")", "—": "—"}
    OPENING = MATCHES.keys()
    CLOSING = MATCHES.values()
    

    def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
        super().__init__(doc, units)
    

    def is_opening(self, i: int):
        return i < len(self.units) and self.units[i].lower()[0] in Brackets.OPENING


    def is_closing(self, i: int):
        return i < len(self.units) and self.units[i].lower()[0] in Brackets.CLOSING


    def closes(self, i: int):
        opener = self.units[self.stack[-1]].lower()[0]
        closer = self.units[i].lower()[0]
        return Brackets.MATCHES[opener] == closer
    

    def identify(self):
        self.stack = []
        
        i = 0
        while i < len(self.units):
            # Closing
            if self.is_closing(i) and self.stack:
                j = None if not self.closes(i) else self.stack.pop()
                
                if not self.stack and j != None:
                    self.units[j].r = self.units[i].r
                    self.units.pop(i)
                    continue
                else:
                    i += 1

            # Opening
            elif self.is_opening(i):
                if not self.stack:
                    self.units[i].labels.add(Unit.BRACKETS)
                self.stack.append(i)
                i += 1

            # Consuming
            elif self.stack:
                # If you're at the end of the possible units,
                # and the list is unclosed, we must stop.
                if i + 1 >= len(self.units):
                    break
                self.units[self.stack[0]].r = self.units[i+1].r
                self.units.pop(i)

            else:
                i += 1
        
        return self.units