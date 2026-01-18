import pytest
from agentic_search.core.scoring import rank_places

def test_rank_by_trust():
    places = [
        {"name": "A", "trust": 0.5, "distance": 10},
        {"name": "B", "trust": 0.9, "distance": 5},
        {"name": "C", "trust": 0.2, "distance": 1}
    ]
    ranked = rank_places(places)
    assert ranked[0]["name"] == "B"
    assert ranked[1]["name"] == "A"
    assert ranked[2]["name"] == "C"
