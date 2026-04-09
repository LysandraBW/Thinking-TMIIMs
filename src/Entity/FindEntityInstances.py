from typing import Any, Set, Tuple
from spacy.tokens import Span
from spacy.util import filter_spans
from .ExtendedDoc import ExtendedDoc
from .text import *
from .names import *
from .tokens import *
from .inflections import *


class FindEntityInstances:
    def __init__(self, doc: ExtendedDoc) -> None:
        self.doc = doc
    
    

    def search_strings_tn(self) -> Set[str]:
        search_strings = set()
        
        for ent in self.doc.doc.ents:
            # We break the text into texts if it has a parenthetical.
            # So, 'cat (dog)' becomes ['cat', 'dog'].
            texts = [clean_text(text) for text in break_text(self.doc.text_lower[ent.start_char:ent.end_char])]
            search_strings.update(texts)

            for text in texts:
                if not text or re.search(r"[^\w\s.-]", text):
                    continue
                
                # Add Base of Text (Ending Noun)
                b_text = text.split()[-1]
                if not re.match(r"\w\$.", b_text):
                    search_strings.add(b_text)

                # Add Singular Version
                s_text = singular(text)
                if s_text:
                    search_strings.add(s_text)

                # Add Plural Version
                p_text = plural(text)
                if p_text:
                    search_strings.add(p_text)
        
        return search_strings



    def find_matches_tn(self, search_strings: Set[str]) -> List[Tuple[int, int]]:
        all_matches = []
        for search in search_strings:
            matches = re.finditer(re.escape(search), self.doc.text_lower, re.IGNORECASE)
            all_matches.extend((match.start(), match.end()) for match in matches)
        return all_matches



    def find_matches_db(self) -> List[Tuple[int, int]]:
        matches = []
        for r_i, data in all_names.iter(self.doc.text_lower):
            key = data['key']
            matches.append((r_i - len(key) + 1, r_i + 1))
        return matches



    def find_ents_from_matches(self, matches: List[Tuple[int, int]]):
        spans = []
        
        for l_index, r_index in matches:
            # The full word must match, not just a substring inside of it.
            # So, if the species we're looking for is "ant", only "ant"
            # will match -- not "pants" or "antebellum". Therefore, the
            # characters to the left and right of the matched string cannot
            # be letters.
            match = self.doc.text[l_index:r_index]
            match_lower = self.doc.text_lower[l_index:r_index]

            l_bound = l_index == 0 or is_boundary(self.doc.text_lower[l_index-1])
            r_bound = r_index == len(self.doc.text_lower) or is_boundary(self.doc.text_lower[r_index])
            
            if not l_bound or not r_bound or r_index - l_index <= 1:
                continue
            
            # Check 1: No Bad Characters
            match = self.doc.text[l_index:r_index]
            if re.search(r"[^\w\s.-]", match):
                continue
            
            # Check 2: Correct Casing, if Scientific
            if data := all_names.get(match_lower, None):
                if data['label'] == 's' and not match[0].isupper():
                    continue
            
            span = self.doc.doc.char_span(l_index, r_index, alignment_mode="expand")
            if not span or not len(span):
                continue
            
            not_sent_start = span.sent.start != span.start

            # Check 3: Correct Casing and Types, Vernacular and Role
            if in_vernacular(match_lower) or in_roles(match_lower):
                if not any(token.pos_ == 'NOUN' for token in span):
                    continue

                if not_sent_start and span[0].pos_ == 'NOUN' and match[0].isupper():
                    continue
            
            # Check 4: Correct Casing, Scientific
            if data := all_names.get(match_lower, None):
                if not_sent_start and in_scientific(match_lower) in ['specificEpithet', 'intraspecificEpithet'] and match[0].isupper():
                    continue
            
            # Expand Species
            # Let's say there's a word like "squirrel". That's a bit ambiguous. 
            # Is it a brown squirrel, a bonobo? If the species is possibly missing
            # information (like an adjective to the left of it), we should expand
            # in order to get a full picture of the species.
            is_short = len(span) == 1 and span[0].pos_ == "NOUN"
            
            # Remove Outer Symbols
            # There are times where a species is identified with a parenthesis
            # nearby. Here, we remove that parenthesis (and any other symbols).

            span = contract_unit(
                self.doc.doc,
                il_unit=span.start, 
                ir_unit=span.end-1, 
                speech=["ADJ", "PROPN", "NOUN", "X"],
                include=True,
                verbose=False
            )

            if not span or not len(span):
                continue
            
            if is_short:
                span = expand_unit(
                    self.doc.doc,
                    il_unit=span.start, 
                    ir_unit=span.end-1,
                    il_boundary=0,
                    ir_boundary=len(self.doc.doc) - 1,
                    speech=["ADJ", "PROPN", "NOUN"],
                    literals=["-"],
                    include=True,
                    direction="LEFT",
                    verbose=False
                )

                if not span:
                    continue
                
                # Remove Outer Symbols (Again)
                # The previous expansion contains a literal.
                # There might not be a need for that literal.
                # To handle that case, we contract.
                span = contract_unit(
                    self.doc.doc,
                    il_unit=span.start,
                    ir_unit=span.end-1,
                    speech=["ADJ", "PROPN", "NOUN", "X"],
                    include=True,
                    verbose=False
                )

                if not span or not len(span):
                    continue
            
            # A species must have a noun or a
            # proper noun. This may help discard
            # bad results.
            noun_found = False
            for token in span:
                if token.pos_ in ["NOUN", "PROPN", "X"]:
                    noun_found = True
                    break
            
            if not noun_found:
                continue

            # The names I'd like to identify should
            # not have any numbers or odd characters.
            if re.search(r"[^\w\s.-]", match):
                continue
            
            # Added
            spans.append(span)

        spans = filter_spans(spans)
        return spans



    def find_ents_tn(self) -> List[Span]:
        searches = self.search_strings_tn()
        matches = self.find_matches_tn(searches)
        return self.find_ents_from_matches(matches)



    def find_ents_db(self) -> List[Span]:
        matches = self.find_matches_db()
        return self.find_ents_from_matches(matches)
    


    def find(self, *, verbose=False) -> List[Span]:
        ents_tn = self.find_ents_tn()

        if verbose:
            print('TN Entities:', ents_tn)
        
        ents_db = self.find_ents_db()

        if verbose:
            print('DB Entities:', ents_db)
        
        ents = filter_spans(ents_tn + ents_db)

        if not ents:
            return []
        
        # Merge Consecutive Span-Intervals
        ents.sort(key=lambda ent: ent.start)
        merged = ents and [ents[0]]
        for curr in ents[1:]:
            prev = merged[-1]
            
            if prev.end >= curr.start:
                end = max(prev.end, curr.end)
                merged[-1] = self.doc.doc[prev.start:end]
            else:
                merged.append(curr)
        
        if verbose:
            print('Found Entities:', merged)
        
        return merged


    def __call__(self, *, verbose=False) -> Any:
        return self.find(verbose=verbose)