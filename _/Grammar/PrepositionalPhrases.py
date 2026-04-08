from Identify import *
from _.ExtendedDoc import ExtendedDoc
from _.Grammar.Unit import ExtendedDoc, List, Unit
from DependentClause import *

class Prepositional_Phrases(Identify):
    def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
        super().__init__(doc, units)
        self.separator = None


    # A prepositional phrase is typically ended by a noun.
    # Therefore, when we run into a noun, we end the phrase.
    # We must also check that it is the last of the first noun(s)
    # we encounter.
    def last_noun(self, i: int):
        if bool(
            # 1. End
            i >= len(self.units) or 
            
            # 2. Noun
            self.units[i].start().pos_ not in [
                "NOUN", 
                "PROPN", 
                "PRON"
            ]
        ):
            return False

        return bool(
            i + 1 >= len(self.units) or 
            (
                self.units[i+1].size() == 1 and 
                (
                    self.units[i+1].start().pos_ not in [
                        "NOUN", 
                        "PROPN", 
                        "PRON", 
                        "PART"
                    ] or
                    self.units[i+1].start().lower_ in Dependent_Clauses.RELATIVE_NOUNS
                )
            )
        )
    

    def end(self, i: int):
        return bool(
            # 1. End of List
            i + 1 >= len(self.units) or
            
            # 2. Clause
            self.units[i+1].label_has([
                Unit.COLON,
                Unit.COLON_BREAK,
                Unit.I_CLAUSE,
                Unit.D_CLAUSE,
                Unit.P_PHRASE,
                Unit.BREAK,
                Unit.AND_OR_END,
                Unit.END
            ]) or
            
            # 3. Noun
            self.last_noun(i)
        )

    
    def identify(self):    
        i = 0
        
        while i < len(self.units):
            # Skip
            is_comp = self.units[i].size() != 1
            is_non_adp = self.units[i].start().pos_ != "ADP"
            is_not_to = self.units[i].lower() != "to"
            
            if (is_comp or is_non_adp) and is_not_to:
                i += 1
                continue

            # Create Clause
            self.units[i].labels.add(Unit.P_PHRASE)
            noun_seen = False
            
            while not self.end(i+1):
                noun_seen = noun_seen or self.units[i+1].start().pos_ in [
                    "NOUN", 
                    "PROPN", 
                    "PRON"
                ]
                # Add Child
                if self.units[i+1].label_has([Unit.BRACKETS, Unit.QUOTE]):
                    if noun_seen:
                        break
                    self.units[i].children.append(self.units[i+1])
                
                self.units[i].r = self.units[i+1].r
                self.units.pop(i+1)

            if bool(
                    self.units[i+1].size() == 1 and 
                    self.units[i+1].span()[0].pos_ in ["NOUN", "PROPN", "PRON", "ADJ", "VERB"] and 
                    self.units[i+1].lower() not in Dependent_Clauses.RELATIVE_NOUNS
                ):
                self.units[i].r = self.units[i+1].r
                self.units.pop(i+1)
            
            i += 1
        
        return self.units   