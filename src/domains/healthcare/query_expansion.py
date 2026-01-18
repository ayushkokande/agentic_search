def expand_query(query: str) -> str:
    """
    Simple expansion for healthcare domain.
    If terms like 'doctor' present, add synonyms.
    """
    if "doctor" in query.lower():
        return query + " physician clinic"
    return query + " healthcare"
