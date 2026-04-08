from .Unit import Unit
from typing import List

class Quote:    
    @staticmethod
    def is_opening(units: List[Unit], i: int) -> bool:
        if i >= len(units):
            return False
        
        s = units[i].lower()[0]
        return (s == "'" or s == '"') and units[i].span()[0].pos_ == "PUNCT"
    


    @staticmethod
    def is_closing(units: List[Unit], i: int) -> bool:
        if i >= len(units):
            return False
        
        s = units[i].lower()[0]
        return (s == "'" or s == '"') and units[i].span()[0].pos_ == "PUNCT"
    


    @staticmethod
    def closes(units: List[Unit], i: int, stack: List[str]) -> bool:
        if not stack:
            return False
        
        opener = stack[-1]
        closer = units[i].lower()

        return opener == closer
    


    @staticmethod
    def identify(units: List[Unit], verbose=False):
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')
        
        stack: List[str] = []

        i = 0
        while i < len(units):
            if verbose:
                print(f"[i={i}] [POS={units[i].span()[0].pos_}] Unit: '{units[i].text()}'")
                print(f'Stack: {stack}')
                print(f'Units: {[unit.text() for unit in units]}')
            
            # Closing
            if Quote.is_closing(units=units, i=i) and Quote.closes(units=units, i=i, stack=stack):
                if verbose:
                    print('\tClose')
                
                stack.pop()
                units[i-1].r = units[i].r
                units.pop(i)
            
            # Opening
            elif Quote.is_opening(units=units, i=i):
                if verbose:
                    print('\tOpen')
                
                stack_has = bool(stack)
                stack.append(units[i].lower()[0])

                if stack_has:
                    units[i-1].r = units[i].r
                    units.pop(i)
                else:
                    units[i].labels.add(Unit.BRACKETS)
                    i += 1
            
            # Consuming
            elif stack:
                if verbose:
                    print('\tConsume')
                
                units[i-1].r = units[i].r
                units.pop(i)

            else:
                i += 1

            if verbose:
                print()
                print()


        if verbose:
            print(f'Out: {[unit.text() for unit in units]}\n\n')
        
        return units
    


    def __new__(cls, units: List[Unit], verbose=False):
        return Quote.identify(units, verbose)