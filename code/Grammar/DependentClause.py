from .Unit import Unit
from typing import List

class DependentClause:
    RELATIVE_NOUNS = [
        "who",
        "whom",
        "which",
        "what",
        "that",
        "whose",
        "whomever",
        "whoever",
        "whichever",
        "whatever"
    ]
    


    @staticmethod
    def is_last_noun(units: List[Unit], i: int, verbose=False):
        if i >= len(units):
            return False
        
        if verbose:
            print(f"\t\tChecking Unit '{units[i].text()}'")
            print(f"\t\t\tUnit Starting PoS='{units[i].start().pos_}'")
                
        if units[i].start().pos_ not in ["NOUN", "PROPN", "PRON"]:
            return False

        return bool(
            i + 1 >= len(units) or 
            (
                units[i+1].size() == 1 and 
                (
                    units[i+1].start().pos_ not in ["NOUN", "PROPN","PART"] or
                    units[i+1].start().lower_ in DependentClause.RELATIVE_NOUNS
                )
            )
        )



    @staticmethod
    def is_end(units: List[Unit], i: int, separator: str, verb_seen: bool, noun_seen: bool, verbose=False):
        if i >= len(units):
            return True

        # Here, we check if the unit after
        # is a clause. As we don't combine two
        # clauses, we must end here if that is
        # the case.
        if bool(
            i + 1 < len(units) and 
            units[i+1].label_has([Unit.COLON, Unit.COLON_BREAK, Unit.I_CLAUSE, Unit.D_CLAUSE])
        ):
            if verbose:
                print(f"\tChecking if '{units[i]}' is End")
                print('\t\ttNext is Colon/ColonBreak/I-Clause/D-Clause')
            return True

        lower = units[i].lower()
        speech = units[i].start().pos_

        # Conditions
        cond_1 = speech == "SCONJ"
        cond_2 = lower[0] == separator
        cond_3 = lower in DependentClause.RELATIVE_NOUNS
        cond_4 = noun_seen and speech == 'VERB' and not list(units[i].start().rights)
        cond_5 = verb_seen and DependentClause.is_last_noun(units, i, verbose=True)
        cond_6 = units[i].label_has([Unit.SEP_SCONJ, Unit.SEP_PUNCT_SCONJ])

        if verbose:
            print(f"\tChecking if '{units[i]}' is End")
            print(f'\t\tCond. 1: {cond_1}')
            print(f'\t\tCond. 2: {cond_2}')
            print(f'\t\tCond. 3: {cond_3}')
            print(f'\t\tCond. 4: {cond_4}')
            print(f'\t\tCond. 5: {cond_5}')
            print(f'\t\tCond. 6: {cond_6}\n')
        
        return cond_1 or cond_2 or cond_3 or cond_4 or cond_5 or cond_6



    @staticmethod
    def identify(units: List[Unit], separator: str, verbose=False):
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')

        i = 0
        while i < len(units):
            if verbose:
                print(f"[i={i}|PoS={units[i].span()[0].pos_}{'' if i + 1 >= len(units) else f'''|nUnit={units[i+1].span()}'''}{str('' if len(units[i].span()) != 2 else f'|nPoS={units[i].span()[1].pos_}')}] Unit: '{units[i].text()}'")
                print(f'Units: {[unit.text() for unit in units]}')
            
            # Skip
            if units[i].label_has([Unit.COLON, Unit.COLON_BREAK, Unit.I_CLAUSE, Unit.D_CLAUSE, Unit.P_PHRASE]):
                if verbose:
                    print('\tSkip 1\n\n')
                
                i += 1
                continue
            
            # Skip if Not Dependent Clause
            if (
                units[i].lower() not in DependentClause.RELATIVE_NOUNS and 
                units[i].start().pos_ != "SCONJ" and
                not units[i].label_has([Unit.SEP_SCONJ, Unit.SEP_PUNCT_SCONJ])
            ):
                if verbose:
                    print('\tSkip 2\n\n')

                i += 1
                continue

            # Create Clause
            units[i].labels.add(Unit.D_CLAUSE)

            verb_seen = False
            noun_seen = False
            while not DependentClause.is_end(units, i + 1, separator=separator, verb_seen=verb_seen, noun_seen=noun_seen, verbose=verbose):
                if units[i+1].start().pos_ == 'VERB':
                    verb_seen = True
                
                if units[i+1].start().pos_ in ['NOUN', 'PRON', 'PROPN']:
                    noun_seen = True
                
                units[i].r = units[i+1].r

                # Add Child
                if units[i+1].label_has([Unit.BRACKETS, Unit.QUOTE, Unit.P_PHRASE]):
                    units[i].children.append(units[i+1])
                
                units.pop(i+1)

            # This block determines whether we should
            # add the end to the clause's tokens.
            if bool(
                    i + 1 < len(units) and 
                    units[i+1].size() == 1 and 
                    units[i+1].span()[0].pos_ in ["NOUN", "PROPN", "PRON", "ADJ", "VERB"] and 
                    units[i+1].lower() not in DependentClause.RELATIVE_NOUNS
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
    


    def __new__(cls, units: List[Unit], separator: str, verbose=False):
        return DependentClause.identify(units, separator=separator, verbose=verbose)