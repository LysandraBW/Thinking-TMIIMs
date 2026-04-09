from typing import Callable, Any, List, Tuple
from .Unit import Unit


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



class Lists:
    NOUNS = ["NOUN", "PRON", "PROPN"]
    ENCLOSED = {
        "[": "]",
        "{": "}",
        "(": ")",
        "\"": "\""
    }

    OPENING = set(ENCLOSED.keys())
    CLOSING = set(ENCLOSED.values())


    
    @staticmethod
    def is_stop(unit: Unit, separator: str) -> bool:
        is_break = Unit.SEP_PUNCT in unit.labels and unit.lower()[0] == separator
        is_clause = unit.label_has([
            Unit.I_CLAUSE, 
            Unit.D_CLAUSE, 
            Unit.P_PHRASE,
            Unit.COLON,
            Unit.COLON_BREAK
        ])

        return is_break or bool(is_clause)


    
    @staticmethod
    def find_lists(units: List[Unit], separator: str, verbose=False):
        lists: Any = [
            # A single list
            [
                # An interval representing an item within a list
                [None, None]
            ]
        ]

        if verbose:
            print(f"\nFind Lists\nIn Units: {[unit.text() for unit in units]}")
        
        text = " ".join([unit.lower() for unit in units])

        # It has been a while since I've looked at my code.
        # It seems that I'm checking whether the units are enclosed
        # in a pair of brackets. If they are, stack_pass = True.
        # What does stack_pass mean or do? I have yet to remember.
        opening_characters = [char for char in text if char in Lists.OPENING]
        closing_characters = [char for char in text if char in Lists.CLOSING]

        # In Enclosure
        in_enclosure = False

        if bool(
            len(opening_characters) == 1 and 
            len(closing_characters) == 1 and
            text[+0] in opening_characters and 
            text[-1] in closing_characters and
            Lists.ENCLOSED[text[0]] == text[-1]
        ):
            in_enclosure = True
        
        if verbose:
            print(f'Opening Characters: {opening_characters}')
            print(f'Closing Characters: {closing_characters}')
            print(f"Text: {text}")
            print(f"In Enclosure: {in_enclosure}")
        
        i = 0
        stack = []
        
        while i < len(units):
            unit = units[i]

            # If we're not in an enclosure,
            # we check whether the current unit is an opening or closing.
            # If it's an opening, we add it to the stack. It seems that I'm handling
            # an enclosure within a potential list. Why would I need this though? Perhaps,
            # the entire list's content would be added within the stack?
            if not in_enclosure:
                if unit.lower() in Lists.OPENING:
                    stack.append(unit.lower())
                if unit.lower() in Lists.CLOSING and stack and Lists.ENCLOSED[stack[-1]] == unit.lower():
                    stack.pop()
            
            # An empty list starts out with
            # [None, None]. Keep in mind that lists
            # holds a list of lists of lists (intervals).
            opened = lists[-1][0] != [None, None]

            # Actions
            close_list = unit.lower()[0] == separator and unit.has_label(Unit.SEP_PUNCT_AND_OR)
            close_item = unit.lower()[0] == separator and unit.has_label(Unit.SEP_PUNCT)
            scrap_list = unit.has_label(Unit.COLON, Unit.COLON_BREAK)
        
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
                
                # So, we're at the end of the list.
                # So, we need to find the last item.
                # So, so, so.

                # Find the L Index of Last Item
                # This doesn't require any further thinking,
                # the last item's start would be immediately
                # after the comma, unless the writer is mean.
                last_item_l = i + 1

                # Finding the R Index of Last Item
                # We are attempting to bound the last item's
                # right index. Why? Imagine:
                # The grass is green, the sun is yellow, and the sky is blue, but you are red.
                # We know the last item's left index comes immediately after
                # the 'and'. However, where does it end (i.e., what is its right index)?
                # We don't know, but we can bound it by finding the next stop, which
                # would be some sort of separator. In this case, it would be ', but'. 
                last_item_r = last_item_l
                distance_from_next_stop = find_index(units[last_item_l:], lambda e: Lists.is_stop(e, separator))

                # We extend the last item up until it
                # reaches the next stop.
                if distance_from_next_stop > 0:
                    last_item_r += distance_from_next_stop - 1
                # If there's no stop stopping us, we extend
                # the last item to the end of the units.
                elif distance_from_next_stop == -1:
                    last_item_r = len(units) - 1

                # Add Last Item
                lists[-1].append([last_item_l, last_item_r])

                # Add New List
                lists.append([[None, None]])
                i += 1

            # Close Item
            elif not stack and opened and close_item:
                # I know what you're thinking: if this
                # is an interval, why is the left number
                # greater than the right number? Well,
                # refer to the else-block. In the next
                # iteration, if we don't close the item,
                # close the list, or scrap the list, we
                # would continue the new item.
                # However, we're planning ahead. We're
                # not actually at this new item yet,
                # we're just setting the stage. There might
                # not even be a new item. So, we set its
                # left number, but not the right.
                # If we actually reach the new item,
                # the right number will be updated and
                # we'll have everything in order. However,
                # if there is no new item, then this would
                # be a sign that this is a bad item and
                # that we need to remove it.

                # Add New Item
                lists[-1].append([i + 1, i])
                i += 1
                
            # Scrap List
            elif not stack and opened and scrap_list:
                # We're overwriting whatever list was
                # previously being built with a new list.
                lists[-1] = [[None, None]]
                i += 1
            
            # Continue Item
            else:
                # This is the first item,
                # so no preparation took
                # place to warrant the else.
                if not opened:
                    lists[-1][0] = [i, i]
                else:
                    lists[-1][-1][1] += 1
                i += 1

        if verbose:
            print(f"1. Lists: {lists}")
        
        # If we reach the end of the list and the last
        # list is invalid (< 3 items), we remove it.
        if lists and bool(
            len(lists[-1]) < 3 or 
            (
                not find(units[lists[-1][0][0]:], lambda e: e.has_label(Unit.SEP_PUNCT_AND_OR) and e.lower()[0] == separator)
            )
        ):
            lists.pop()
        
        if verbose:
            print(f"2. Lists: {lists}")
        
        # In each item, we look for pairs (e.g. X and Y).
        # We only handle one conjunction.
        num_lists = len(lists)
        for i, opened_list in enumerate(lists):
            if i >= num_lists:
                break
            
            for l, r in opened_list:
                tokens = Unit.tokens(units=units[l:r+1])
                if not tokens:
                    continue

                conj = find_all(tokens, lambda t: Unit.is_conjunction(t))
                if len(conj) == 1:
                    lists.append([[l, r]])
        
        if verbose:
            print(f"3. Lists: {lists}")
        
        # If there's no lists at all, we can take advantage
        # of lax rules. So, we're basically doing everything 
        # we did initially, again. Is there a better way to 
        # do this? Me in the past did not know and me in the
        # present does not feel like knowing.
        if not lists:
            stack = []
            opened_list: List[List[Any]] = [[None, None]]
            conj_seen = False
            
            i = 0
            while i < len(units):
                unit = units[i]

                # It appears that we're also handling
                # enclosures in this version?
                if unit.lower() in Lists.OPENING:
                    stack.append(unit.lower())
                
                if unit.lower() in Lists.CLOSING and stack and Lists.ENCLOSED[stack[-1]] == unit.lower():
                    stack.pop()
                      
                if unit.has_label(Unit.SEP_CCONJ):
                    if not conj_seen:
                        conj_seen = True
                    # If we've already seen a conjunction,
                    # we end the opened list.
                    elif opened_list != [[None, None]]:
                        opened_list[-1][1] = i - 1
                        lists.append(opened_list)
                        opened_list = [[i - 1, i]]
                else:
                    # Open a List
                    if opened_list == [[None, None]]:
                        opened_list = [[i, i]]
                    # Continue Item
                    else:
                        opened_list[-1][1] = i
                
                i += 1
            
            if opened_list != [[None, None]] and conj_seen:
                lists.append(opened_list)
        
        if verbose:
            print(f"4. Lists: {lists}")
        
        # Here we remove duplicates, I'm not sure if duplicates still
        # occur, I observed them once, but this is here in case.
        i = 0
        while i < len(lists):
            if lists[i] in lists[i+1:]:
                lists.pop(i)
            else:
                i += 1
        
        if verbose:
            print(f"5. Lists: {lists}")
        
        # Delete Invalid Lists
        i = 0
        while i < len(lists):
            # We delete the list if
            # (1) it contains one item and that item only contains one
            # token; or (2) the list with one item has no ANDs or ORs; 
            # or (3) it has two items.
            if bool(
                (
                    len(lists[i]) == 1 and 
                    lists[i][0][0] == lists[i][0][1]
                ) or
                (
                    len(lists[i]) == 1 and
                    # An AND/OR is required.
                    not [unit for unit in units[lists[i][0][0]:lists[i][0][1]+1] if unit.lower() in ["and", "or"]]
                ) or
                len(lists[i]) == 2
            ):
                lists.pop(i)
            else:
                i += 1
        
        if verbose:
            print(f"6. Lists: {lists}")
        
        return lists


    
    @staticmethod
    def clean_lists(lists, verbose=False):
        # Sort Lists
        # This wasn't here before, I'm wondering
        # if it's not needed?
        # I feel like it would be, since we're
        # handling overlapping bounds.
        lists = sorted(lists, key=lambda l: l[0])
        overlaps = []

        i = 0
        while i + 1 < len(lists):
            a = lists[i]
            b = lists[i+1]
                  
            # Doesn't Overlap
            if a[-1] != b[0]:
                i += 1
                continue
            
            # Skip Short Lists
            # Why? Well, some of them may
            # be a nested list. Other than that,
            # I guess I'm assuming they won't overlap?
            # What do I mean by overlapping? I don't
            # see any greater or less than symbols.
            if len(a) <= 1 or len(b) <= 1:
                i += 1
                continue

            # No Way to Split
            # If there's no way to split it, we remove it.
            if a[-1][1] - a[-1][0] == 0 and b[0][1] - b[0][0] == 0:
                overlaps.extend([i, i + 1])
                i += 2
            else:
                a[-1][1] = a[-1][0]
                b[0][0] = b[0][1]
                i += 2

        lists = [lst for i, lst in enumerate(lists) if i not in overlaps]
        
        if verbose:
            print(f"7. Lists: {lists}")
        
        return lists


    
    # If I remember correctly, this is to expand an item's
    # 'area'. The first item would be expanded to the left,
    # and the last item would be expanded to the right -- hence,
    # the direction parameter.
    # spans: A list of spans wherein a span is seen as having 
    # already expanded tokens.
    # tokens: This seems to be the set of tokens we can expand into.
    # start: Where you're starting from in the set of tokens.
    # direction: Whether you're expanding to the left or right.
    @staticmethod
    def expand_noun(spans, tokens, start, direction):
        for span in spans:
            tokens_i = [t.i for t in span]
            if tokens[start].i in tokens_i:
                while start >= 0 and start < len(tokens) and tokens[start].i in tokens_i:
                    start += 1 * direction
                start += 1 * direction * -1
                break
        
        return start


    
    @staticmethod
    def char_bound_list(units: List[Unit], lst, enclosed):
        # We bound each item according to characters or a speech.
        # We find these bounds from the "base item", the second to last item.
        base_tokens = Unit.tokens(units=units[lst[-2][0]:lst[-2][1]+1])
        
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
            
            tokens = Unit.tokens(units=units[l:r+1])
            if not tokens:
                raise Exception
            
            # If it doesn't match, we check if the next set of items can be
            # bounded. If not, we cannot bound the list.
            if tokens[0].lower_ != l_bound:
                if len(inner_items) - i - 1 >= 2:
                    return Lists.bound_list(units, lst[i+2:], enclosed)
                return None
        
        # Check for L Bound in Starting Item
        start_tokens = Unit.tokens(units=units[lst[0][0]:lst[0][1]+1])
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
                return Lists.bound_list(units, lst[1:], enclosed)
            return None

        # If the first of the start tokens is a noun,
        # there may be more to include.
        if start_tokens[start_l].pos_ in Lists.NOUNS:
            start_l = Lists.expand_noun([*units[0].doc.doc.noun_chunks, units[0].doc.doc.ents], start_tokens, start_l, -1)
        
        # Check for R Bound in Ending Item
        end_tokens = Unit.tokens(units=units[lst[-1][0]:lst[-1][1]+1])
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
            end_r = Lists.expand_noun([*units[0].doc.doc.noun_chunks, units[0].doc.doc.ents], end_tokens, end_r, 1)
        
        # Create List
        unit_list = Unit(units[0].doc, labels=Unit.LIST, l=start_tokens[start_l].i, r=end_tokens[end_r].i)
        
        # Add Starting and Ending Items
        unit_list.children.extend([
            Unit(units[0].doc, labels=Unit.ITEM, l=start_tokens[start_l].i, r=start_tokens[-1].i),
            Unit(units[0].doc, labels=Unit.ITEM, l=end_tokens[0].i, r=end_tokens[end_r].i)
        ])
        
        for item in lst[1:-1]:
            tokens = Unit.tokens(units=units[item[0]:item[1]+1])
            if not tokens:
                raise Exception
            unit_item = Unit(units[0].doc, labels=Unit.ITEM, l=tokens[0].i, r=tokens[-1].i)
            unit_list.children.append(unit_item)

        return unit_list


    
    # I cannot remember the difference between this
    # and bound_pair. It seems that we're comparing
    # the literal text as a last ditch attempt.
    @staticmethod
    def char_bound_pair(units: List[Unit], pair):
        tokens = Unit.tokens(units=units[pair[0][0]:pair[0][1]+1])
        if not tokens:
            raise Exception
        
        tokens = sorted(tokens, key=lambda t: t.i)
        num_tokens = len(tokens)
        
        # Middle
        m = find_index(tokens, lambda t: Unit.is_conjunction(t))

        # Bound L by R Token Characters
        l = m - 1
        while l >= 0 and tokens[l].lower_ != tokens[m + 1].lower_:
            l -= 1

        if l < 0:
            return None

        # Bound R by L Token Speech
        r =  m + 1
        while r < num_tokens and not Unit.same_speech(tokens[m-1].pos_, tokens[r].pos_):
            r += 1
        
        if r >= num_tokens:
            return None
        
        doc = units[0].doc
        pair = Unit(doc, labels=Unit.LIST, l=tokens[l].i, r=tokens[r].i, children=[
            Unit(doc, labels=Unit.ITEM, l=tokens[l].i, r=tokens[m-1].i), 
            Unit(doc, labels=Unit.ITEM, l=tokens[m+1].i, r=tokens[r].i)
        ])

        return pair


    
    @staticmethod
    def bound_list(units: List[Unit], lst, enclosed: List[Unit]):
        # Base Tokens
        # The 2nd to last item is already bounded by the
        # left and right sides, so we use it as
        # a reference for the types of tokens we're
        # looking for.

        # The 2nd item is also bounded; you could use
        # different items. Perhaps, I should use all
        # bounded items? Eh, I'm only handling simple
        # situations.
        base_tokens = Unit.tokens(units=units[lst[-2][0]:lst[-2][1]+1]) # Adding a 1 because the intervals are inclusive
        if not base_tokens:
            raise Exception
        num_base_tokens = len(base_tokens)
        
        # Speech Bounds
        speech_noun_verb = ["NOUN", "PROPN", "PRON", "VERB"]
        speech_adjectives = ["ADJ", "ADV", "NUM", "ADP", "AUX"]
        
        # Find L Bound
        # We start from the left and look for
        # any of the above speeches.
        l_bound = []
        for i in range(0, num_base_tokens):
            if base_tokens[i].pos_ in speech_noun_verb:
                l_bound = [base_tokens[i].pos_]
                break

            # We have some more searching to do. If the
            # adjective used for a noun? A proper noun?
            # We continue looking to answer this question.
            elif base_tokens[i].pos_ in speech_adjectives:
                l_bound = [base_tokens[i].pos_]

                j = i + 1
                while j < num_base_tokens:
                    if base_tokens[j].pos_ in speech_noun_verb:
                        l_bound.append(base_tokens[j].pos_)
                        break
                    j += 1
                
                break
        
        if not l_bound:
            return None

        
        # Find R Bound
        # Same process as before, but we start from
        # the right and work our way to the left.
        r_bound = []
        for i in range(num_base_tokens - 1, -1, -1):
            if base_tokens[i].pos_ in speech_noun_verb:
                r_bound.append(base_tokens[i].pos_)
                break

            elif base_tokens[i].pos_ in speech_adjectives:
                r_bound.append(base_tokens[i].pos_)

                j = i - 1
                while j >= 0:
                    if base_tokens[j].pos_ in speech_noun_verb:
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
            
            item_tokens = Unit.tokens(units=units[l:r+1])
            if not item_tokens:
                raise Exception
            
            item_speech = [token.pos_ for token in item_tokens]

            # Must be Homogeneous
            # So, we've seen a verb in a previous item, and there's
            # no verb in this item. This is problematic, so we
            # cut off the list, if possible.
            if ("VERB" not in item_speech and verb_seen) or ("VERB" in item_speech and not verb_seen and i != 0):
                if len(inner_items) >= 2:
                    return Lists.bound_list(units, lst[1:], enclosed)  
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
                    return Lists.bound_list(units, lst[i+2:], enclosed)
                return None
        

        # Check Starting Item
        start_tokens = Unit.tokens(units=units[lst[0][0]:lst[0][1]+1])
        if not start_tokens:
            raise Exception
        
        start_l = len(start_tokens) - 1
        while start_l >= 0 and not Unit.same_speech_list(start_tokens[start_l].pos_, l_bound):
            start_l -= 1

        if start_l < 0:
            if len(inner_items) >= 2:
                return Lists.bound_list(units, lst[1:], enclosed)
            return None

        # Adjust Starting Item
        # ADJs, NUMs, and ADVs can still be a part of a noun.
        # So, I'm including them here.
        if set(l_bound).intersection(["ADJ", "NUM", "ADV", *Lists.NOUNS]):
            start_l = Lists.expand_noun([*units[0].doc.doc.noun_chunks, *units[0].doc.doc.ents], start_tokens, start_l, -1)
        
        # Check Ending Item
        end_tokens = Unit.tokens(units=units[lst[-1][0]:lst[-1][1]+1])
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
            end_r = Lists.expand_noun([*units[0].doc.doc.noun_chunks, *units[0].doc.doc.ents], end_tokens, end_r, 1)


        # Adjusting Bounds for Start and End Entities
        l_i = start_tokens[start_l].i
        l_labels = set([Unit.ITEM])
        
        r_i = end_tokens[end_r].i
        r_labels = set([Unit.ITEM])


        # Handle Potential Overlap Issues with Enclosed
        # If an item overlaps with an enclosure, it must
        # consume it.
        for enclosure in enclosed:
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
      

        # Creating a List
        # We're finally done.
        doc = units[0].doc
        unit_list = Unit(doc, labels=Unit.LIST, l=l_i, r=r_i)

        unit_start_item = Unit(doc, labels=list(l_labels), l=l_i, r=start_tokens[-1].i)
        unit_end_item = Unit(doc, labels=list(l_labels), l=end_tokens[0].i, r=r_i)

        unit_list.children.append(unit_start_item)
        
        # Inner Items
        for item in lst[1:-1]:
            tokens = Unit.tokens(units=units[item[0]:item[1]+1])
            if not tokens:
                raise Exception
            
            unit_item = Unit(doc, labels=Unit.ITEM, l=tokens[0].i, r=tokens[-1].i)
            unit_list.children.append(unit_item)
        
        unit_list.children.append(unit_end_item)

        return unit_list


    
    @staticmethod
    def bound_pair(units: List[Unit], pair, enclosed):
        tokens = Unit.tokens(units=units[pair[0][0]:pair[0][1]+1])
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
        
        for i in range(m + 1, num_tokens):
            if tokens[i].pos_ in speech:
                l_bound = [tokens[i].pos_]
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
        
        for i in range(m - 1, -1, -1):
            if tokens[i].pos_ in speech:
                r_bound = [tokens[i].pos_]
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

        # Adjust L, if Noun or Noun-Related
        if set(l_bound).intersection(["ADJ", "ADV", "NUM", *Lists.NOUNS]):
            l = Lists.expand_noun([*units[0].doc.doc.noun_chunks, units[0].doc.doc.ents], tokens, l, -1)
        
        # Bound R Item
        r = m + 1
        while r < num_tokens and not Unit.same_speech_list(tokens[r].pos_, r_bound):
            r += 1
        
        if r >= num_tokens:
            return None

        # Adjust R, if Noun or Noun-Related
        if set(r_bound).intersection(["ADJ", "ADV", "NUM", *Lists.NOUNS]):
            r = Lists.expand_noun([*units[0].doc.doc.noun_chunks, units[0].doc.doc.ents], tokens, r, 1)


        # Handling Possible Overlaps with Enclosed Units
        l_i = tokens[l].i
        l_label = {Unit.ITEM}
        
        r_i = tokens[r].i
        r_label = {Unit.ITEM}

        for ent in enclosed:
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

        
        doc = units[0].doc
        pair = Unit(doc, labels=Unit.LIST, l=l_i, r=r_i)
        pair.children.extend([
            Unit(units[0].doc, labels=list(l_label), l=l_i, r=m_i-1), 
            Unit(units[0].doc, labels=list(r_label), l=m_i+1, r=r_i)
        ])
        
        return pair


    
    @staticmethod
    def bound_lists(units, lists, enclosed, verbose=False):
        bound_lists = []
        
        for lst in lists:
            bound = None
        
            if len(lst) == 1:
                bound = (
                    Lists.char_bound_pair(units, lst) or 
                    Lists.bound_pair(units, lst, enclosed)
                )
            else:
                bound = (
                    Lists.char_bound_list(units, lst, enclosed) or
                    Lists.bound_list(units, lst, enclosed)
                )

            if bound:
                bound_lists.append(bound)

        if verbose:
            print(f"8. Lists:")
            for bound_list in bound_lists:
                print(f"-> {bound_list}")
        
        return bound_lists


    
    @staticmethod
    def merge_lists(units: List[Unit], bound_lists, verbose=False):
        # My method for identifying overlapping bounds or
        # finding the max coverage is probably flawed. I did
        # not do a proof or test it.

        if verbose:
            print(f"9. IN Units: {[unit.text() for unit in units]}")
            print(f"9. IN Lists:")
            for bound_list in bound_lists:
                print(f"-> {bound_list}")

        
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
        

        # Merge Overlapping Lists
        # I wish I could remember what this
        # did.
        for bound in max_coverage:
            l_overlap = None
            l_overlap_i = -1
            
            r_overlap = None
            r_overlap_i = -1
            
            i = 0
            while i < len(units):
                unit = units[i]
                
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
                units = units[:l_overlap_i] + units[r_overlap_i+1:]
                units.insert(l_overlap_i, mapped_bounds[bound])
                
                mapped_bounds[bound].l = min(l_overlap.l, mapped_bounds[bound].l)
                mapped_bounds[bound].r = max(l_overlap.r, mapped_bounds[bound].r)
                
            elif l_overlap.label_has([Unit.I_CLAUSE, Unit.D_CLAUSE, Unit.P_PHRASE]):
                if l_overlap.l == mapped_bounds[bound].l:
                    # Add Children
                    l_overlap.r = max(l_overlap.r, mapped_bounds[bound].r)
                    l_overlap.children.append(mapped_bounds[bound])
                    units = units[:l_overlap_i+1] + units[r_overlap_i+1:]
                else:
                    # Add Children
                    l_overlap.r = max(l_overlap.r, mapped_bounds[bound].r)
                    l_overlap.children.append(mapped_bounds[bound])
                    units = units[:l_overlap_i+1] + units[r_overlap_i+1:]
                    
            else:
                units = units[:l_overlap_i] + units[r_overlap_i+1:]
                units.insert(l_overlap_i, mapped_bounds[bound])

        if verbose:
            print(f"9. OUT Units:")
            for unit in units:
                print(f"-> {[child.text() for child in unit.children]}")
            
        return units
    


    @staticmethod
    def identify(units: List[Unit], separator: str, enclosed: List[Unit], verbose=False):
        if verbose:
            print(f'In: {[unit.text() for unit in units]}\n\n')
        
        lists = Lists.find_lists(units, separator=separator, verbose=verbose)
        lists = Lists.clean_lists(lists, verbose=verbose)
        lists = Lists.bound_lists(units, lists, enclosed, verbose=verbose)
        lists = Lists.merge_lists(units, lists, verbose=verbose)
        lists = [unit for unit in lists if unit.children]

        if verbose:
            print(f"Out:")
            for unit in lists:
                print(f"-> {[child.text() for child in unit.children]}")
        
        return lists



    def __new__(cls, units, separator, enclosed, verbose=False):
        return Lists.identify(units=units, separator=separator, enclosed=enclosed, verbose=verbose)