from .Unit import *
from .DependentClause import *
from typing import List


class PrepositionalPhrase:
    # A prepositional phrase is typically ended by a noun.
    # Therefore, when we run into a noun, we end the phrase.
    # We must also check that it is the last of the first noun(s)
    # we encounter.
    @staticmethod
    def is_last_noun(units: List[Unit], i: int):
        speech = units[i].start().pos_

        if bool(
            # 1. End
            i >= len(units) or 
            
            # 2. Noun
            speech not in [
                "NOUN", 
                "PROPN", 
                "PRON"
            ]
        ):
            return False

        return bool(
            i + 1 >= len(units) or 
            (
                units[i+1].size() == 1 and 
                (
                    units[i+1].start().pos_ not in ["NOUN", "PROPN","PART"] or
                    units[i+1].start().lower_ in Dependent_Clauses.RELATIVE_NOUNS
                )
            )
        )



    @staticmethod
    def is_end(units: List[Unit], i: int):
        return bool(
            # 1. End of List
            i + 1 >= len(units) or
            
            # 2. Clause
            units[i+1].label_has([
                Unit.COLON,
                Unit.COLON_BREAK,
                Unit.I_CLAUSE,
                Unit.D_CLAUSE,
                Unit.P_PHRASE,
                Unit.SEP_PUNCT,
                Unit.SEP_PUNCT_AND_OR,
                Unit.SEP_PUNCT_CONJ
            ]) or
            
            # 3. Noun
            PrepositionalPhrase.is_last_noun(units, i)
        )



    @staticmethod
    def identify(units: List[Unit], verbose=False) -> List[Unit]:
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')
        
        i = 0
        while i < len(units):
            if verbose:
                print(f"[i={i}|PoS={units[i].span()[0].pos_}{'' if i + 1 >= len(units) else f'''|nUnit={units[i+1].span()}'''}{str('' if len(units[i].span()) != 2 else f'|nPoS={units[i].span()[1].pos_}')}] Unit: '{units[i].text()}'")
                print(f'Units: {[unit.text() for unit in units]}')
            

            # Skip
            is_long = units[i].size() != 1
            is_not_to = units[i].lower() != "to"
            is_not_adp = units[i].start().pos_ != "ADP"
            
            if (is_long or is_not_adp) and is_not_to:
                if verbose:
                    print(f'\t[is_long={is_long}|is_not_to={is_not_to}|is_not_adp={is_not_adp}] Skipped\n\n')
                i += 1
                continue
            
            # If we've reached here, it's because
            # we have identified the current unit
            # as the start of a prepositional phrase.

            # Create Clause
            units[i].labels.add(Unit.P_PHRASE)
            
            # If we have seen a noun and run into brackets or
            # quotes, we exit early -- even if we haven't run
            # into an end.
            # My question is, wouldn't is_end account for the
            # bracket or quotation, since those characters/tokens
            # are left in the unit?
            # I'm going to comment it out to see.
            # noun_seen = False
            while not PrepositionalPhrase.is_end(units, i+1):
                # noun_seen = noun_seen or units[i+1].start().pos_ in [
                #     "NOUN", 
                #     "PROPN", 
                #     "PRON"
                # ]

                # Add Child
                if units[i+1].label_has([Unit.BRACKETS, Unit.QUOTE]):
                    # if noun_seen:
                    #     break
                    units[i].children.append(units[i+1])
                
                units[i].r = units[i+1].r
                units.pop(i+1)
            
            # This block determines whether we should
            # add the end to the clause's tokens.
            if bool(
                    units[i+1].size() == 1 and 
                    units[i+1].span()[0].pos_ in ["NOUN", "PROPN", "PRON", "ADJ", "VERB"] and 
                    units[i+1].lower() not in Dependent_Clauses.RELATIVE_NOUNS
                ):
                units[i].r = units[i+1].r
                units.pop(i+1)
            
            i += 1

            if verbose:
                print()
                print()
        
        if verbose:
            print(f'Out: {[unit.text() for unit in units]}\n\n')
        
        return units   
    

    
    def __new__(cls, units: List[Unit], verbose=False):
        return PrepositionalPhrase.identify(units, verbose)