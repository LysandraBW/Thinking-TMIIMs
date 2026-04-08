class Dependent_Clauses:
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
    

    # def __init__(self, doc: ExtendedDoc, units: List[Unit]) -> None:
    #     super().__init__(doc, units)
    #     self.separator = None


    # def end(self, i: int):
    #     if i >= len(self.units):
    #         return True

    #     # Here, we check if the unit after
    #     # is a clause. As we don't combine two
    #     # clauses, we must end here if that is
    #     # the case.
    #     if bool(
    #         i + 1 < len(self.units) and 
    #         self.units[i+1].label_has([
    #             Unit.COLON, 
    #             Unit.COLON_BREAK,
    #             Unit.I_CLAUSE,
    #             Unit.D_CLAUSE
    #         ])
    #     ):
    #         return True

    #     return bool(
    #         self.units[i].lower()[0] == self.separator or
    #         self.units[i].lower() in Dependent_Clauses.RELATIVE_NOUNS or
    #         self.units[i].start().pos_ in ["SCONJ"]
    #     )


    # def identify(self, separator: str):
    #     self.separator = separator
        
    #     i = 0
        
    #     while i < len(self.units):
    #         # Skip
    #         if self.units[i].label_has([
    #             Unit.COLON,
    #             Unit.COLON_BREAK,
    #             Unit.I_CLAUSE, 
    #             Unit.D_CLAUSE, 
    #             Unit.P_PHRASE
    #         ]):
    #             i += 1
    #             continue

    #         # Indicators of Dependent Clause
    #         rel = self.units[i].lower() in Dependent_Clauses.RELATIVE_NOUNS
    #         sub = self.units[i].start().pos_ == "SCONJ"
            
    #         if not sub and not rel:
    #             i += 1
    #             continue

    #         # Create Clause
    #         self.units[i].labels.add(Unit.D_CLAUSE)
    #         while not self.end(i+1):
    #             self.units[i].r = self.units[i+1].r

    #             # Add Child
    #             if self.units[i+1].label_has([Unit.BRACKETS, Unit.QUOTE, Unit.P_PHRASE]):
    #                 self.units[i].children.append(self.units[i+1])
                
    #             self.units.pop(i+1)

    #         i += 1
        
    #     return self.units