from spacy.tokens import Token, Doc, Span

class ExtendedDoc:
    def __init__(self, doc: Doc) -> None:
        self.doc = doc
        self.text = doc.text
        self.text_lower = self.text.lower()
        self.sents = list(doc.sents)
        self.token_to_sent = {token.i: sent for sent in self.sents for token in sent}