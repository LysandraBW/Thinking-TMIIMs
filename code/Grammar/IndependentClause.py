from .Unit import Unit
from .DependentClause import *
from typing import List


class IndependentClause:
    
    @staticmethod
    def is_end(units: List[Unit], i: int, delimiters: List[int]):
        if i >= len(units):
            return True

        if units[i].label_has(delimiters):
            return True
        
        # Here, we check if the unit after
        # the supposed end is a clause. If it
        # is, then we can end at the current unit.
        return bool(
            i + 1 < len(units) and 
            units[i+1].label_has([
                Unit.COLON,
                Unit.COLON_BREAK,
                Unit.I_CLAUSE,
                Unit.D_CLAUSE
            ])
        )

    

    @staticmethod
    def identify(units: List[Unit], delimiters: List[int], verbose=False):
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')
        
        i = 0
        while i < len(units):
            if verbose:
                print(f"[i={i}] Unit: '{units[i].text()}'")
            
            # Skip: Not Start
            is_delim = units[i].label_has(delimiters)
            is_start = units[i].start().lower_ not in DependentClause.RELATIVE_NOUNS and units[i].start().pos_ not in ["ADP", "SCONJ", "CCONJ"]

            if verbose:
                print(f'\tis_delim: {is_delim}')
                print(f'\tis_start: {is_start}')

            if not is_delim and not is_start:
                i += 1
                if verbose:
                    print(f'\t\tSkipped')
                
                continue
            
            # Skip: Clause Conflict
            if units[i].label_has([Unit.I_CLAUSE, Unit.D_CLAUSE, Unit.P_PHRASE]):
                i += 1
                if verbose:
                    print(f'\tSkipped: Clause Conflict')
                
                continue
            
            # I don't want the conjunction to be a
            # part of the clause.
            if is_delim:
                i += 1
            
            # Create Clause
            units[i].labels.add(Unit.I_CLAUSE)

            while not IndependentClause.is_end(units, i + 1, delimiters):
                units[i].r = units[i+1].r

                # Add Child
                if units[i+1].label_has([Unit.BRACKETS, Unit.QUOTE, Unit.P_PHRASE]):
                    units[i].children.append(units[i+1])
                
                units.pop(i+1)

            i += 1

            if verbose:
                print()
                print()
        
        if verbose:
            print(f'Out: {[unit.text() for unit in units]}\n\n')
        
        return units
    

    
    def __new__(cls, units: List[Unit], delimiters: List[int], verbose=False):
        return IndependentClause.identify(units, delimiters=delimiters, verbose=verbose)