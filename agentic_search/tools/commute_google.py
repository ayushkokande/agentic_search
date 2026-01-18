import os
import re
import requests
from langchain.tools import tool

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_DISTANCE_MATRIX_API_KEY")

_LATLNG_RE = re.compile(r"^\s*-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?\s*$")


def _is_latlng(s: str) -> bool:
    return bool(_LATLNG_RE.match(s or ""))


@tool
def compute_commute(place_name: str, user_location: str) -> str:
    """
    Compute commute time using Google Distance Matrix API.

    Args:
        place_name: Destination (address or a place name string).
        user_location: Origin (address or "lat,lng").

    Returns:
        A human-readable duration like "17 mins" (or a clear error string).
    """
    if not GOOGLE_MAPS_API_KEY:
        return "Error: GOOGLE_MAPS_API_KEY is not set."

    if not place_name or not user_location:
        return "Error: place_name and user_location are required."

    # Distance Matrix expects origins/destinations as addresses or lat,lng.
    # If you have a Place ID for destination, use 'place_id:XXXX' format.
    origins = user_location.strip()
    destinations = place_name.strip()

    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origins,
        "destinations": destinations,
        "key": GOOGLE_MAPS_API_KEY,
        "mode": "driving",          # change to "walking", "bicycling", "transit" as needed
        "units": "metric",          # or "imperial"
        # "departure_time": "now",   # uncomment for live traffic (requires billing + supported regions)
        # "traffic_model": "best_guess",
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return f"Error: Distance Matrix request failed: {e}"

    # Top-level API status
    status = data.get("status")
    if status != "OK":
        # Common: REQUEST_DENIED (billing/API not enabled/restrictions), OVER_QUERY_LIMIT, INVALID_REQUEST
        err_msg = data.get("error_message", "")
        return f"Error: Distance Matrix API status={status}. {err_msg}".strip()

    rows = data.get("rows", [])
    if not rows or not rows[0].get("elements"):
        return "Error: No elements returned from Distance Matrix."

    element = rows[0]["elements"][0]
    element_status = element.get("status")
    if element_status != "OK":
        # Common: NOT_FOUND, ZERO_RESULTS
        return f"Error: No route found (status={element_status})."

    # Duration (normal) and Duration in traffic (if departure_time=now)
    duration = element.get("duration", {}).get("text")
    duration_in_traffic = element.get("duration_in_traffic", {}).get("text")

    # Prefer traffic-aware duration when available
    return duration_in_traffic or duration or "Error: Duration not available."
