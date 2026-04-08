import regex
from typing import List
from functools import lru_cache



binomial = r'((^\p{Lu}(\.|\p{Ll}+))\s(sp\.|spp\.|(\p{Ll}(\.|\p{Ll}+))))'
trinomial = r'((^\p{Lu}(\.|\p{Ll}+))\s(\p{Ll}(\.|\p{Ll}+)\s)(sp\.|spp\.|(\p{Ll}(\.|\p{Ll}+))))'



@lru_cache(maxsize=128)
def re_taxa(s: str) -> bool:
    return bool(regex.match(r'^\p{Lu}\p{Ll}+$', s))



@lru_cache(maxsize=128)
def re_taxonomic_name(s: str) -> bool:
    return bool(regex.match(r'^(\p{Lu}(\.|\p{Ll}+))\s(\p{Ll}(\.|\p{Ll}+)\s)?\p{Ll}(\.|\p{Ll}+)$', s))



@lru_cache(maxsize=128)
def re_taxonomic_notation(s: str) -> str | None:
    if match := regex.match(rf'{binomial}\s((\p{{Lu}}|\(|et al|sensu|nov|comb|stat|syn|s\.s\.|s\.l\.).*)$', s):
        return match.group(1)

    if match := regex.match(rf'{trinomial}\s((\p{{Lu}}|\(|et al|sensu|nov|comb|stat|syn|s\.s\.|s\.l\.).*)$', s):
        return match.group(1)

    return None



@lru_cache(maxsize=128)
def abbreviate(s: str) -> List[str]:
    name = s if re_taxonomic_name(s) else re_taxonomic_notation(s)
    if not name:
        return []
    
    res = []
    name = name.split()
    
    if len(name) >= 2:
        res.append(f'{name[0][0].upper()}. {name[1].lower()}')
    
    if len(name) == 3:
        res.append(f'{name[0][0].upper()}. {name[1][0].lower()}. {name[2].lower()}')
    
    return res