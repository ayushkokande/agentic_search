from langchain.tools import tool

@tool
def assess_trust(place_name: str) -> float:
    """
    Stub to assess trustworthiness of a place (e.g., user ratings).
    """
    # Dummy trust score between 0 and 1
    return 0.8
