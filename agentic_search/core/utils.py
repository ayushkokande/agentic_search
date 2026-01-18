from typing import List, Any

def dedupe_places(places: List[Any]) -> List[Any]:
    """
    Remove duplicate places by name.
    """
    seen = set()
    unique = []
    for place in places:
        name = place.get("name")
        if name and name not in seen:
            seen.add(name)
            unique.append(place)
    return unique
