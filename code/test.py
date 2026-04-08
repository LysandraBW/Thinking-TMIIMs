import spacy
import unittest
from ExtendedDoc import *
from Grammar import Bracket, Quote, Colon, Unit, Units, Separator

class TestGrammar(unittest.TestCase):
    nlp = spacy.load("en_core_web_sm")



    def test_brackets(self):
        tests = [
            {
                'input': 'The dog (his name was Bob) roared.',
                'output': ['The', 'dog', '(his name was Bob)', 'roared', '.']
            },
            {
                'input': '(Chapter 1) He walked up to the door.',
                'output': ['(Chapter 1)']
            },
            {
                'input': 'The dog {barked}',
                'output': ['The', 'dog', '{barked}']
            },
            {
                'input': '[The] (dog) {barked}',
                'output': ['[The]', '(dog)', '{barked}']
            },
            {
                'input': 'The dog {barked (but it sounded like a roar)}',
                'output': ['The', 'dog', '{barked (but it sounded like a roar)}']
            }
        ]

        for test in tests:
            doc = ExtendedDoc(self.nlp(test['input']))
            units = Units.initialize_units(doc, doc.sents[0])
            units = Bracket(units, verbose=True)
            self.assertEqual([unit.text() for unit in units], test['output'])



    def test_quotes(self):
        tests = [
            {
                'input': 'The dog\'s collar was red.',
                'output': ['The', 'dog', '\'s', 'collar', 'was', 'red', '.']
            },
            {
                'input': 'The \'dog\' had a red collar.',
                'output': ['The', '\'dog\'', 'had', 'a', 'red', 'collar', '.']
            },
            {
                'input': '"The \'dog\' had a red collar."',
                'output': ['"The \'dog\' had a red collar."']
            }
        ]

        for test in tests:
            doc = ExtendedDoc(self.nlp(test['input']))
            units = Units.initialize_units(doc, doc.sents[0])
            units = Quote(units, verbose=True)
            self.assertEqual([unit.text() for unit in units], test['output'])
    


    def test_colons(self):
        tests = [
            {
                'input': 'A B C D : 1 2 3 4',
                'output': ['A', 'B', 'C', 'D', ":", "1 2 3 4"]
            },
            {
                'input': 'A B C D 1 2 3 4:',
                'output': ['A', 'B', 'C', 'D', '1', '2', '3', '4', ':']
            },
            {
                'input': ':A B C D 1 2 3 4',
                'output': [':', 'A B C D 1 2 3 4']
            }
        ]

        for test in tests:
            doc = ExtendedDoc(self.nlp(test['input']))
            units = Units.initialize_units(doc, doc.sents[0])
            units = Colon(units, verbose=True)
            self.assertEqual([unit.text() for unit in units], test['output'])



    def test_separators(self):
        tests = [
            {
                'input': 'A, B, and C; but 1 2 3; it will hear you or see you',
                'output_text': ['A', ',', 'B', ', and', 'C', '; but', '1', '2', '3', ';', 'it', 'will', 'hear', 'you', 'or', 'see', 'you'],
                'output_tags': [None, Unit.SEP_PUNCT, None, Unit.SEP_PUNCT_AND_OR, None, Unit.SEP_PUNCT_CONJ, None, None, None, Unit.SEP_PUNCT, None, None, None, None, Unit.SEP_CONJ, None, None]
            }
        ]

        for test in tests:
            doc = ExtendedDoc(self.nlp(test['input']))
            units = Units.initialize_units(doc, doc.sents[0])
            units = Separator(units, verbose=True)
            self.assertEqual([unit.text() for unit in units], test['output_text'])
            self.assertEqual([None if not unit.labels else next(iter(unit.labels)) for unit in units], test['output_tags'])
    



if __name__ == "__main__":
    unittest.main()