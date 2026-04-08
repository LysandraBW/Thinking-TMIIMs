from .Unit import Unit
from typing import List

class Colon:
    @staticmethod
    def identify(units: List[Unit], verbose=False):
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')
        
        i = 0
        while i < len(units):
            if verbose:
                print(f"[i={i}] Unit: '{units[i].text()}'\n\n")
            
            if units[i].lower()[-1] != ":":
                i += 1
                continue

            units[i].labels.add(Unit.COLON_BREAK)

            if i + 1 < len(units):
                units[i+1].labels.add(Unit.COLON)
                units[i+1].r = units[-1].r
                units = units[:i+2]
            
            break

        if verbose:
            print(f'Out: {[unit.text() for unit in units]}\n\n')
        
        return units


    def __new__(cls, units: List[Unit], verbose=False):
        return Colon.identify(units, verbose)