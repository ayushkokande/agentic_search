from typing import List, Dict

def rank_places(places: List[Dict]) -> List[Dict]:
    """
    Rank places by trust score (descending), and then by distance (ascending).
    """
    # Sort by (-trust, distance)
    ranked = sorted(
        places,
        key=lambda p: (-p.get("trust", 0.0), p.get("distance", float("inf")))
    )
    return ranked
