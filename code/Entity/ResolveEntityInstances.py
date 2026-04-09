from typing import Any, Set, Dict, TypedDict, List, cast
from spacy.tokens import Span
from .ExtendedDoc import *
from .text import *
from .names import *
from .tokens import *
from .inflections import *
from .inflections_latin import *
from nltk.stem import PorterStemmer, SnowballStemmer, LancasterStemmer



ps = PorterStemmer()



class Entity(TypedDict):
    labels: Set[str]
    spans: Set[Span]
    values: Set[str]
    lowers: Set[str]
    morphs: Set[str]
    subs: Set[str]
    subs_mapped: Dict[str, Set[str]]
    taxa: Set[str]
    taxonomic: Set[str]
    scientific: Set[str]
    vernacular: Set[str]



class ResolveEntityInstances:
    def __init__(self, doc: ExtendedDoc) -> None:
        self.doc = doc
    

    def find_substitutions(self, ents: List[Span]) -> Dict[str, List[str]]:
        token_to_ent = {}
        for ent in ents:
            for token in ent:
                token_to_ent[token] = ent
        
        # The text provides information about 
        # names that will be used interchangeably,
        # like "predatory crab (Carcinus maenas)".
        substitutions: Dict[str, List[str]] = {}


        def add_substitutions(a, b):
            notation_a = re_taxonomic_notation(a)
            notation_b = re_taxonomic_notation(b)

            a = a if notation_a else a.lower()
            b = b if notation_b else b.lower()
                    
            if a not in substitutions:
                substitutions[a] = []
            substitutions[a].append(b)

            return


        start = None
        for token in self.doc.doc:
            # Neighboring Spans
            # We're only using the last token of the span.
            # token_to_ent[token][-1] == token: is used so
            # that we only use the last token of the span
            if token in token_to_ent and token_to_ent[token][-1] == token:
                token_span = token_to_ent[token]
                token_n1 = token.i + 1 <= len(self.doc.doc) - 1 and token.nbor(1)
                token_n2 = token.i + 2 <= len(self.doc.doc) - 1 and token.nbor(2)
                
                same_sent_n2 = token and token_n2 and token.sent == token_n2.sent
                
                # Use Case: "Diptera: Tephritidae"
                if token_n1 and token_n2 and same_sent_n2 and token_n1.lower_ in ['.', ':'] and token_n2 in token_to_ent:
                    add_substitutions(
                        self.doc.text[token_span.start_char:token_span.end_char], 
                        self.doc.text[token_to_ent[token_n2].start_char:token_to_ent[token_n2].end_char]
                    )
            
            # Dealing with Parentheses
            # 1. Opening Parentheses
            if token.text == "(":
                start = token

            # 2. Closing Parentheses
            if start and token.text == ")":
                # Spans in Parentheses
                tracked_spans = set()
                tracked_spans.update(self.doc.doc[i] for i in range(start.i + 1, token.i) if self.doc.doc[i] in token_to_ent)

                # Span to Left of Parentheses
                token_k = start.i != 0 and start.nbor(-1)
                if not token_k or token_k not in token_to_ent:
                    start = None
                    continue
                
                span_k = token_to_ent[token_k]
                text_k = self.doc.text[span_k.start_char:span_k.end_char]

                for span in tracked_spans:
                    text_v = self.doc.text[span.start_char:span.end_char]
                    add_substitutions(text_k, text_v)
                
                start = None
        
        
        return substitutions



    @staticmethod
    def clean_name(name: str) -> str:
        name = re.sub(rf'[{string.punctuation}]', ' ', name)
        name = re.sub(r'\s+', ' ', name)
        return name
    


    def create_entity(self, instances: Set[Span]) -> Entity | None:
        if not instances:
            return None
        
        # Pick a Span
        span = next(iter(instances))

        # Name
        value = self.doc.text[span.start_char:span.end_char]
        lower = value.lower()
        
        # Taxonomic Name
        name_taxonomic = value if re_taxonomic_name(value) else re_taxonomic_notation(value)
        name_taxonomic_lower = None if not name_taxonomic else name_taxonomic.lower()
        name_is_taxonomic_notation = name_taxonomic and name_taxonomic != value

        # Get Labels
        label = None
        
        if in_vernacular(lower):
            label = 'v'
        elif in_roles(lower):
            label = 'r'
        elif in_scientific(name_taxonomic_lower or lower):
            label = 's'
        else:
            for r_i, data in all_names.iter(self.doc.text_lower):
                if len(data['key']) <= 2:
                    continue
                
                r_i += 1
                l_i = r_i - len(data['key'])

                l_bound = l_i == 0 or is_boundary(self.doc.text_lower[l_i-1])
                r_bound = r_i == len(self.doc.text_lower) or is_boundary(self.doc.text_lower[r_i])

                if not l_bound or not r_bound:
                    continue
                
                if label and data['label'] != label:
                    label = 'm'
                    break
                label = data['label']        


        if not label:
            label = 'm'
        
        
        # Get Substitutions
        subs = mapped_names.get(name_taxonomic_lower or lower, set())
        

        # Get Morphs
        morphs = set()
        

        # Casing matters if the name is that
        # of taxonomic notation. For example,
        # Salmo trutta l. != Salmo trutta L.
        if name_is_taxonomic_notation:
            morphs.add(value)
            morphs.add(ResolveEntityInstances.clean_name(value))
        else:
            morphs.add(lower)
            morphs.add(ResolveEntityInstances.clean_name(value))
        
        if name_taxonomic_lower:
            morphs.add(name_taxonomic_lower)
        
        if label == 's':
            if name_taxonomic_lower:
                for inflection in abbreviate(name_taxonomic):
                    inflection = inflection.lower()
                    morphs.add(inflection)
                    morphs.add(ResolveEntityInstances.clean_name(inflection))
            else:
                for inflection in get_inflections_latin(lower):
                    morphs.add(inflection)
                    morphs.add(ResolveEntityInstances.clean_name(inflection))
        else:
            morphs.add(ps.stem(lower))
            for inflection in get_inflections(lower, span[-1].tag_):
                morphs.add(inflection)
                morphs.add(ResolveEntityInstances.clean_name(inflection))
        

        return {
            'labels': {label},
            'spans': instances,
            'values': {value},
            'morphs': morphs,
            'lowers': {lower},
            'subs': subs,
            'subs_mapped': {form: subs for form in morphs},
            'taxa': morphs if label == 's' and is_taxa(value) else set(),
            'taxonomic': set() if not name_taxonomic_lower else {name_taxonomic_lower},
            'scientific': morphs if label == 's' else set(),
            'vernacular': morphs if label == 'v' else set()   
        }



    def merge(self, a: Entity, b: Entity) -> Entity:
        merged = {}
        
        keys = set([*a.keys(), *b.keys()])
        for key in keys:
            merged[key] = a[key] | b[key]
        
        return cast(Entity, merged)
    


    def merge_linked(self, links: Dict[int, Set[int]], ents: List[Entity]) -> List[Entity]:
        link_pairs = list(links.items())
        link_pairs.sort(key=lambda link: len(link[1]), reverse=True)
        
        for source_i, targets_i in link_pairs:
            if not ents[source_i]:
                continue
            
            for target_i in targets_i:
                if source_i == target_i or not ents[target_i]:
                    continue
                
                ents[target_i] = self.merge(
                    ents[target_i], 
                    ents[source_i]
                )
            
            # We set the source entity to None if it
            # has been merged with any targets. As this line
            # will change some entities to None, we must check
            # for the targets that actually exist.
            if [target_i for target_i in targets_i if ents[target_i]]:
                ents[source_i] = cast(Entity, None)

        return [ent for ent in ents if ent]
    
    

    def merge_by_contains(self, ents: List[Entity]) -> List[Entity]:
        links = {i: set() for i in range(len(ents))}
        
        i = 0
        while i < len(ents):
            j = i + 1
            while j < len(ents):
                # Matching Labels
                # If the labels don't match, we can save time
                # and continue on to the next pair of groups.
                if (
                    'm' not in ents[i]['labels'] and 
                    'm' not in ents[j]['labels'] and
                    not ('r' in ents[i]['labels'] and 'v' in ents[j]['labels']) and
                    not ('v' in ents[i]['labels'] and 'r' in ents[j]['labels']) and
                    ents[i]['labels'].isdisjoint(ents[j]['labels'])
                ):
                    j += 1
                    continue
                
                morphs_i: Any = ents[i]['morphs']
                morphs_j: Any = ents[j]['morphs']

                if not morphs_i.isdisjoint(morphs_j):
                    links[i].add(j)
                    links[j].add(i)
                else:
                    found = [False, False]

                    for form_i in morphs_i:
                        for form_j in morphs_j:
                            index = form_j.find(form_i)
                            if index != -1 and (index == 0 or is_boundary(form_j[index-1])) and (index + len(form_i) == len(form_j) or is_boundary(form_j[index + len(form_i)])):
                                links[i].add(j)
                                found[0] = True
                            index = form_i.find(form_j)
                            if index != -1 and (index == 0 or is_boundary(form_i[index-1])) and (index + len(form_j) == len(form_i) or is_boundary(form_i[index + len(form_j)])):
                                links[j].add(i)
                                found[1] = True
                            
                            # No More Comparisons
                            # If both are true, we will not find
                            # any more important information. So,
                            # we can save ourselves the time.
                            if found[0] and found[1]:
                                break
                        
                        # Break
                        if found[0] and found[1]:
                            break
                
                j += 1
            i += 1

        return self.merge_linked(links, ents)


    def merge_by_internal_subs(self, ents: List[Entity], subs: Dict[str, List[str]]) -> List[Entity]:
        links = {i: set() for i in range(len(ents))}
        
        for k, v in subs.items():
            sources = [i for i, group in enumerate(ents) if group['morphs'] & {k}]
            targets = [i for i, group in enumerate(ents) if i not in sources and group['morphs'] & set(v)]
            
            # Swap
            # Either 'sources' or 'targets' will have only 1
            # element.
            if len(sources) > len(targets):
                sources, targets = targets, sources

            if not sources:
                continue
            
            links[sources[0]].update(targets)
        
        return self.merge_linked(links, ents)


    def merge_by_external_subs(self, ents: List[Entity]) -> List[Entity]:
        links = {i: set() for i in range(len(ents))}
        
        i = 0
        while i < len(ents):
            j = i + 1
            while j < len(ents):
                if i in links.get(j, []):
                    j += 1
                    continue

                found = False

                pairs = [
                    ['taxa', 'vernacular'],
                    ['vernacular', 'taxa'],
                    ['scientific', 'vernacular'],
                    ['vernacular', 'scientific']
                ]
                
                for l1, l2 in pairs:
                    A: Set[str] = ents[i][l1] - ents[j][l1]
                    B: Set[str] = ents[j][l2] - ents[i][l2]
                    
                    # We do not want to merge two different species because of a
                    # similar ancestor. Alas, the 'taxa' group cannot have any species.
                    if l1 == 'taxa' and ents[i]['taxonomic']:
                        continue

                    if l2 == 'taxa' and ents[j]['taxonomic']:
                        continue

                    subs_mapped_a: Dict[str, Set[str]] = ents[i]['subs_mapped']
                    subs_mapped_b: Dict[str, Set[str]] = ents[j]['subs_mapped']

                    A_subs = set().union(*[subs_mapped_a[a] for a in A if subs_mapped_a[a]]) or A
                    B_subs = set().union(*[subs_mapped_b[b] for b in B if subs_mapped_b[b]]) or B
                    
                    if not A_subs.isdisjoint(B_subs):
                        links[i].add(j)
                        links[j].add(i)
                        found = True
                        break
                    
                if not found:
                    A: Set[str] = ents[i]['morphs'] - ents[j]['morphs']
                    B: Set[str] = ents[j]['morphs'] - ents[i]['morphs']

                    for a in A:
                        for b in B:
                            if names_related(a, b):
                                links[i].add(j)
                                links[j].add(i)
                                found = True
                                break
                            
                        if found:
                            break
                j += 1
            i += 1

        return self.merge_linked(links, ents)



    def resolve(self, ent_instances: List[Span], *, verbose=False) -> List[Entity]:
        # Create Entities
        mapped = {}
        for ent in ent_instances:
            ent_text_lower = self.doc.text_lower[ent.start_char:ent.end_char]
            if ent_text_lower not in mapped:
                mapped[ent_text_lower] = set()
            mapped[ent_text_lower].add(ent)
        
        ents_res = [self.create_entity(instances) for instances in mapped.values()]
        ents_res = [ent for ent in ents_res if ent]

        if verbose:
            print('Create Groups')
            for g_i, group in enumerate(ents_res):
                print(g_i, group['morphs'], group['labels'])
            print()
            print()
        
        ents_res = self.merge_by_contains(ents_res)    
        if verbose:
            print('Group by Contains')
            for g_i, group in enumerate(ents_res):
                print(g_i, group['morphs'])
            print()
            print()
        
        subs = self.find_substitutions(ent_instances)
        if verbose:
            print(f'Subs: {subs}')
        
        ents_res = self.merge_by_internal_subs(ents_res, subs)
        if verbose:
            print('Group by Internal Subs')
            for g_i, group in enumerate(ents_res):
                print(g_i, group['morphs'])
            print()
            print()

        ents_res = self.merge_by_external_subs(ents_res)
        if verbose:
            print('Group by External Subs')
            for g_i, group in enumerate(ents_res):
                print(g_i, group['morphs'])
            print()
            print()

        if verbose:
            print()
            for g_i, group in enumerate(ents_res):
                print(g_i, group['morphs'])
            print()
            print()

        return ents_res


    
    def __call__(self, ent_instances: List[Span], *, verbose=False) -> Any:
        return self.resolve(ent_instances, verbose=verbose)