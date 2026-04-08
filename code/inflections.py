import inflect
from typing import Any, Set
from functools import lru_cache


inflector = inflect.engine()


@lru_cache(maxsize=64)
def plural(s: Any) -> str | None:
    try:
        return inflector.plural(s) or None
    except Exception:
        return None


@lru_cache(maxsize=64)
def singular(s: Any) -> str | None:
    try:
        return inflector.singular_noun(s) or None
    except Exception:
        return None


@lru_cache(maxsize=64)
def get_inflections(s: str, tag: str | None) -> Set[str]:
    inflections = set()
    if (not tag or tag == 'NN' or tag == 'NNP') and (inf := plural(s)) and inf != s:
        inflections.add(inf)
    if (not tag or tag == 'NNS' or tag == 'NNPS') and (inf := singular(s)) and inf != s:
        inflections.add(inf)
    return inflections
