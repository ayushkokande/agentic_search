from langchain.tools import tool

@tool
def compute_commute(place_name: str, user_location: str) -> str:
    """
    Stub for Google Directions / commute time.
    """
    # Dummy commute time calculation
    return f"{10 + len(place_name) % 30} mins"
