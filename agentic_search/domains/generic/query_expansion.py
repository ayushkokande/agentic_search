def expand_query(query: str) -> str:
    """
    Simple query expansion for generic domain.
    For demo, we just append a common phrase.
    """
    return f"{query} near me"
