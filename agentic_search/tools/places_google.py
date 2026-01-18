from langchain.tools import tool
from typing import List, Dict

@tool
def search_places(query: str) -> List[Dict]:
    """
    Stub for Google Places search.
    Returns dummy places matching the query.
    """
    # Example stub results (in reality, call Google Places API here)
    return [
        {"name": f"{query.title()} Place 1", "address": "123 Main St", "distance": 1.2},
        {"name": f"{query.title()} Place 2", "address": "456 Elm St",  "distance": 3.4},
        {"name": f"{query.title()} Place 3", "address": "789 Oak Ave",  "distance": 5.6},
    ]
