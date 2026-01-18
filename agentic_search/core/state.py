from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict
from langchain_core.messages import BaseMessage

@dataclass
class SearchState:
    # core
    query: str = ""
    domain: str = ""
    expanded_query: str = ""
    user_location: str = ""

    # messaging / trace
    messages: List[BaseMessage] = field(default_factory=list)

    # intermediate artifacts
    places: List[Dict[str, Any]] = field(default_factory=list)
    filtered: List[Dict[str, Any]] = field(default_factory=list)
    ranked: List[Dict[str, Any]] = field(default_factory=list)

    # outputs
    final_results: List[Dict[str, Any]] = field(default_factory=list)

    # generic
    results: List[Any] = field(default_factory=list)   # optional—keep only if you still use it
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)
