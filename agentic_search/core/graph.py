print("USING graph.py FROM:", __file__)

import json
from typing import Dict

from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from core.state import SearchState
from config import OPENAI_API_KEY
from core.prompts import PROMPT_PARSE, PROMPT_RELAX
from core.policies import decide_relax
from core.scoring import rank_places
from core.utils import dedupe_places

from domains.generic.ontology import *
from domains.generic.query_expansion import expand_query as gen_expand_query
from domains.generic.constraints import apply_constraints as gen_apply_constraints
from domains.generic.postprocess import postprocess as gen_postprocess
from domains.healthcare.ontology import *
from domains.healthcare.query_expansion import expand_query as hc_expand_query
from domains.healthcare.constraints import apply_constraints as hc_apply_constraints
from domains.healthcare.postprocess import postprocess as hc_postprocess

from tools.places_google import search_places
from tools.commute_google import compute_commute
from tools.hours_google import get_hours
from tools.trust import assess_trust
from tools.cache import get_cached, set_cached

# Global LLM instance - will be set when build_agent_graph is called
_llm = None

def parse_query(state: SearchState) -> Dict:
    global _llm
    query = state.messages[-1].content
    # Call LLM to parse domain and keywords
    response: AIMessage = _llm.invoke([HumanMessage(content=f"{PROMPT_PARSE}\nUser query: {query}")])
    content = response.content.strip().lower()
    # Very simple parsing: decide domain by keyword
    domain = "healthcare" if any(term in query.lower() for term in HEALTHCARE_TERMS) else "generic"
    # For simplicity, we ignore keywords extraction
    expanded = query
    state.query = query
    return {"domain": domain, "expanded_query": expanded, "messages": [response]}

def expand_query(state: SearchState) -> Dict:
    domain = state["domain"]
    query = state["expanded_query"]
    if domain == "healthcare":
        new_query = hc_expand_query(query)
    else:
        new_query = gen_expand_query(query)
    return {"expanded_query": new_query}

def retrieve_places(state: SearchState) -> Dict:
    query = state.get("expanded_query") or state.get("query", "")
    if not query:
        return {"places": []}
    cached = get_cached(query)
    if cached is not None:
        return {"places": cached}
    results = search_places.invoke({"query": query}) or []
    set_cached(query, results)
    tool_msg = ToolMessage(
        name="search_places",
        content=json.dumps(results, ensure_ascii=True),
        tool_call_id="search_places"
    )
    return {"places": results, "messages": [tool_msg]}

def enrich(state: SearchState) -> Dict:
    places = state.get("places", [])
    user_loc = state.get("user_location", "current location")
    enriched = []
    for place in places:
        name = place["name"]
        # Compute commute and hours via tools
        commute = compute_commute.invoke({"place_name": name, "user_location": user_loc})
        hours = get_hours.invoke({"place_name": name})
        trust = assess_trust.invoke({"place_name": name})
        enriched.append({
            "name": name,
            "address": place.get("address", ""),
            "distance": place.get("distance", 0.0),
            "open_hours": hours,
            "trust": trust,
            "commute": commute
        })
    # Remove duplicates
    enriched_unique = dedupe_places(enriched)
    return {"filtered": enriched_unique}  # reuse "filtered" key for pipeline

def filter_results(state: SearchState) -> Dict:
    places = state.get("filtered", [])
    domain = state["domain"]
    if domain == "healthcare":
        filtered = hc_apply_constraints(places)
    else:
        filtered = gen_apply_constraints(places)
    return {"filtered": filtered}

def rank_results(state: SearchState) -> Dict:
    places = state.get("filtered", [])
    ranked = rank_places(places)
    return {"ranked": ranked}

def relax_query(state: SearchState) -> Dict:
    global _llm
    response: AIMessage = _llm.invoke([HumanMessage(content=f"{PROMPT_RELAX}\nOriginal query: {state['query']}")])
    new_query = response.content.strip()
    return {"expanded_query": new_query, "messages": [response]}

def postprocess_results(state: SearchState) -> Dict:
    final = state.get("ranked", [])
    domain = state["domain"]
    if domain == "healthcare":
        final = hc_postprocess(final)
    else:
        final = gen_postprocess(final)
    return {"final_results": final}

def build_agent_graph() -> StateGraph:
    """
    Build and return the LangGraph StateGraph for the search agent.
    """

    # Initialize LLM (with API key from config)
    global _llm
    _llm = ChatOpenAI(temperature=0, api_key=OPENAI_API_KEY)

    # Define state graph
    graph = StateGraph(SearchState)

    # Build graph nodes
    graph.add_node("parse_query", parse_query)
    graph.add_node("expand_query", expand_query)
    graph.add_node("retrieve", retrieve_places)
    graph.add_node("enrich", enrich)
    graph.add_node("filter_results", filter_results)
    graph.add_node("rank_results", rank_results)
    graph.add_node("relax_query", relax_query)
    graph.add_node("postprocess_results", postprocess_results)

    # Define edges (flow)
    graph.add_edge(START, "parse_query")
    graph.add_edge("parse_query", "expand_query")
    graph.add_edge("expand_query", "retrieve")
    graph.add_edge("retrieve", "enrich")
    graph.add_edge("enrich", "filter_results")
    graph.add_edge("filter_results", "rank_results")

    # After ranking, decide to relax or finish
    graph.add_conditional_edges(
        "rank_results",
        decide_relax,
        {"relax": "relax_query", "end": "postprocess_results"}
    )
    # If we relax, go back to retrieval with new query
    graph.add_edge("relax_query", "retrieve")
    # Postprocess then end
    graph.add_edge("postprocess_results", END)

    # Compile graph
    return graph.compile()
