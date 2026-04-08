import re
import unicodedata
import regex
import string
from typing import List



def break_text(text: str) -> List[str]:
    enclosures = {
        "(":")", 
        "[":"]",
        "{":"}"
    }
    
    # This contains the text that's not inside
    # any enclosure.
    base = []

    # This contains the text that's inside
    # an enclosure.
    groups = []
    
    # This is used for building groups, which can
    # have a nested structure.
    stacks = []
    
    # These are the pairs of characters that
    # define the enclosure (parenthetical).
    openers = list(enclosures.keys())
    closers = list(enclosures.values())
    
    # This contains the opening characters of the groups 
    # that are currently open (e.g. '(', '['). We use it 
    # so that we know whether to open or close a group.
    opened = []
    
    for i, char in enumerate(text):
        # Open Group
        if char in openers:
            stacks.append([])
            opened.append(char)
        # Close Group
        elif opened and char == enclosures.get(opened[-1], ""):
            groups.append(stacks.pop())
            opened.pop()
        # Add to Group
        elif opened:
            stacks[-1].append(i)
        # Add to Base Text
        else:
            base.append(i)
    
    # We close the remaining groups that have not
    # been closed.
    while stacks:
        groups.append(stacks.pop())
        
    # Cluster Groups' Indices
    # A list in the lists of indices (where each list represents a group of text) could have 
    # an interruption (e.g. [0, 1, 2, 10, 15]) because of a parenthetical. So, we cluster the
    # indices in each list to make the output more useful (e.g. [(0, 3), (10, 16)]). As you
    # can see, we've adjusted some indices for ease-of-use.
    lists_of_indices = [*groups, base]        
    lists_of_clustered_indices = []

    for list_of_indices in lists_of_indices:
        if not list_of_indices:
            continue

        # We start off with a single cluster that is made up of the
        # first index. If the next index follows the first index, 
        # we continue the cluster. If it doesn't, we create a new cluster.
        clustered_indices = [[list_of_indices[0], list_of_indices[0] + 1]]
        
        for index in list_of_indices[1:]:
            if clustered_indices[-1][1] == index:
                clustered_indices[-1][1] = index + 1
            else:
                clustered_indices.append([index, index + 1])

        # Add Clustered Indices
        lists_of_clustered_indices.append(clustered_indices)

    lists_of_clustered_text = [[text[cluster[0]:cluster[1]] for cluster in clusters] for clusters in lists_of_clustered_indices]
    return ["".join(list_of_clustered_text) for list_of_clustered_text in lists_of_clustered_text]



def trim_text(text: str) -> str:
    # 1. Delete Inside and Outside Space
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([?.!,])", r"\1", text)
    text = text.strip()

    # 2. Delete Outside Non-Letters
    while text:
        start_len = len(text)
        if text and not text[0].isalnum():
            text = text[1:]
        if text and not text[-1].isalnum():
            text = text[:-1]
        if start_len == len(text):
            break
    
    return text



def clean_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s)
    s = regex.sub(r'(\p{Ll})(\p{Lu})', r'\1 \2', s)
    s = regex.sub(r'([\.,:;\)\]\}])([\p{Lu}\p{Ll}])', r'\1 \2', s)
    s = regex.sub(r'([\p{Lu}\p{Ll}])([\(\[\{]])', r'\1 \2', s)
    return s



def is_boundary(c):
    return c.isspace() or c in string.punctuation
