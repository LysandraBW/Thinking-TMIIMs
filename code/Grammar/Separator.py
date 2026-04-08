from .Unit import Unit
from typing import List

# The meaning of a break and an end is a bit
# ambiguous.

# From what I can gather,
# - End: r'[;,] [CCONJ]'
# - Break: r'[;,] [^CCONJ]'

# I don't like these terms.
# Shame on you.
# So, I'd like to rename them.
# end   -> SEP_PUNCTUATION_CONJUNCTION
#       -> SEP_PUNCTUATION_AND_OR
# break -> SEP_PUNCTUTATION
 

class Separator:
    @staticmethod
    def conj_follows_punct_not(units: List[Unit], i: int):
        if i >= len(units):
            return False
        
        if units[i].lower() not in [";", ","]:
            return False

        return not bool(
            i + 1 < len(units) and 
            units[i+1].size() == 1 and 
            units[i+1].span()[0].pos_ == "CCONJ"
        )

    
    @staticmethod
    def conj_follows_punct(units: List[Unit], i: int):
        if i >= len(units):
            return False
        
        if units[i].lower() not in [";", ","]:
            return False
        
        return bool(
            i + 1 < len(units) and 
            units[i+1].size() == 1 and 
            units[i+1].span()[0].pos_ == "CCONJ"
        )



    @staticmethod
    def identify(units: List[Unit], verbose=False):
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')
        
        i = 0
        while i < len(units):
            if verbose:
                print(f"[i={i}|PoS={units[i].span()[0].pos_}{str('' if len(units[i].span()) != 2 else f'|nPoS={units[i].span()[1].pos_}')}{'' if i + 1 >= len(units) else f'''|nUnit={units[i+1].span()}'''}] Unit: '{units[i].text()}'")
                print(f'Units: {[unit.text() for unit in units]}\n\n')

            # Separator Type: Punctuation
            if Separator.conj_follows_punct_not(units, i):
                units[i].labels.add(Unit.SEP_PUNCT)
                i += 1
            
            # Separator Type: Punctuation -> Conjunction
            elif Separator.conj_follows_punct(units, i):
                conjunction = units[i+1].start().lower_

                # Adding Specificity
                if conjunction in ["and", "or"]:
                    units[i].labels.add(Unit.SEP_PUNCT_AND_OR)
                else:
                    units[i].labels.add(Unit.SEP_PUNCT_CONJ)
                
                units[i].r += 1
                units.pop(i+1)
            
            # Separator Type: Conjunction
            elif units[i].start().pos_ == "CCONJ":
                units[i].labels.add(Unit.SEP_CONJ)
                i += 1

            else:
                i += 1
        
        if verbose:
            print(f'Out: {[unit.text() for unit in units]}\n\n')
        
        return units



    def __new__(cls, units: List[Unit], verbose=False):
        return Separator.identify(units, verbose)