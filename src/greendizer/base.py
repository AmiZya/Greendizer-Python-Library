def is_empty_or_none(s):
    '''
    Returns a value indicating whether the string is empty or none
    @param s:str String to check.
    @return: bool
    '''
    return not s or len(s) == 0


def extract_id_from_uri(s):
    '''
    Returns the ID section of an URI.
    @param s:str URI
    @return: str
    '''
    return [ item for item in s.split("/") if not is_empty_or_none(item) ][-1]
