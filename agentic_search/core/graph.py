print("USING graph.py FROM:", __file__)

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from typing import Dict

from agentic_search.core.types import SearchState
from agentic_search.core.prompts import PROMPT_PARSE, PROMPT_EXPAND, PROMPT_RELAX
from agentic_search.core.policies import decide_relax
from agentic_search.core.scoring import rank_places
from agentic_search.core.utils import dedupe_places

import agentic_search.domains.generic.ontology as gen_ont
import agentic_search.domains.generic.query_expansion as gen_expand
import agentic_search.domains.generic.constraints as gen_constraints
import agentic_search.domains.generic.postprocess as gen_post
import agentic_search.domains.healthcare.ontology as hc_ont
import agentic_search.domains.healthcare.query_expansion as hc_expand
import agentic_search.domains.healthcare.constraints as hc_constraints
import agentic_search.domains.healthcare.postprocess as hc_post

from agentic_search.tools.places_google import search_places
from agentic_search.tools.commute_google import compute_commute
from agentic_search.tools.hours_google import get_hours
from agentic_search.tools.trust import assess_trust
from agentic_search.tools.cache import get_cached, set_cached

def build_agent_graph() -> StateGraph:
    """
    Build and return the LangGraph StateGraph for the search agent.
    """

    # Initialize LLM (with API key from config)
    llm = ChatOpenAI(temperature=0)

    # Define state graph
    graph = StateGraph(SearchState)

    # Node: Parse the query (determine domain, keywords)
    def parse_query(state: SearchState) -> Dict:
        query = state["messages"][-1].content
        # Call LLM to parse domain and keywords
        response: AIMessage = llm.invoke([HumanMessage(content=f"{PROMPT_PARSE}\nUser query: {query}")])
        content = response.content.strip().lower()
        # Very simple parsing: decide domain by keyword
        domain = "healthcare" if any(term in query.lower() for term in hc_ont.HEALTHCARE_TERMS) else "generic"
        # For simplicity, we ignore keywords extraction
        expanded = query
        return {"domain": domain, "expanded_query": expanded, "messages": [response]}

    # Node: Expand the query using domain-specific logic
    def expand_query(state: SearchState) -> Dict:
        domain = state["domain"]
        query = state["expanded_query"]
        if domain == "healthcare":
            new_query = hc_expand.expand_query(query)
        else:
            new_query = gen_expand.expand_query(query)
        return {"expanded_query": new_query}

    # Node: Retrieve places (using stubbed Google Places), with caching
    # We use ToolNode for the search_places tool
    # Note: Graph automatically uses state["expanded_query"] as input for the tool
    tool_node_search = ToolNode([search_places])

    # Node: Enrich results with hours, commute, trust
    def enrich(state: SearchState) -> Dict:
        places = state.get("places", [])
        user_loc = state.get("user_location", "current location")
        enriched = []
        for place in places:
            name = place["name"]
            # Compute commute and hours via tools (call them directly as functions)
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

    # Node: Filter by domain constraints
    def filter_results(state: SearchState) -> Dict:
        places = state.get("filtered", [])
        domain = state["domain"]
        if domain == "healthcare":
            filtered = hc_constraints.apply_constraints(places)
        else:
            filtered = gen_constraints.apply_constraints(places)
        return {"filtered": filtered}

    # Node: Rank results
    def rank_results(state: SearchState) -> Dict:
        places = state.get("filtered", [])
        ranked = rank_places(places)
        return {"ranked": ranked}

    # Node: Decide whether to relax constraints
    # This uses the policy function
    # It should return either "relax" or "end"
    # We'll hook it up in conditional edges.

    # Node: Relax query
    def relax_query(state: SearchState) -> Dict:
        response: AIMessage = llm.invoke([HumanMessage(content=f"{PROMPT_RELAX}\nOriginal query: {state['query']}")])
        new_query = response.content.strip()
        return {"expanded_query": new_query, "messages": [response]}

    # Node: Final postprocessing of results
    def postprocess_results(state: SearchState) -> Dict:
        final = state.get("ranked", [])
        domain = state["domain"]
        if domain == "healthcare":
            final = hc_post.postprocess(final)
        else:
            final = gen_post.postprocess(final)
        return {"final_results": final}

    # Build graph nodes
    graph.add_node("parse_query", parse_query)
    graph.add_node("expand_query", expand_query)
    graph.add_node("retrieve", tool_node_search)  # ToolNode for search_places
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
