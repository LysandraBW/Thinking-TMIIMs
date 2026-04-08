import spacy
import unittest
from ExtendedDoc import *
from Grammar import Bracket, Quote, Colon, Separator, PrepositionalPhrase, DependentClause, Unit, Units

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
            units = Bracket(units, verbose=False)

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
            units = Quote(units, verbose=False)

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
            units = Colon(units, verbose=False)

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
            units = Separator(units, verbose=False)

            self.assertEqual([unit.text() for unit in units], test['output_text'])
            self.assertEqual([None if not unit.labels else next(iter(unit.labels)) for unit in units], test['output_tags'])
    


    def test_prepositional_phrases(self):
        tests = [
            {
                'input': 'A new railroad is under construction',
                'output': ['A', 'new', 'railroad', 'is', 'under construction'],
            },
            {
                'input': 'After two trial runs we did it for real',
                'output': ['After two trial runs', 'we', 'did', 'it', 'for real'],
            },
            {
                'input': 'By the way, John is here',
                'output': ['By the way', ',', 'John', 'is', 'here'],
            },
            {
                'input': 'The apple trees are in full bearing',
                'output': ['The', 'apple', 'trees', 'are', 'in full bearing'],
            },
            {
                'input': 'Never tell tales out of school',
                'output': ['Never', 'tell', 'tales', 'out of school'],
            },
            {
                'input': 'In the picture room',
                'output': ['In the picture room'],
            }
        ]

        for test in tests:
            doc = ExtendedDoc(self.nlp(test['input']))

            units = Units.initialize_units(doc, doc.sents[0])
            units = PrepositionalPhrase(units, verbose=False)

            self.assertEqual([unit.text() for unit in units], test['output'])
    


    def test_dependent_clause(self):
        tests = [
            {
                'input': 'We have an umbrella because it is raining',
                'output': ['We', 'have', 'an', 'umbrella', 'because it is raining'],
            },
            {
                'input': 'Because it is raining, we have an umbrella',
                'output': ['Because it is raining', ',', 'we', 'have', 'an', 'umbrella'],
            },
            {
                'input': 'The movie that we watched last night was fun.',
                'output': ['The', 'movie', 'that we watched last night', 'was', 'fun', '.'],
            },
            {
                'input': 'The man who lives next door is a doctor',
                'output': ['The', 'man', 'who lives next door', 'is', 'a', 'doctor'],
            },
            {
                'input': 'What you said surprised me',
                'output': ['What you said', 'surprised', 'me'],
            },
            {
                'input': 'If it rains, we\'ll stay inside',
                'output': ['If it rains', ',', 'we', "'ll", 'stay', 'inside'],
            },
            {
                'input': 'She called after she arrived.',
                'output': ['She', 'called', 'after she arrived', '.']
            }
        ]

        for test in tests:
            doc = ExtendedDoc(self.nlp(test['input']))

            units = Units.initialize_units(doc, doc.sents[0])
            units = DependentClause(units, separator=',', verbose=True)

            self.assertEqual([unit.text() for unit in units], test['output'])



if __name__ == "__main__":
    unittest.main()