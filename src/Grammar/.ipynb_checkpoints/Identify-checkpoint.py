import string
from typing import Dict, Tuple
from .Unit import *
from .Bracket import *
from .DependentClause import *
from .IndependentClause import *
from .Lists import *
from .Colon import *
from .PrepositionalPhrase import *
from .Quote import *
from .Separator import *
from Entity.ExtendedDoc import *


class Identify:
    @staticmethod
    def identify(doc: ExtendedDoc, verbose=False):
        unit_map = Identify.load_doc(doc, verbose=verbose)
        return unit_map


    def __new__(cls, doc: ExtendedDoc, verbose=False):
        return Identify.identify(doc, verbose=verbose)
    


    @staticmethod
    def load_doc(doc: ExtendedDoc, verbose=False) -> Dict[Tuple[int, int], Unit]:
        unit_map = {}
        
        for sent in doc.sents:
            sent_tokens = list(sent)
            sent_unit_map = Identify.load_units(doc, sent_tokens, verbose=verbose)
            unit_map.update(sent_unit_map)
        
        return unit_map



    @staticmethod
    def load_unit(unit) -> Dict[Tuple[int, int], Unit]:
        unit_map = {}
        if unit.l != -1:
            unit_map[(unit.l, unit.r)] = unit

        # Add Children
        for child in unit.children:
            child_ent_map = Identify.load_unit(child)
            unit_map.update(child_ent_map)
        
        return unit_map
    


    @staticmethod
    def init_units(doc: ExtendedDoc, span: Span) -> List[Unit]:
        units = []
        for token in span:
            unit = Unit( 
                doc=doc,
                l=token.i, 
                r=token.i
            )
            units.append(unit)
        return units


    
    @staticmethod
    def load_units(doc: ExtendedDoc, tokens: List[Token], load_clauses: bool = True, load_enclosures: bool = True, verbose: bool = False):
        units = []
        for token in tokens:
            unit = Unit(
                doc, 
                l=token.i, 
                r=token.i
            )
            units.append(unit)
        
        if verbose:
            print(f'In: {[unit.text() for unit in units]}')
        
        # Enclosures
        # These are extracted first due to their
        # simplicity.
        if load_enclosures:
            units = Quote(units)
            units = Bracket(units)

            if verbose:
                print(f'1. Enclosures: {[unit.text() for unit in units]}')

        # These class of units can be put inside a larger
        # unit (which makes it hard to know where they are
        # later on). Thus, they're stored in this variable for
        # later use in the list identification.
        enclosed = []
        for unit in units:
            if unit.label_has([Unit.BRACKETS, Unit.QUOTE]):
                enclosed.append(unit)
        
        if verbose:
            print(f'\tEnclosed: {[unit.text() for unit in enclosed]}')

        # Find Partioning Separator
        # If a sentence uses the below structure:
        # "When ... , .... ; therefore, ... ."
        # There is a hierarchical structure between
        # the semicolons and commas where the former
        # nests the latter. Therefore, we find the
        # higher-ranking separator (which would be
        # the semicolon, if there's any) to use for
        # further separation.
        sep = ","
        for unit in units:
            if ";" == unit.lower()[0]:
                sep = ";"
                break

        # Separators and Colons
        # The separators here also include conjunctions and
        # the use of both conjunctions and punctuation.
        units = Separator(units)

        if verbose:
            print(f'2. Separators: {[unit.text() for unit in units]}')
        
        if load_enclosures:
            units = Colon(units)

            if verbose:
                print(f'3. Colons: {[unit.text() for unit in units]}')

        # I've moved this up here, because shouldn't a
        # clause know when a noun is a list?
        units = Lists(units, separator=sep, enclosed=enclosed)
        if verbose:
            print(f'7. Lists: {[unit.text() for unit in units]}')
        

        if load_clauses:
            units = PrepositionalPhrase(units, verbose=False)
            if verbose:
                print(f'4. Prepositional Phrases: {[unit.text() for unit in units]}')

            units = DependentClause(units, separator=sep)
            if verbose:
                print(f'5. Dependent Clauses: {[unit.text() for unit in units]}')

            units = IndependentClause(units, delimiters=[Unit.SEP_PUNCT_CCONJ, Unit.SEP_PUNCT_SCONJ, Unit.SEP_CCONJ, Unit.SEP_SCONJ, Unit.SEP_PUNCT, Unit.SEP_PUNCT_AND_OR])
            if verbose:
                print(f'6. Independent Clauses: {[unit.text() for unit in units]}')
        
        # There is some overlap between lists and independent
        # clauses because they both can use ", [AND/OR]", but
        # after the lists are identified, we can assume the
        # remaining ", [AND/OR]" are parts of independent 
        # clauses.
        # Since the lists are already loaded, we can use whichever
        # delimiter.
        # if load_clauses:
        #     units = IndependentClause(units, delimiters=[Unit.SEP_PUNCT_CCONJ, Unit.SEP_PUNCT_SCONJ, Unit.SEP_CCONJ, Unit.SEP_SCONJ, Unit.SEP_PUNCT, Unit.SEP_PUNCT_AND_OR])
        #     if verbose:
        #         print(f'8. Independent Clauses: {[unit.text() for unit in units]}')

        # Merge Ungrouped Entities
        i = 0
        while i < len(units):
            if not units[i].labels:
                while i + 1 < len(units) and (not units[i+1].lower() in string.punctuation and (not units[i+1].labels)):
                    units.pop(i+1)
                    units[i].r += 1
                units[i].labels = {Unit.FRAGMENT}
            i += 1

        if verbose:
            print(f'9. Add Fragments: {[unit.text() for unit in units]}')
        
        # Remove Fragments
        # If we're already parsing a fragment
        # (indicated by load_clauses = False), we
        # should not add meaningless, duplicate fragments.
        if not load_clauses or not load_enclosures:
            units = [ent for ent in units if ent.labels != {Unit.FRAGMENT}]

            if verbose:
                print(f'10. Remove Fragments: {[unit.text() for unit in units]}')
        
        # Map Units
        # This map lists the units, the units' children,
        # those childrens' children, and so on, in a convenient
        # manner, arguably. It all starts with one unit, which
        # we have as the "parent". It encapsulates the units
        # we want to list.
        parent = Unit(doc, l=-1, r=-1, children=units)
        parent_unit_map = Identify.load_unit(parent)
        
        for unit in set([*units, *enclosed]):
            unit_tokens = [*unit.span()]

            # Minimum Size Not Met
            if not (2 < len(unit_tokens) < len(tokens)):
                continue
            
            # Loading Not Needed
            if not unit.label_has([Unit.I_CLAUSE, Unit.D_CLAUSE, Unit.FRAGMENT, Unit.COLON, Unit.BRACKETS, Unit.QUOTE]):
                continue
            
            load_clauses = not unit.label_has([
                Unit.I_CLAUSE, 
                Unit.D_CLAUSE, 
                Unit.FRAGMENT
            ])
            
            unit_map = Identify.load_units(doc, unit_tokens, load_clauses=load_clauses, load_enclosures=False, verbose=verbose)
            
            # Add Unit's Items to Parent's Unit Map
            for k, v in unit_map.items():
                parent_unit_map[k] = v
        
        return parent_unit_map



    @staticmethod
    def units_at_i(unit_map: Dict[Tuple[int, int], Unit], i: int) -> List[Unit]:
        units = []
        for k, v in unit_map.items():
            if k[0] <= i <= k[1]:
                units.append(v)
        return units
    


    @staticmethod
    def units_left_of_i(unit_map: Dict[Tuple[int, int], Unit], i: int, ignore: List[int] | None = None) -> Unit | None:
        units: List[Unit] = []
        for k, v in unit_map.items():
            if k[1] <= i:
                units.append(v)

        if ignore:
            units = [unit for unit in units if unit.has_label(*ignore)]
        
        units = sorted(units, key=lambda unit: unit.r, reverse=True)
        return units[0]

    

    @staticmethod
    def units_right_of_i(unit_map: Dict[Tuple[int, int], Unit], i: int, ignore: List[int] | None = None) -> Unit | None:
        units: List[Unit] = []
        for k, v in unit_map.items():
            if k[0] >= i:
                units.append(v)

        if ignore:
            units = [unit for unit in units if unit.has_label(*ignore)]
        
        units = sorted(units, key=lambda unit: unit.r)
        return units[0]
    


    @staticmethod
    def a_contains_b(a: Tuple[int, int], b: Tuple[int, int]):
        return (a[0] <= b[0] < a[1] and a[0] <= b[1] < a[1]) or (a[0] < b[0] <= a[1] and a[0] < b[1] <= a[1])



    @staticmethod
    def a_overlaps_b(a: Tuple[int, int], b: Tuple[int, int]):
        return a[0] <= b[0] <= a[1] or a[0] <= b[1] <= a[1]