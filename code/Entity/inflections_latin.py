import re
from typing import Any, Set
from functools import lru_cache


latin_inflections = [
    ('us', 'i'), 
    ('um', 'a'), 
    ('a', 'ae'), 
    ('is', 'es'), 
    ('x', 'ges'), 
    ('on', 'a'), 
    ('os', 'oi'), 
    ('ma', 'mata'),
    ('ex', 'ices'), 
    ('ix', 'ices'),
    ('pus', 'podes'), 
]


@lru_cache(maxsize=64)
def get_inflections_latin(s: str) -> Set[str]:
    inflections = set()

    for k, v in latin_inflections:
        inf = re.sub(rf'{k}$', v, s)
        if inf != s:
            inflections.add(inf)
        
        inf = re.sub(rf'{v}$', k, s)
        if inf != s:
            inflections.add(inf)
        
    return inflections
