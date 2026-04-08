from typing import List, Set
from more_itertools import collapse
from ExtendedDoc import *

class Unit:
    LIST = 1
    ITEM = 2
    QUOTE = 3
    SEP_PUNCT = 4
    SEP_PUNCT_CCONJ = 5
    SEP_PUNCT_SCONJ = 15
    SEP_PUNCT_AND_OR = 6
    COLON = 7
    COLON_BREAK = 8
    I_CLAUSE = 9
    D_CLAUSE = 10
    P_PHRASE = 11
    BRACKETS = 12
    FRAGMENT = 13
    SEP_CCONJ = 14
    SEP_SCONJ = 16


    def __init__(self, doc: ExtendedDoc, *, labels: int | List[int] | None = None, l: int | None = None, r: int | None =None, children: List["Unit"] | None = None) -> None:
        self.doc = doc
        self.labels: Set[int] = set() if not labels else set([labels]) if not isinstance(labels, list) else set(labels)
        self.l = -1 if l is None else l
        self.r = -1 if r is None else r
        self.children = children or []
    
    
    def size(self):
        return self.r - self.l + 1


    def span(self):
        return self.doc.doc[self.l:self.r+1]


    def text(self):
        span = self.span()
        return self.doc.text[span.start_char:span.end_char]
    

    def lower(self):
        span = self.span()
        return self.doc.text_lower[span.start_char:span.end_char]


    def start(self):
        return self.doc.doc[self.l]


    def end(self):
        return self.doc.doc[self.r]


    def sent_start(self):
        return self.doc.token_to_sent[self.l].start


    def label_has(self, labels):
        return self.labels.intersection(labels)


    @staticmethod
    def tokens(*, unit: "Unit | None" = None, units: List["Unit"] | None = None) -> List[Token] | None:
        if units:
            tokens = collapse(list(unit.span()) for unit in units)
            tokens = sorted(tokens, key=lambda token: token.i)
            return tokens
        elif unit:
            tokens = list(unit.span())
            return tokens
        else:
            return None


    @staticmethod
    def is_conjunction(token):
        return token.lower_ in ["and", "or"]


    @staticmethod
    def same_speech(speech_1, speech_2):
        nouns = ["NOUN", "PRON", "PROPN"]
        if speech_1 in nouns and speech_2 in nouns:
            return True
        return speech_1 == speech_2


    @staticmethod
    def same_speech_list(speech_1, speeches_2):
        for speech_2 in speeches_2:
            if Unit.same_speech(speech_1, speech_2):
                return True
        return False
    

    @property
    def labels_(self):
        labels = []
        if Unit.LIST in self.labels:
            labels.append("List")
        if Unit.ITEM in self.labels:
            labels.append("Item")
        if Unit.QUOTE in self.labels:
            labels.append("Quote")
        if Unit.SEP_PUNCT in self.labels:
            labels.append("Punctuation")
        if Unit.SEP_PUNCT_CCONJ in self.labels:
            labels.append("Punctuation Followed by Coordinating Conjunction")
        if Unit.SEP_PUNCT_SCONJ in self.labels:
            labels.append("Punctuation Followed by Subordinating Conjunction")
        if Unit.SEP_PUNCT_AND_OR in self.labels:
            labels.append("Puncutation Followed by And or Or")
        if Unit.COLON in self.labels:
            labels.append("Colon")
        if Unit.COLON_BREAK in self.labels:
            labels.append("Colon Break")
        if Unit.I_CLAUSE in self.labels:
            labels.append("Independent Clause")
        if Unit.D_CLAUSE in self.labels:
            labels.append("Dependent Clause")
        if Unit.P_PHRASE in self.labels:
            labels.append("Prepositional Phrase")
        if Unit.BRACKETS in self.labels:
            labels.append("Brackets")
        if Unit.FRAGMENT in self.labels:
            labels.append("Fragment")
        if Unit.SEP_CCONJ in self.labels:
            labels.append("Coordinating Conjunction")
        if Unit.SEP_SCONJ in self.labels:
            labels.append("Subordinating Conjunction")
        return ", ".join(labels) or "None"
    

    
    def __str__(self):
        return self.text()
    