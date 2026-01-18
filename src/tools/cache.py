_cache = {}

def get_cached(query: str):
    """Retrieve cached results for a query."""
    return _cache.get(query)

def set_cached(query: str, results):
    """Cache the results for a query."""
    _cache[query] = results
