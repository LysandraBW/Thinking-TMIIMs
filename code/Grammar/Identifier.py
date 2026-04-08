from .Unit import *
# from Brackets import *
# from Colons import *
# from DependentClause import *
# from IndependentClause import *
# from List import *
# from PrepositionalPhrases import *
# from Quotes import *
# from Separators import *
# from ExtendedDoc import *
# from typing import Dict, Tuple


class Units:
    # @staticmethod
    # def identify(doc: ExtendedDoc):
    #     unit_map = Identifier.load_unit_map_doc(doc)
    #     return unit_map

    

    # @staticmethod
    # def load_unit_map_doc(doc: ExtendedDoc) -> Dict[Tuple[int, int], Unit]:
    #     unit_map = {}
        
    #     for sent in doc.sents:
    #         sent_tokens = list(sent)
    #         sent_unit_map = Identifier.load_units(doc, sent_tokens)
    #         unit_map.update(sent_unit_map)
        
    #     return unit_map



    # @staticmethod
    # def load_unit_map(unit) -> Dict[Tuple[int, int], Unit]:
    #     unit_map = {}
    #     if unit.l != -1:
    #         unit_map[(unit.l, unit.r)] = unit

    #     # Add Children
    #     for child in unit.children:
    #         child_ent_map = Identifier.load_unit_map(child)
    #         unit_map.update(child_ent_map)
        
    #     return unit_map
    


    @staticmethod
    def initialize_units(doc: ExtendedDoc, span: Span) -> List[Unit]:
        units = []
        for token in span:
            unit = Unit( 
                doc=doc,
                l=token.i, 
                r=token.i
            )
            units.append(unit)
        return units


    
    # @staticmethod
    # def load_units(doc: ExtendedDoc, tokens: List[Token], load_clauses: bool = True, load_enclosures: bool = True):
    #     units = []
    #     for token in tokens:
    #         unit = Unit(
    #             doc, 
    #             l=token.i, 
    #             r=token.i
    #         )
    #         units.append(unit)

    #     # Enclosures
    #     # These are extracted first due to their
    #     # simplicity.
    #     if load_enclosures:
    #         units = Quotes(doc, units).identify()
    #         units = IdentifyBrackets(doc, units).identify()

    #     # These class of units can be put inside a larger
    #     # unit (which makes it hard to know where they are
    #     # later on). Thus, they're stored in this variable for
    #     # later use in the list identification.
    #     enclosures = []
    #     for unit in units:
    #         if unit.label_has([Unit.BRACKETS, Unit.QUOTE]):
    #             enclosures.append(unit)
        
    #     # Find Partioning Separator
    #     # If a sentence uses the below structure:
    #     # "When ... , .... ; therefore, ... ."
    #     # There is a hierarchical structure between
    #     # the semicolons and commas where the former
    #     # nests the latter. Therefore, we find the
    #     # higher-ranking separator (which would be
    #     # the semicolon, if there's any) to use for
    #     # further separation.
    #     sep = ","
    #     for unit in units:
    #         if ";" == unit.lower()[0]:
    #             sep = ";"
    #             break

    #     # Separators and Colons
    #     # The separators here also include conjunctions and
    #     # the use of both conjunctions and punctuation.
    #     units = Separators(doc, units).identify()

    #     if load_enclosures:
    #         units = Colons(doc, units).identify()

    #     if load_clauses:
    #         units = Prepositional_Phrases(doc, units).identify()
    #         units = Dependent_Clauses(doc, units).identify(sep)
    #         units = Independent_Clauses(doc, units).identify([Unit.END])
        
    #     units = Lists(doc, units, enclosures).identify(sep)
        
    #     # There is some overlap between lists and independent
    #     # clauses because they both can use ", [AND/OR]", but
    #     # after the lists are identified, we can assume the
    #     # remaining ", [AND/OR]" are parts of independent 
    #     # clauses.
    #     if load_clauses:
    #         units = Independent_Clauses(doc, units).identify([Unit.AND_OR_END])

    #     # Merge Ungrouped Entities
    #     i = 0
    #     while i < len(units):
    #         if not units[i].labels:
    #             while i + 1 < len(units) and (not units[i+1].lower() in string.punctuation and (not units[i+1].labels)):
    #                 units.pop(i+1)
    #                 units[i].r += 1
    #             units[i].labels = {Unit.FRAGMENT}
    #         i += 1

    #     # Remove Fragments
    #     # If we're already parsing a fragment
    #     # (indicated by load_clauses = False), we
    #     # should not add meaningless, duplicate fragments.
    #     if not load_clauses or not load_enclosures:
    #         units = [ent for ent in units if ent.labels != {Unit.FRAGMENT}]
        
    #     # Map Units
    #     # This map lists the units, the units' children,
    #     # those childrens' children, and so on, in a convenient
    #     # manner, arguably. It all starts with one unit, which
    #     # we have as the "parent". It encapsulates the units
    #     # we want to list.
    #     parent = Unit(doc, l=-1, r=-1, children=units)
    #     parent_unit_map = Identifier.load_unit_map(parent)
        
    #     for unit in set(*units, *enclosures):
    #         unit_tokens = [*unit.span()]

    #         # Minimum Size Not Met
    #         if not (2 < len(unit_tokens) < len(tokens)):
    #             continue
            
    #         # Loading Not Needed
    #         if not unit.label_has([Unit.I_CLAUSE, Unit.D_CLAUSE, Unit.FRAGMENT, Unit.COLON, Unit.BRACKETS, Unit.QUOTE]):
    #             continue
            
    #         load_clauses = not unit.label_has([
    #             Unit.I_CLAUSE, 
    #             Unit.D_CLAUSE, 
    #             Unit.FRAGMENT
    #         ])
            
    #         unit_map = Identifier.load_units(doc, unit_tokens, load_clauses=load_clauses, load_enclosures=False)
            
    #         # Add Unit's Items to Parent's Unit Map
    #         for k, v in unit_map.items():
    #             parent_unit_map[k] = v
        
    #     return parent_unit_map



    # @staticmethod
    # def units_at_i(unit_map: Dict[Tuple[int, int], Unit], i: int):
    #     units = []
    #     for k, v in unit_map.items():
    #         if k[0] <= i <= k[1]:
    #             units.append(v)
    #     return units



    # @staticmethod
    # def collapse_units(doc: ExtendedDoc, unit_map: Dict[Tuple[int, int], Unit], labels: List[int] = [Unit.LIST]):
    #     unit_bounds = [k for k, v in unit_map.items() if not v.label_has([Unit.ITEM])]
    #     distinct_unit_bounds = Identifier.distinct_bounds(unit_bounds, larger=False)
        
    #     units = [unit[1] for unit in unit_map.items() if unit[0] in distinct_unit_bounds]
    #     units = sorted(units, key=lambda unit: unit.l)
        
    #     tokens: List[Token] = []
    #     units_tokens: List[List[Token]] = []
        
    #     i = 0
    #     while i < len(units):
    #         curr = units[i]
    #         tokens.extend([*curr.span()])

    #         next = None if i + 1 >= len(units) else units[i+1]

    #         if next and next.label_has(labels):
    #             i += 1
    #             continue

    #         if units_tokens:
    #             l = units_tokens[-1][-1].i
    #             r = tokens[0].i

    #             if r - l > 1:
    #                 units_tokens[-1].extend(list(doc.doc[l+1:r]))
            
    #         units_tokens.append(tokens)
    #         tokens = []
            
    #         i += 1

    #     if tokens:
    #         units_tokens.append(tokens)

    #     return units_tokens



    # @staticmethod
    # def a_contains_b(a: Tuple[int, int], b: Tuple[int, int]):
    #     return (a[0] <= b[0] < a[1] and a[0] <= b[1] < a[1]) or (a[0] < b[0] <= a[1] and a[0] < b[1] <= a[1])



    # @staticmethod
    # def a_overlaps_b(a: Tuple[int, int], b: Tuple[int, int]):
    #     return a[0] <= b[0] <= a[1] or a[0] <= b[1] <= a[1]



    # @staticmethod
    # def collapse_tokens_by_unit(doc, units):
    #     # Split Tokens
    #     split_tokens = []
    #     tokens = [] # Running List of Tokens
        
    #     i = 0
    #     num_tokens = len(doc)
        
    #     while i < num_tokens:
    #         token = doc[i]

    #         # Case 1: End of Sentence (.)
    #         end_of_sentence_1 = token.i == token.sent.end - 1 and token.pos_ == "PUNCT"
    #         end_of_sentence_2 = i + 1 < num_tokens and doc[i+1].sent.start != token.sent.start

    #         if end_of_sentence_1 or end_of_sentence_2:
    #             if tokens:
    #                 split_tokens.append(tokens)
    #             tokens = []
            

    #         # Case 2: Comma (,), Semicolon (;), Colon (:), Conjunction (AND/OR)
    #         elif token.lower_[0] in ",;:" or token.pos_ == "CCONJ":
    #             t_units = units.units_at_i(token.i)
    #             unit_lists = [unit for unit in t_units if unit.label_has([Unit.LIST])]

    #             if unit_lists:
    #                 tokens.append(token)
    #                 i += 1
    #             else:
    #                 unit_breaks = [unit for unit in t_units if unit.label_ in [Unit.AND_OR_END, Unit.END, Unit.BREAK, Unit.COLON_BREAK, Unit.CONJ]]
    #                 if tokens:
    #                     split_tokens.append(tokens)
                    
    #                 tokens = []
        
    #                 if unit_breaks:
    #                     unit = unit_breaks[0]
    #                     i += unit.r - unit.l + 1
    #                 else:
    #                     i += 1
                
    #             continue
                
            
    #         # Case 3: Regular Token
    #         else:
    #             t_units = units.units_at_i(token.i)

    #             split = False
    #             cont_loop = False
                
    #             for unit in t_units:
    #                 if unit.label_has([Unit.I_CLAUSE, Unit.D_CLAUSE]) and token.i == unit.l:
    #                     if tokens:
    #                         split_tokens.append(tokens)
    #                     tokens = [token]
    #                     split = True
    #                 elif unit.label_has([Unit.BRACKETS]):
    #                     i += unit.r - unit.l + 1
    #                     split_tokens.append([*unit.span()])
    #                     split = True
    #                     cont_loop = True
    #                 elif unit.label_has([Unit.P_PHRASE]) and (unit.start().pos_ == "SCONJ" or not tokens):
    #                     i += unit.r - unit.l + 1
    #                     split_tokens.append([*unit.span()])
    #                     split = True
    #                     cont_loop = True
                
    #             # We can't continue the while-loop
    #             # from the for-loop.
    #             if cont_loop:
    #                 continue

    #             if not split:
    #                 tokens.append(token)
            
    #         i += 1
        

    #     if tokens:
    #         split_tokens.append(tokens)


    #     return split_tokens
    


    # @staticmethod
    # def distinct_bounds(bounds: List[Tuple[int, int]], larger=True):
    #     dounds = []
        
    #     for bound in bounds:
    #         impure = False
            
    #         for i, dound in enumerate(dounds):    
    #             surround = Identifier.a_contains_b(bound, dound)
    #             contains = Identifier.a_contains_b(dound, bound)
    #             overlaps = Identifier.a_overlaps_b(bound, dound)

    #             impure = surround or contains or overlaps

    #             if overlaps:
    #                 d_length = dound[1] - dound[0]
    #                 b_length = bound[1] - bound[0]
    #                 dounds[i] = dound if d_length >= b_length else bound
    #             elif larger:
    #                 if surround:
    #                     dounds[i] = bound
    #                 elif contains:
    #                     dounds[i] = dound
    #             else:
    #                 if surround:
    #                     dounds[i] = dound
    #                 elif contains:
    #                     dounds[i] = bound

    #         if not impure:
    #             dounds.append(bound)

        
    #     return list(set(dounds))