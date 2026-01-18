from langchain.tools import tool

@tool
def get_hours(place_name: str) -> str:
    """
    Stub to get business hours for a place.
    """
    # Dummy hours string
    return "9am - 5pm"
