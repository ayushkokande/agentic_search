import os
import requests
from typing import List, Dict, Any, Optional
from langchain.tools import tool

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

SCHEMA_VERSION = 1
SOURCE = "google_places_textsearch"


def _normalized_place(
    *,
    ok: bool,
    name: str = "",
    place_id: str = "",
    address: str = "",
    rating: Optional[float] = None,
    total_ratings: Optional[int] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    status: Optional[str] = None,
    error: Optional[str] = None,
    raw: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a canonical place dict with a stable schema."""
    return {
        "ok": ok,
        "schema_version": SCHEMA_VERSION,
        "source": SOURCE,

        # Canonical place fields (always present)
        "name": name or "",
        "place_id": place_id or "",
        "address": address or "",
        "rating": rating,
        "total_ratings": total_ratings,
        "lat": lat,
        "lng": lng,

        # Diagnostics (always present)
        "status": status,
        "error": error,
        "raw": raw or {},
    }


def _to_float(x: Any) -> Optional[float]:
    try:
        return float(x) if x is not None else None
    except (TypeError, ValueError):
        return None


def _to_int(x: Any) -> Optional[int]:
    try:
        return int(x) if x is not None else None
    except (TypeError, ValueError):
        return None


@tool
def search_places(query: str) -> List[Dict[str, Any]]:
    """
    Search places using Google Places Text Search API.

    Returns a list of normalized place objects. Even error cases return
    a list with a single normalized object with ok=False and error filled.
    """
    if not GOOGLE_MAPS_API_KEY:
        return [
            _normalized_place(
                ok=False,
                status="CONFIG_ERROR",
                error="GOOGLE_MAPS_API_KEY is not set.",
                raw={"query": query},
            )
        ]

    if not query or not query.strip():
        return [
            _normalized_place(
                ok=False,
                status="INPUT_ERROR",
                error="query is required.",
                raw={"query": query},
            )
        ]

    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": GOOGLE_MAPS_API_KEY}

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        return [
            _normalized_place(
                ok=False,
                status="HTTP_ERROR",
                error=f"Places API request failed: {e}",
                raw={"query": query},
            )
        ]
    except ValueError as e:
        # JSON decode error
        return [
            _normalized_place(
                ok=False,
                status="PARSE_ERROR",
                error=f"Places API response was not valid JSON: {e}",
                raw={"query": query},
            )
        ]

    status = data.get("status")
    if status != "OK":
        # REQUEST_DENIED, OVER_QUERY_LIMIT, ZERO_RESULTS, INVALID_REQUEST, etc.
        return [
            _normalized_place(
                ok=False,
                status=status,
                error=data.get("error_message") or f"Places API status={status}",
                raw=data,
            )
        ]

    results = data.get("results") or []
    places: List[Dict[str, Any]] = []

    for r in results[:10]:
        loc = ((r.get("geometry") or {}).get("location") or {})

        name = r.get("name") or ""
        place_id = r.get("place_id") or ""
        address = r.get("formatted_address") or r.get("vicinity") or ""

        # If Google gives a malformed entry, keep it but mark ok=False.
        # You can alternatively skip it.
        ok = bool(name and place_id)

        places.append(
            _normalized_place(
                ok=ok,
                name=name,
                place_id=place_id,
                address=address,
                rating=_to_float(r.get("rating")),
                total_ratings=_to_int(r.get("user_ratings_total")),
                lat=_to_float(loc.get("lat")),
                lng=_to_float(loc.get("lng")),
                status="OK" if ok else "PARTIAL_RESULT",
                error=None if ok else "Missing required fields: name/place_id",
                raw=r,
            )
        )

    # If OK but no results, return a normalized “empty result” object.
    if not places:
        return [
            _normalized_place(
                ok=False,
                status="ZERO_RESULTS",
                error="No places found for query.",
                raw=data,
            )
        ]

    return places
