import os
import json
import regex
import pickle
import sqlite3
import ahocorasick
import pandas as pd
from typing import Any, Callable
from .names_patterns import *
from .inflections import *
from pathlib import Path


conn = sqlite3.connect(Path(__file__).parent / '../../data/col.db')
# conn.execute("ANALYZE NameUsage")
# conn.execute("PRAGMA cache_size = -1000000")


def load_data(path: str | Path, load: Callable[[], Any], *, force: bool = False) -> Any:
    data = None
    if not force and os.path.exists(path):
        with open(path, "rb") as file:
            data = pickle.load(file)
    else:
        data = load()
        with open(path, "wb") as file:
            pickle.dump(data, file, pickle.HIGHEST_PROTOCOL)
    return data



# ---------------- #
# Load Scientifics #
# ---------------- #
def load_scientifics():
    df = pd.read_sql(f"""
        SELECT *
        FROM NameUsage
    """, conn)

    cols = [
        ["kingdom", "col:kingdom"],
        ["phylum", "col:phylum"],
        ["subphylum", "col:subphylum"],
        ["class", "col:class"],
        ["subclass", "col:subclass"],
        ["order", "col:order"],
        ["suborder", "col:suborder"],
        ["superfamily", "col:superfamily"],
        ["family", "col:family"],
        ["subfamily", "col:subfamily"],
        ["genus", "col:genus"],
        ["subgenus", "col:subgenus"],
        ["genericName", "col:genericName"],
        ["specificEpithet", "col:specificEpithet"],
        ["intraspecificEpithet", "col:infraspecificEpithet"],
        ["species", "col:species"],
        ["scientificName", "col:scientificName"]
    ]
    
    data = []
    for col in cols:
        vals = set()
        
        for val in df[col[1]].tolist():
            if not val:
                continue
            val = val.lower()
            # The sub-genus is placed inside
            # '(...)', so we need to capture it.
            if col[0] == "subgenus":
                match = regex.match(r'^([A-Za-z]+)\s\(([A-Za-z]+)\)$', val)
                vals.add(val if not match else match.group(2))
            else:
                vals.add(val)
        
        data.append({
            'label': col[0],
            'column': col[1],
            'values': vals
        })

    del df
    return data



# ---------------- #
# Load Vernaculars #
# ---------------- #
def load_vernaculars():
    df = pd.read_sql(f"""
        SELECT "col:name" 
        FROM VernacularName 
        WHERE "col:language" = 'eng'
    """, conn)

    names = [{name} | get_inflections(name, None) for name in df["col:name"].tolist() if name]
    names = set().union(*names)

    # Add More Names from File
    with open(Path(__file__).parent / '../../data/hard/vernaculars.json') as f:
        names = names | set(json.load(f))
    
    return names



# ----------------- #
# Load Mapped Names #
# ----------------- #
def load_mapped_names():
    df = pd.read_sql(f'''
        SELECT *
        FROM MappedName
    ''', conn)

    mapped_names = {}
    
    for i, row in df.iterrows():
        names = [name for name in [row.ScientificName, row.VernacularName, row.Genus] if name]

        for i, name in enumerate(names):
            forms = [name.lower()]
        
            # Add Abbreviated Scientific Name
            if i == 0 and (abbrevs := abbreviate(name)):
                forms.append(abbrevs[-1].lower())

            for form in forms:
                if form not in mapped_names:
                    mapped_names[form] = set()
                
                for col in [col for col in row if col]:
                    mapped_names[form].add(col.lower())
    
    del df
    return mapped_names



# ---------- #
# Load Roles #
# ---------- #
def load_roles():
    roles = None
    with open(Path(__file__).parent / '../../data/hard/roles.json') as f:
        roles = set(json.load(f))
    return roles



# -------------- #
# Load All Names #
# -------------- #
def load_all_names(scientifics, vernaculars, roles):
    all_names = ahocorasick.Automaton()
     
    # Scientific Names
    for scientific in scientifics:
        for val in scientific['values']:
            all_names.add_word(val, {
                'key': val,
                'label': 's',
            })
    
     # Role
    for role in roles:
        all_names.add_word(role, {
            'key': role,
            'label': 'r'
        })
    
    # Vernacular Names
    for name in vernaculars:
        all_names.add_word(name, {
            'key': name,
            'label': 'v'
        })
    
    all_names.make_automaton()
    return all_names



# ----------------- #
# Load Interactions #
# ----------------- #
def load_interactions():
    with open(Path(__file__).parent / '../../data/hard/interaction.json') as f:
        words = set(json.load(f))
        interactions = ahocorasick.Automaton()
        for word in words:
            interactions.add_word(word, word)    
        interactions.make_automaton()
        return interactions



# ------------ #
# Load Actions #
# ------------ #
def load_actions():
    with open(Path(__file__).parent / '../../data/hard/actions.json') as f:
        words = set(json.load(f))
        actions = ahocorasick.Automaton()
        for word in words:
            actions.add_word(word, word)    
        actions.make_automaton()
        return actions



# --------- #
# Load Data #
# --------- #
print('Loading Mapped Names...')
mapped_names = load_data(Path(__file__).parent / "../../data/NamesMapped.pickle", load_mapped_names, force=False)
print(f'# of Mapped Names: {len(mapped_names)}\n')


print('Loading Vernaculars...')
vernaculars = load_data(Path(__file__).parent / "../../data/Vernaculars.pickle", load_vernaculars, force=False)
print(f'# of Vernacular Names: {len(vernaculars)}\n')


print('Loading Scientfics...')
scientifics = load_data(Path(__file__).parent / "../../data/Scientifics.pickle", load_scientifics, force=False)
print(f'# of Scientific Groups: {len(scientifics)}\n')


print('Loading Roles...')
roles = load_roles()
print(f'# of Roles: {len(roles)}\n')


print('Loading Interactions...')
interactions = load_interactions()
print(f'# of Interactions: {len(interactions)}\n')


print('Loading Actions...')
actions = load_actions()
print(f'# of Actions: {len(actions)}\n')


print('Loading All Names...')
all_names = load_data(Path(__file__).parent / "../../data/NamesAll.pickle", lambda: load_all_names(
    roles=roles,
    scientifics=scientifics, 
    vernaculars=vernaculars
), force=False)
print(f'# of Names: {len(all_names)}\n')


conn.close()


# --------- #
# Functions #
# --------- #
@lru_cache(maxsize=64)
def in_roles(s: str) -> bool:
    return s.lower() in roles



@lru_cache(maxsize=64)
def in_vernacular(s: str) -> bool:
    return s.lower() in vernaculars



@lru_cache(maxsize=64)
def in_scientific(s: str) -> str | None:
    s = s.lower()
    for scientific in scientifics:
        if s in scientific['values']:
            return scientific['label']
    return None



@lru_cache(maxsize=64)
def is_taxa(s: str) -> bool:
    return re_taxa(s) and (data := all_names.get(s.lower(), None)) and data['label'] == 's'



@lru_cache(maxsize=64)
def is_taxonomic(s: str) -> bool:
    if not re_taxonomic_name(s):
        return False
    return (data := all_names.get(s.lower(), None)) and data['label'] == 's'



@lru_cache(maxsize=64)
def is_taxonomic_notation(s: str) -> str | None:
    name = re_taxonomic_notation(s)
    if not name:
        return None
    return all_names.get(name.lower(), None)



def get_substitutions(s: str) -> list[str]:
    return mapped_names.get(s.lower(), [])



bacteria_kingdoms = {
    'pseudomonadati', 
    'bacillati', 
    'methanobacteriati', 
    'fusobacteriati', 
    'thermotogati'
}



def connect():
    conn = sqlite3.connect(Path(__file__).parent / '../../data/col.db')
    conn.execute("PRAGMA cache_size = -1000000")
    return conn



@lru_cache(maxsize=128)
def names_related(s1: str, s2: str, conn: sqlite3.Connection) -> bool:
    buffer = []

    s1 = s1.lower()
    s2 = s2.lower()
    
    if s1 == s2:
        return True
    
    used_s1 = False
    used_s2 = False
    
    for scientific in scientifics:
        if used_s1 and used_s2:
            break
        
        if not used_s1 and s1 in scientific['values']:
            buffer.append((s1, scientific['column']))
            used_s1 = True
            continue

        if not used_s2 and s2 in scientific['values']:
            buffer.append((s2, scientific['column']))
            used_s2 = True
            continue
        
    if len(buffer) != 2:
        return False
        
    (t1_val, t1_col), (t2_val, t2_col) = buffer
    
    # Bacteria
    # We need a different method of determining whether
    # something is related to bacteria, as bacteria is
    # not very defined in the database.
    if t1_val == 'bacteria' and t2_col in ['col:scientificName', 'col:species']:
        q = f'''
            SELECT LOWER("col:kingdom")
            FROM NameUsage
            WHERE LOWER("{t2_col}") = \'{t2_val}\'
            LIMIT 1
        '''
        output = conn.execute(q).fetchone()
        output = None if not output or not output[0] else output[0].lower()
        if output in bacteria_kingdoms:
            return True
    

    q = f'''
        SELECT 1
        FROM NameUsage
        WHERE LOWER("{t2_col}") = \'{t2_val}\' AND LOWER("{t1_col}") = \'{t1_val}\'
        LIMIT 1
    '''

    return bool(conn.execute(q).fetchone())