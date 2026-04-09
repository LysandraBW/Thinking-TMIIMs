from typing import List
from spacy.tokens import Doc



def expand_unit(doc: Doc, il_unit: int, ir_unit: int, il_boundary: int, ir_boundary: int, speech: List[str] | None = None, literals: List[str] | None = None, include: bool = True, direction: str = 'BOTH', verbose: bool = False):    
    speech = speech or []
    literals = literals or []


    if il_unit > ir_unit:
        if verbose:
            print(f"Error: il_unit of {il_unit} greater than ir_unit of {ir_unit}")
        return None
    
    if direction in ['BOTH', 'LEFT'] and il_boundary > il_unit:
        if verbose:
            print(f"Error: il_unit of {il_unit} less than il_boundary of {il_boundary}")
        return None
    
    if direction in ['BOTH', 'RIGHT'] and ir_boundary < ir_unit:
        if verbose:
            print(f"Error: ir_unit of {ir_unit} greater than ir_boundary of {ir_boundary}")
        return None
    

    # Move Left
    if direction in ['BOTH', 'LEFT']:
        # The indices are inclusive, therefore, when 
        # the condition fails, il_unit will be equal
        # to il_boundary.
        while il_unit > il_boundary:
            # We assume that the current token is allowed,
            # and look to the token to the left.
            l_token = doc[il_unit-1]

            # If the token is invalid, we stop expanding.
            in_set = l_token.pos_ in speech or l_token.lower_ in literals

            # Case 1: include=False, in_set=True
            # If we're not meant to include the defined tokens, and the
            # current token is in that set, we stop expanding.
            # Case 2: include=True, in_set=False
            # If we're meant to include the defined tokens, and the current
            # token is not in that set, we stop expanding.
            # Case 3: include=in_set
            # If we're meant to include the defined tokens, and the current
            # token is in that set, we continue expanding. If we're not meant
            # to include the defined tokens, and the current token is not
            # in that set, we continue expanding.
            if include ^ in_set:
                break
            
            # Else, the left token is valid, and
            # we continue to expand.
            il_unit -= 1

    # Move Right
    if direction in ['BOTH', 'RIGHT']:
        # Likewise, when the condition fails,
        # ir_unit will be equal to the ir_boundary.
        # The ir_boundary is also inclusive.
        while ir_unit < ir_boundary:
            # Assuming that the current token is valid,
            # we look to the right to see if we can
            # expand.
            r_token = doc[ir_unit+1]

            # If the token is invalid, we stop expanding.
            in_set = r_token.pos_ in speech or r_token.lower_ in literals
            if include ^ in_set:
                break

            # Else, the token is valid and
            # we continue.
            ir_unit += 1


    assert il_unit >= il_boundary and ir_unit <= ir_boundary
    expanded_unit = doc[il_unit:ir_unit+1]
        
    return expanded_unit



def contract_unit(doc: Doc, il_unit: int, ir_unit: int, speech: List[str] | None = None, literals: List[str] | None = None, include: bool = True, direction: str = 'BOTH', verbose: bool = False): 
    speech = speech or []
    literals = literals or []


    if il_unit > ir_unit:
        if verbose:
            print(f"Error: il_unit of {il_unit} greater than ir_unit of {ir_unit}")
        return None
    

    # Move Right
    if direction in ['BOTH', 'LEFT']:
        while il_unit < ir_unit:
            # We must check if the current token is not allowed. If it's
            # not allowed, we contract (remove).
            token = doc[il_unit]

            # include = True means that we want the tokens that match
            # the speech and/or literals in the contracted unit.
            
            # include = False means that we don't want the tokens that
            # match the speech and/or literals in the contracted unit.
            
            # Case 1: include = True, in_set = True
            # We have a token that's meant to be included in the set.
            # However, we're contracting, which means we would end up
            # removing the token if we continue. Therefore, we break.
            
            # Case 2: include = False, in_set = False
            # We have a token that's not in the set which defines the
            # tokens that aren't meant to be included. Therefore, we 
            # have a token that is meant to be included. If we continue,
            # we would end up removing this token. Therefore, we break.
            
            # Default:
            # If we have a token that's in the set (in_set=True) of
            # tokens we're not supposed to include in the contracted 
            # unit (include=False), we need to remove it. Likewise, if
            # we have a token that's not in the set (in_set=False) of
            # tokens to include in the contracted unit (include=True),
            # we need to remove it.
            
            in_set = token.pos_ in speech or token.lower_ in literals
            if include == in_set:
                break

            # The token is valid, thus we continue.
            il_unit += 1

    # Move Left      
    if direction in ['BOTH', 'RIGHT']:
        while ir_unit > il_unit:
            token = doc[ir_unit]

            # The token is invalid and we
            # stop contracting.
            in_set = token.pos_ in speech or token.lower_ in literals
            if include == in_set:
                break

            # The token is valid and we continue.
            ir_unit -= 1


    assert il_unit <= ir_unit
    contracted_unit = doc[il_unit:ir_unit+1]
    
    return contracted_unit