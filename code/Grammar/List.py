from typing import Callable, Any, Tuple
from Identify import *
from _.ExtendedDoc import ExtendedDoc
from _.Grammar.Unit import ExtendedDoc, List, Unit



def find(elements: List[Any], condition: Callable[[Any], bool]) -> Any:
    for element in elements:
        if condition(element):
            return element
    return None



def find_index(elements: List[Any], condition: Callable[[Any], bool]) -> int:
    for i, element in enumerate(elements):
        if condition(element):
            return i
    return -1



def find_all(elements: List[Any], condition: Callable[[Any], bool]) -> List[Any]:
    satisfies = []
    for i, element in enumerate(elements):
        if condition(element):
            satisfies.append(element)
    return satisfies



class Lists(Identify):
    NOUNS = ["NOUN", "PRON", "PROPN"]
    ENCLOSURES = {
        "[": "]",
        "{": "}",
        "(": ")",
        "\"": "\""
    }

    OPENING = set(ENCLOSURES.keys())
    CLOSING = set(ENCLOSURES.values())



    def __init__(self, doc: ExtendedDoc, units: List[Unit], enclosures: List[Unit]) -> None:
        super().__init__(doc, units)
        self.enclosures = enclosures


    
    def is_stop(self, unit: Unit) -> bool:
        is_break = Unit.BREAK in unit.labels and unit.lower()[0] == self.separator
        is_clause = unit.label_has([
            Unit.I_CLAUSE, 
            Unit.D_CLAUSE, 
            Unit.P_PHRASE,
            Unit.COLON,
            Unit.COLON_BREAK
        ])
        return bool(is_break or is_clause)


    
    def find_lists(self, separator: str):
        self.separator = separator
        
        lists: List[List[Any]] = [
            [
                [None, None]
            ]
        ]

        # print(f"find_lists")
        # print(f"Units:")
        # for i, unit in enumerate(self.units):
        #     print(f"{i}, {unit}")
        
        
        stack = []
        stack_pass = False

        text = " ".join([unit.lower() for unit in self.units])

        # It has been a while since I've looked at my code.
        # It seems that I'm checking whether the units are enclosed
        # in a pair of brackets. If they are, stack_pass = True.
        # What does stack_pass mean or do? I have yet to remember.
        opening_characters = [char for char in text if char in Lists.OPENING]
        closing_characters = [char for char in text if char in Lists.CLOSING]

        if bool(
            len(opening_characters) == 1 and 
            len(closing_characters) == 1 and
            text[+0] in opening_characters and 
            text[-1] in closing_characters and
            Lists.ENCLOSURES[text[0]] == text[-1]
        ):
            stack_pass = True

        # print(f"Text: {text}")
        # print(f"Stack Pass: {stack_pass}")
        
        i = 0
        while i < len(self.units):
            unit = self.units[i]

            # If we're not in an enclosure,
            # we check whether the current unit is an opening or closing.
            # If it's an opening, we add it to the stack. It seems that I'm handling
            # enclosures within a potential list. Why would I need this though? Perhaps,
            # the entire list's content would be added within the stack?
            if not stack_pass:
                if unit.lower() in Lists.OPENING:
                    stack.append(unit.lower())
                elif stack and unit.lower() in Lists.CLOSING and Lists.ENCLOSURES[stack[-1]] == unit.lower():
                    stack.pop()
            
            opened = lists[-1][0] != [None, None]

            # Actions
            close_list = unit.label_has([Unit.AND_OR_END]) and unit.lower()[0] == separator
            close_item = unit.label_has([Unit.BREAK]) and unit.lower()[0] == separator
            remove_list = unit.label_has([
                Unit.COLON, 
                Unit.COLON_BREAK
            ])
        
            # Close List
            # We only close the list if we're not 
            # in an enclosure and there's
            # something to close.
            if not stack and opened and close_list:
                # Invalid List, Remove
                if len(lists[-1]) < 2:
                    lists[-1] = [[None, None]]
                    i += 1
                    continue
                    
                # Find the L Index of Last Item
                last_item_l = i + 1

                # Find the R Index of Last Item
                last_item_r = last_item_l
                
                distance_from_next_stop = find_index(self.units[last_item_l:], lambda e: self.is_stop(e))
                # We extend the last item up until it
                # reaches the next stop.
                if distance_from_next_stop > 0:
                    last_item_r += distance_from_next_stop - 1
                # No Stop Found
                elif distance_from_next_stop == -1:
                    last_item_r = len(self.units) - 1

                # Add Last Item
                lists[-1].append([last_item_l, last_item_r])
                lists.append([[None, None]])
                i += 1

            # Close Item
            elif not stack and opened and close_item:
                lists[-1].append([i + 1, i])
                i += 1
                
            # Remove List
            elif not stack and opened and remove_list:
                lists[-1] = [[None, None]]
                i += 1
            
            # Continue Item
            else:
                if not opened:
                    lists[-1][0] = [i, i]
                else:
                    lists[-1][-1][1] += 1
                i += 1
            
        # print(f"1. Lists: {lists}")
        # If we reach the end of the list and the last
        # list is invalid (< 3 items), we remove it.
        if bool(
            lists and len(lists[-1]) < 3 or 
            (
                lists and
                not find(self.units[lists[-1][0][0]:], lambda e: e.label_has([Unit.AND_OR_END]) and e.lower()[0] == separator)
            )
        ):
            lists.pop()
        
        # print(f"2. Lists: {lists}")
        # In each item, we look for pairs (e.g. X and Y).
        # We only handle one conjunction.
        num_lists = len(lists)
        for i, lst in enumerate(lists):
            if i >= num_lists:
                break
            
            for l, r in lst:
                tokens = Unit.tokens(units=self.units[l:r+1])
                if not tokens:
                    continue
                conj = find_all(tokens, lambda t: Unit.is_conjunction(t))
                if len(conj) == 1:
                    lists.append([[l, r]])
        
        # print(f"3. Lists: {lists}")
        # If there's no lists at all, we can take advantage
        # of lax rules.
        if not lists:
            stack = []
            lst: List[List[Any]] = [[None, None]]
            i = 0
            conj_seen = False
            while i < len(self.units):
                unit = self.units[i]

                if unit.lower() in Lists.OPENING:
                    stack.append(unit.lower())
    
                if stack and unit.lower() in Lists.CLOSING and Lists.ENCLOSURES[stack[-1]] == unit.lower():
                    stack.pop()
                      
                if unit.label_has([Unit.CONJ]):
                    if not conj_seen:
                        conj_seen = True
                    elif lst != [[None, None]]:
                        lst[-1][1] = i - 1
                        lists.append(lst)
                        lst = [[i - 1, i]]
                else:
                    if lst == [[None, None]]:
                        lst = [[i, i]]
                    else:
                        lst[-1][1] = i
                
                i += 1
            
            if lst != [[None, None]] and conj_seen:
                lists.append(lst)
        # print(f"4. Lists: {lists}")
        # Here we remove duplicates, I'm not sure if duplicates still
        # occur, I observed them once, but this is here in case.
        # Note: I could do a cheeky list(set(...)), at least I think.
        i = 0
        while i < len(lists):
            if lists[i] in lists[i+1:]:
                lists.pop(i)
            else:
                i += 1
        # print(f"5. Lists: {lists}")
        # Remove Invalid Lists
        i = 0
        while i < len(lists):
            # The list contains one item and that item only contains one
            # token, or the list has two items.
            if bool(
                (
                    len(lists[i]) == 1 and 
                    lists[i][0][0] == lists[i][0][1]
                ) or
                (
                    len(lists[i]) == 1 and
                    # An AND/OR is required.
                    not [unit for unit in self.units[lists[i][0][0]:lists[i][0][1]+1] if "and" in unit.lower() or "or" in unit.lower()]
                ) or
                len(lists[i]) == 2
            ):
                lists.pop(i)
            else:
                i += 1
        # print(f"6. Lists: {lists}")
        return lists


    
    def clean_lists(self, lists):
        overlaps = []

        i = 0
        while i + 1 < len(lists):
            a = lists[i]
            b = lists[i+1]
                  
            if a[-1] != b[0]:
                i += 1
                continue

            if len(a) <= 1 or len(b) <= 1:
                i += 1
                continue

            # No Way to Split
            if a[-1][1] - a[-1][0] == 0 and b[0][1] - b[0][0] == 0:
                overlaps.extend([i, i + 1])
                i += 2
            else:
                a[-1][1] = a[-1][0]
                b[0][0] = b[0][1]
                i += 2

        lists = [l for i, l in enumerate(lists) if i not in overlaps]
        # print(f"7. Lists: {lists}")
        return lists


    
    def expand_noun(self, tokens, start, direction):
        for span in [*self.doc.doc.noun_chunks, *self.doc.doc.ents]:
            tokens_i = [t.i for t in span]
            if tokens[start].i in tokens_i:
                while start >= 0 and start < len(tokens) and tokens[start].i in tokens_i:
                    start += 1 * direction
                start += 1 * direction * -1
                break
        
        return start


    
    def char_bound_list(self, lst):
        # We bound each item according to characters or a speech.
        # We find these bounds from the "base item", the second to last item.
        base_tokens = Unit.tokens(units=self.units[lst[-2][0]:lst[-2][1]+1])
        
        if not base_tokens:
            raise Exception
        
        # As we're bounding by characters, primarily, the left bound is just
        # the characters of the first token
        l_bound = base_tokens[0].lower_

        # The right bound is the first tag, of the below set of tags, that we
        # encounter in the base tokens. If there's not such a token, we cannot
        # bound the items.
        speech = ["NOUN", "PROPN", "PRON", "VERB", "NUM"]
        r_bound = None
        for i in range(len(base_tokens) - 1, -1, -1):
            if base_tokens[i].pos_ in speech:
                r_bound = base_tokens[i]
                break

        if not r_bound:
            return None

        # The inner items are already bounded on the left and right sides.
        # All we need to check is whether the start matches with the left bound.
        inner_items = lst[1:-2]

        for i, item in enumerate(inner_items):
            l = item[0]
            r = item[1]
            
            tokens = Unit.tokens(units=self.units[l:r+1])
            if not tokens:
                raise Exception
            
            # If it doesn't match, we check if the next set of items can be
            # bounded. If not, we cannot bound the list.
            if tokens[0].lower_ != l_bound:
                if len(inner_items) - i - 1 >= 2:
                    return self.bound_list(lst[i+2:])
                return None
        
        # Check for L Bound in Starting Item
        start_tokens = Unit.tokens(units=self.units[lst[0][0]:lst[0][1]+1])
        if not start_tokens:
            raise Exception
        
        start_l = len(start_tokens) - 1
        while start_l >= 0 and start_tokens[start_l].lower_ != l_bound:
            start_l -= 1

        # L Bound Not Found
        if start_l < 0:
            # If the list is greater than 4 items, we can
            # cut off the starting item, and try again.
            if len(inner_items) >= 2:
                return self.bound_list(lst[1:])
            return None

        # If the first of the start tokens is a noun,
        # there may be more to include.
        if start_tokens[start_l].pos_ in Lists.NOUNS:
            start_l = self.expand_noun(start_tokens, start_l, -1)
        
        # Check for R Bound in Ending Item
        end_tokens = Unit.tokens(units=self.units[lst[-1][0]:lst[-1][1]+1])
        if not end_tokens:
            raise Exception
        
        end_r = 0
        num_end_tokens = len(end_tokens)
        while end_r < num_end_tokens and end_tokens[end_r].pos_ not in speech:
            end_r += 1

        if end_r >= num_end_tokens:
            return None

        # If the last of the end tokens is a noun, there may be more
        # to include.
        if end_tokens[end_r].pos_ in Lists.NOUNS:
            end_r = self.expand_noun(end_tokens, end_r, 1)
        
        # Create List
        unit_list = Unit(self.doc, labels=Unit.LIST, l=start_tokens[start_l].i, r=end_tokens[end_r].i)
        
        # Add Starting and Ending Items
        unit_list.children.extend([
            Unit(self.doc, labels=Unit.ITEM, l=start_tokens[start_l].i, r=start_tokens[-1].i),
            Unit(self.doc, labels=Unit.ITEM, l=end_tokens[0].i, r=end_tokens[end_r].i)
        ])
        
        for item in lst[1:-1]:
            tokens = Unit.tokens(units=self.units[item[0]:item[1]+1])
            if not tokens:
                raise Exception
            unit_item = Unit(self.doc, labels=Unit.ITEM, l=tokens[0].i, r=tokens[-1].i)
            unit_list.children.append(unit_item)

        return unit_list


    
    def char_bound_pair(self, pair):
        tokens = Unit.tokens(units=self.units[pair[0][0]:pair[0][1]+1])
        if not tokens:
            raise Exception
        
        tokens = sorted(tokens, key=lambda t: t.i)
        num_tokens = len(tokens)
        
        # Middle
        middle = find_index(tokens, lambda t: Unit.is_conjunction(t))

        # Bound L by R Token Characters
        l = middle - 1
        while l >= 0 and tokens[l].lower_ != tokens[middle + 1].lower_:
            l -= 1

        if l < 0:
            return None

        # Bound R by L Token Speech
        r =  middle + 1
        while r < num_tokens and not Unit.same_speech(tokens[middle-1].pos_, tokens[r].pos_):
            r += 1
        
        if r >= num_tokens:
            return None
        
        pair = Unit(self.doc, labels=Unit.LIST, l=tokens[l].i, r=tokens[r].i, children=[
            Unit(self.doc, labels=Unit.ITEM, l=tokens[l].i, r=tokens[middle-1].i), 
            Unit(self.doc, labels=Unit.ITEM, l=tokens[middle+1].i, r=tokens[r].i)
        ])

        return pair


    
    def bound_list(self, lst):
        # Base Item (2nd to Last Item) Tokens
        # This item is already bounded by the
        # left and right sides, which is useful.
        base_tokens = Unit.tokens(units=self.units[lst[-2][0]:lst[-2][1]+1])
        if not base_tokens:
            raise Exception
        
        num_base_tokens = len(base_tokens)
        
        # Speech Bounds
        speech = ["NOUN", "PROPN", "PRON", "VERB"]
        adjectives = ["ADJ", "ADV", "NUM", "ADP", "AUX"]
        

        # Find L Bound
        l_bound = []
        for i in range(0, num_base_tokens):
            if base_tokens[i].pos_ in speech:
                l_bound = [base_tokens[i].pos_]
                break
            elif base_tokens[i].pos_ in adjectives:
                l_bound = [base_tokens[i].pos_]

                j = i + 1
                while j < num_base_tokens:
                    if base_tokens[j].pos_ in speech:
                        l_bound.append(base_tokens[j].pos_)
                        break
                    j += 1
                
                break
        
        if not l_bound:
            return None

        
        # Find R Bound
        r_bound = []
        for i in range(num_base_tokens - 1, -1, -1):
            if base_tokens[i].pos_ in speech:
                r_bound = [base_tokens[i].pos_]
                break
            elif base_tokens[i].pos_ in adjectives:
                r_bound = [base_tokens[i].pos_]

                j = i - 1
                while j >= 0:
                    if base_tokens[j].pos_ in speech:
                        r_bound.append(base_tokens[j].pos_)
                        break
                    j -= 1
                
                break

        if not r_bound:
            return None
        

        # Check Inner Items
        # The inner items must have the left bound,
        # the right bound isn't as important.
        inner_items = lst[1:-1]

        verb_seen = False
        for i, item in enumerate(inner_items):
            l = item[0]
            r = item[1]
            
            item_tokens = Unit.tokens(units=self.units[l:r+1])
            if not item_tokens:
                raise Exception
            
            item_speech = [token.pos_ for token in item_tokens]

            # Must be Homogeneous
            if "VERB" not in item_speech and verb_seen:
                if len(inner_items) >= 2:
                    return self.bound_list(lst[1:])  
                else:
                    return None
            elif "VERB" in item_speech:
                verb_seen = True

            # Not Found
            if not set(l_bound).intersection(item_speech):
                # We check if the list starting at the next
                # item has a chance. If it does, that becomes
                # the list.
                if len(inner_items) - i + 1 >= 2:
                    return self.bound_list(lst[i+2:])
                return None
        

        # Check Starting Item
        start_tokens = Unit.tokens(units=self.units[lst[0][0]:lst[0][1]+1])
        if not start_tokens:
            raise Exception
        
        start_l = len(start_tokens) - 1
        while start_l >= 0 and not Unit.same_speech_list(start_tokens[start_l].pos_, l_bound):
            start_l -= 1

        if start_l < 0:
            if len(inner_items) >= 2:
                return self.bound_list(lst[1:])
            return None

        # Adjust Starting Item
        if set(l_bound).intersection(["ADJ", "NUM", "ADV", *Lists.NOUNS]):
            start_l = self.expand_noun(start_tokens, start_l, -1)
        
        # Check Ending Item
        end_tokens = Unit.tokens(units=self.units[lst[-1][0]:lst[-1][1]+1])
        if not end_tokens:
            raise Exception
        
        end_r = 0
        num_end_tokens = len(end_tokens)

        while end_r < num_end_tokens and not Unit.same_speech_list(end_tokens[end_r].pos_, r_bound):
            end_r += 1

        if end_r >= num_end_tokens:
            return None

        # Adjust Ending Item
        if set(r_bound).intersection(["ADJ", "NUM", "ADV", *Lists.NOUNS]):
            end_r = self.expand_noun(end_tokens, end_r, 1)
    
        # Adjusting Bounds for Start and End Entities
        l_i = start_tokens[start_l].i
        l_labels = set([Unit.ITEM])
        
        r_i = end_tokens[end_r].i
        r_labels = set([Unit.ITEM])

        # Handle Potential Overlap Issues w Enclosures
        for enclosure in self.enclosures:
            if not enclosure.label_has([Unit.BRACKETS, Unit.QUOTE]):
                continue
            
            l_overlap = enclosure.l <= start_tokens[start_l].i <= enclosure.r
            r_overlap = enclosure.l <= end_tokens[end_r].i <= enclosure.r

            # Left Item
            if l_overlap and not r_overlap:
                l_labels.update(enclosure.labels & {Unit.BRACKETS, Unit.QUOTE})
                l_i = min(enclosure.l, l_i)

            # Right Item
            if not l_overlap and r_overlap:
                r_labels.update(enclosure.labels & {Unit.BRACKETS, Unit.QUOTE})
                r_i = max(enclosure.r, r_i)
      
        unit_list = Unit(self.doc, labels=Unit.LIST, l=l_i, r=r_i)

        unit_start_item = Unit(self.doc, labels=list(l_labels), l=l_i, r=start_tokens[-1].i)
        unit_end_item = Unit(self.doc, labels=list(l_labels), l=end_tokens[0].i, r=r_i)
        unit_list.children.extend([unit_start_item, unit_end_item])

        for item in lst[1:-1]:
            tokens = Unit.tokens(units=self.units[item[0]:item[1]+1])
            if not tokens:
                raise Exception
            
            unit_item = Unit(self.doc, labels=Unit.ITEM, l=tokens[0].i, r=tokens[-1].i)
            unit_list.children.append(unit_item)

        return unit_list


    
    def bound_pair(self, pair):
        tokens = Unit.tokens(units=self.units[pair[0][0]:pair[0][1]+1])
        if not tokens:
            raise Exception

        tokens = sorted(tokens, key=lambda t: t.i)
        num_tokens = len(tokens)
        
        # Conjunction Partitions
        m = find_index(tokens, lambda t: Unit.is_conjunction(t))
        m_i = tokens[m].i

        # Speech for Bounding
        # We handle lists of the types below.
        speech = ["NOUN", "PROPN", "PRON", "VERB"]
        adjectives = ["ADJ", "ADV", "NUM", "ADP", "AUX"]

        # Find L Bound
        l_bound = []
        l_bound_i = None
        
        for i in range(m + 1, num_tokens):
            if tokens[i].pos_ in speech:
                l_bound = [tokens[i].pos_]
                l_bound_i = tokens[i].i
                break
            # With adjectives, we can also add the following token
            # as a bound. This allows a list like "X and [ADJ] Y"
            # to be recognized.
            elif tokens[i].pos_ in adjectives:
                l_bound = [tokens[i].pos_]

                j = i + 1
                while j < num_tokens:
                    if tokens[j].pos_ in speech:
                        l_bound.append(tokens[j].pos_)
                        break
                    j += 1
                
                break

        if not l_bound:
            return None
        
        # Find R Bound
        r_bound = []
        r_bound_i = None
        
        for i in range(m - 1, -1, -1):
            if tokens[i].pos_ in speech:
                r_bound = [tokens[i].pos_]
                r_bound_i = tokens[i].i
                break
            # With adjectives, we can also list the following token
            # as a bound. This allows a list like "X and [ADJ] Y"
            # to be recognized.
            elif tokens[i].pos_ in adjectives:
                r_bound = [tokens[i].pos_]

                j = i - 1
                while j >= 0:
                    if tokens[j].pos_ in speech:
                        r_bound.append(tokens[j].pos_)
                        break
                    j -= 1
                
                break
        
        if not r_bound:
            return None
        
        # Bound L Item
        l = m - 1
        while l >= 0 and not Unit.same_speech_list(tokens[l].pos_, l_bound):
            l -= 1

        if l < 0:
            return None

        # Adjust L if Noun
        if l_bound in Lists.NOUNS:
            l = self.expand_noun(tokens, l, -1)
        
        # Bound R Item
        r = m + 1
        while r < num_tokens and not Unit.same_speech_list(tokens[r].pos_, r_bound):
            r += 1
        
        if r >= num_tokens:
            return None

        # Adjust R if Noun
        if r_bound in Lists.NOUNS:
            r = self.expand_noun(tokens, r, 1)

        # Further Adjusting Bounds for Entities
        l_i = tokens[l].i
        l_label = {Unit.ITEM}
        
        r_i = tokens[r].i
        r_label = {Unit.ITEM}
        for ent in self.enclosures:
            if not ent.label_has([Unit.BRACKETS, Unit.QUOTE]):
                continue
            
            l_overlap = ent.l <= tokens[l].i <= ent.r
            r_overlap = ent.l <= tokens[r].i <= ent.r

            # Left Item
            if l_overlap and not r_overlap:
                l_label.update(ent.labels & {Unit.BRACKETS, Unit.QUOTE})
                l_i = min(ent.l, l_i)

            # Right Item
            if not l_overlap and r_overlap:
                r_label.update(ent.labels & {Unit.BRACKETS, Unit.QUOTE})
                r_i = max(ent.r, r_i)

        
        pair = Unit(self.doc, labels=Unit.LIST, l=l_i, r=r_i)
        pair.children.extend([
            Unit(self.doc, labels=list(l_label), l=l_i, r=m_i-1), 
            Unit(self.doc, labels=list(r_label), l=m_i+1, r=r_i)
        ])
        
        return pair


    
    def bound_lists(self, lists):
        bound_lists = []
        
        for lst in lists:
            bound = None
        
            if len(lst) == 1:
                bound = self.char_bound_pair(lst)
                if not bound:
                    bound = self.bound_pair(lst)
            else:
                bound = self.char_bound_list(lst)
                if not bound:
                    bound = self.bound_list(lst)
            
            if bound:
                bound_lists.append(bound)
        # print(f"8. Lists:")
        # for bound_list in bound_lists:
        #     print(f"-> {bound_list}")
        return bound_lists


    
    def merge_lists(self, bound_lists):
        # Map (L, R) to Unit List
        mapped_bounds = {}
        for lst in bound_lists:
            mapped_bounds[(lst.l, lst.r)] = lst
        bounds = list(mapped_bounds.keys())

        # Find Largest Coverage of Bounds
        max_coverage = []
        
        for bound in bounds:
            overlap = False
            for i, max_bound in enumerate(max_coverage):
                contains = max_bound[0] <= bound[0] <= max_bound[1] or max_bound[0] <= bound[1] <= max_bound[1]
                surround = bound[0] <= max_bound[0] <= bound[1] or bound[0] <= max_bound[1] <= bound[1]
                
                if contains or surround:
                    overlap = True
                
                    if bound[1] - bound[0] > max_bound[1] - max_bound[0]:
                        max_coverage[i] = bound
            
            if not overlap:
                max_coverage.append(bound)
        
        # Integrate Lists
        for bound in max_coverage:
            l_overlap = None
            l_overlap_i = -1
            
            r_overlap = None
            r_overlap_i = -1
            
            i = 0
            while i < len(self.units):
                unit = self.units[i]
                
                # Overlap w/ Left
                if not l_overlap and unit.l <= bound[0] <= unit.r:
                    l_overlap = unit
                    l_overlap_i = i
    
                # Overlap w/ Right
                if unit.l <= bound[1] <= unit.r:
                    r_overlap = unit
                    r_overlap_i = i

                if l_overlap and r_overlap:
                    break

                i += 1

            if not l_overlap or not r_overlap:
                raise Exception
            
            if l_overlap.label_has([Unit.BRACKETS, Unit.QUOTE]):
                self.units = self.units[:l_overlap_i] + self.units[r_overlap_i+1:]
                self.units.insert(l_overlap_i, mapped_bounds[bound])
                
                mapped_bounds[bound].l = min(l_overlap.l, mapped_bounds[bound].l)
                mapped_bounds[bound].r = max(l_overlap.r, mapped_bounds[bound].r)
                
            elif l_overlap.label_has([Unit.I_CLAUSE, Unit.D_CLAUSE, Unit.P_PHRASE]):
                if l_overlap.l == mapped_bounds[bound].l:
                    # Add Children
                    l_overlap.r = max(l_overlap.r, mapped_bounds[bound].r)
                    l_overlap.children.append(mapped_bounds[bound])
                    self.units = self.units[:l_overlap_i+1] + self.units[r_overlap_i+1:]
                else:
                    # Add Children
                    l_overlap.r = max(l_overlap.r, mapped_bounds[bound].r)
                    l_overlap.children.append(mapped_bounds[bound])
                    self.units = self.units[:l_overlap_i+1] + self.units[r_overlap_i+1:]
                    
            else:
                self.units = self.units[:l_overlap_i] + self.units[r_overlap_i+1:]
                self.units.insert(l_overlap_i, mapped_bounds[bound])

        return self.units
    


    
    def identify(self, sep):
        lists = self.find_lists(sep)
        lists = self.clean_lists(lists)
        lists = self.bound_lists(lists)
        lists = self.merge_lists(lists)
        return lists