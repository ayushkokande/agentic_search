from agentic_search.core.utils import dedupe_places

def test_dedupe_places():
    places = [
        {"name": "Place A", "address": "X"},
        {"name": "Place B", "address": "Y"},
        {"name": "Place A", "address": "Z"}  # duplicate name
    ]
    unique = dedupe_places(places)
    assert len(unique) == 2
    names = {p["name"] for p in unique}
    assert names == {"Place A", "Place B"}
