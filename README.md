# Agentic Search

This project implements an **agentic search loop** over an unrestricted space using LangChain and LangGraph. The agent accepts a user query (generic or healthcare), decomposes and plans sub-tasks, retrieves and enriches information (stubbed Google Places & Directions APIs), filters by domain constraints, ranks results, and optionally relaxes constraints for further search. The full planning→retrieval→enrichment→filtering→ranking→relaxation loop is orchestrated via LangGraph, with each step represented as a node in the graph. 

We use `ChatOpenAI` for LLM-based steps (prompt parsing, query expansion, relaxation, etc.) and stub functions for data tools (places search, commute, hours). The Streamlit interface (`app.py`) runs the agent and displays both the **final results** and the detailed **agent trace** (state updates and messages at each step). The design follows approaches for complex query answering and agentic RAG outlined in recent LangChain resources:contentReference[oaicite:2]{index=2}:contentReference[oaicite:3]{index=3}.

**Features:**
- Modular architecture with `core`, `tools`, `domains`, and `ui` modules.
- Stubbed Google API tools (`places_google.py`, `commute_google.py`, `hours_google.py`) – can be replaced with real API calls.
- Domain-specific modules (`generic` and `healthcare`) for ontology, query expansion, constraints, and post-processing.
- LangGraph StateGraph for orchestrating nodes and conditional logic.
- Streamlit UI for input query and real-time trace output.
- Example unit tests for scoring, policy decisions, and deduplication.

**Installation:** See `pyproject.toml` for dependencies. Ensure you have an OpenAI API key in environment (or set it in `.env`). Run with:
```bash
streamlit run agentic_search/app.py
