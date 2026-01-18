import os
import requests
from langchain.tools import tool

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


def _places_text_search(place_name: str) -> str | None:
    """
    Returns the best matching place_id for a place_name using Places Text Search.
    """
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {
        "query": place_name,
        "key": GOOGLE_MAPS_API_KEY,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "OK" or not data.get("results"):
        return None

    return data["results"][0].get("place_id")


def _place_details_hours(place_id: str) -> dict | None:
    """
    Returns opening_hours from Place Details.
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,opening_hours,utc_offset_minutes",  # keep minimal to reduce cost
        "key": GOOGLE_MAPS_API_KEY,
    }

    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if data.get("status") != "OK":
        return None

    return data.get("result")


@tool
def get_hours(place_name: str) -> str:
    """
    Get business hours using Google Places API.
    Uses: Text Search -> Place Details -> opening_hours.weekday_text.

    Returns:
        A readable string like:
        "Mon: 9:00 AM – 5:00 PM | Tue: 9:00 AM – 5:00 PM | ..."
    """
    if not GOOGLE_MAPS_API_KEY:
        return "Error: GOOGLE_MAPS_API_KEY is not set."

    if not place_name:
        return "Error: place_name is required."

    try:
        place_id = _places_text_search(place_name)
        if not place_id:
            return f"Hours unavailable: No matching place found for '{place_name}'."

        details = _place_details_hours(place_id)
        if not details:
            return f"Hours unavailable: Could not fetch details for '{place_name}'."

        opening_hours = details.get("opening_hours")
        if not opening_hours:
            return f"Hours unavailable: '{details.get('name', place_name)}' has no opening hours listed."

        # Most useful representation
        weekday_text = opening_hours.get("weekday_text")
        if weekday_text:
            return " | ".join(weekday_text)

        # Fallback: open_now only
        open_now = opening_hours.get("open_now")
        if open_now is not None:
            return f"Currently {'open' if open_now else 'closed'}."

        return f"Hours unavailable: No readable hours returned for '{details.get('name', place_name)}'."

    except requests.RequestException as e:
        return f"Error: Places API request failed: {e}"
