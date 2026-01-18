from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any

class Place(BaseModel):
    place_id: str
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    rating: Optional[float] = None
    user_ratings_total: Optional[int] = None
    url: Optional[str] = None
    source: str = "google"
    raw: Dict[str, Any] = Field(default_factory=dict)

class SearchState(BaseModel):
    results: List[Any] = Field(default_factory=list)
