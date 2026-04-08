from .Unit import Unit
from .Identify import *
from typing import List


class Bracket:
    MATCHES = {"[": "]",  "(": ")", "—": "—", "{": "}"}
    OPENING = MATCHES.keys()
    CLOSING = MATCHES.values()
    


    @staticmethod
    def is_opening(units: List[Unit], i: int) -> bool:
        return i < len(units) and units[i].lower()[0] in Bracket.OPENING



    @staticmethod
    def is_closing(units: List[Unit], i: int) -> bool:
        return i < len(units) and units[i].lower()[0] in Bracket.CLOSING



    @staticmethod
    def closes(units: List[Unit], i: int, stack: List[str]) -> bool:
        if not stack:
            return False
        opener = stack[-1]
        closer = units[i].lower()[0]
        return Bracket.MATCHES[opener] == closer
    

    
    @staticmethod
    def identify(units: List[Unit], verbose=False):
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')
        
        stack: List[str] = []

        i = 0
        while i < len(units):
            if verbose:
                print(f"[i={i}] Unit: '{units[i].text()}'")
                print(f'Stack: {stack}')
                print(f'Units: {[unit.text() for unit in units]}')
            
            # Closing
            if Bracket.is_closing(units=units, i=i) and Bracket.closes(units=units, i=i, stack=stack):
                if verbose:
                    print('\tClose')
                
                stack.pop()
                units[i-1].r = units[i].r
                units.pop(i)
            
            # Opening
            elif Bracket.is_opening(units=units, i=i):
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

            print()
            print()

        if verbose:
            print(f'Out: {[unit.text() for unit in units]}\n\n')
        
        return units
    
    

    def __new__(cls, units: List[Unit], verbose=False):
        return Bracket.identify(units, verbose)