from typing import TypedDict, Annotated, List
from langchain_core import HumanMessage, AIMessage, ToolMessage
from langgraph.graph.message import add_messages

# Define the structure of a Place result
class Place(TypedDict):
    name: str
    address: str
    distance: float
    open_hours: str
    trust: float

# Define the overall graph state
class SearchState(TypedDict):
    # Store conversation and trace messages (human, AI, tool)
    messages: Annotated[List, add_messages]

    # Input query and domain
    query: str
    domain: str  # e.g., 'generic' or 'healthcare'
    expanded_query: str  # after query expansion
    user_location: str  # optional for proximity (can default to "current location")
    
    # Retrieved places and subsequent lists
    places: List[Place]        # initial retrieval results
    filtered: List[Place]      # after applying constraints
    ranked: List[Place]        # after ranking
    final_results: List[Place] # after post-processing (output)
