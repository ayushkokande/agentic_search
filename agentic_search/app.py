import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from agentic_search.core.graph import build_agent_graph
from agentic_search.core.types import SearchState
from agentic_search.ui.formatters import places_to_dataframe

def main():
    st.title("Agentic Search Interface")
    query = st.text_input("Enter your search query:", "")
    if not query:
        st.info("Please enter a query to begin the search.")
        return

    # Initialize graph and state
    graph = build_agent_graph()
    initial_state = SearchState(
        messages=[HumanMessage(content=query)],
        query=query,
        domain="",
        expanded_query=query,
        user_location="current location",
        places=[],
        filtered=[],
        ranked=[],
        final_results=[]
    )

    # Run the agent graph and capture updates
    result_state = graph.invoke(initial_state)
    
    # Display the trace: messages from human/AI/tool
    st.header("Agent Trace")
    for msg in result_state["messages"]:
        if isinstance(msg, HumanMessage):
            st.markdown(f"**User:** {msg.content}")
        elif isinstance(msg, AIMessage):
            st.markdown(f"**Agent:** {msg.content}")
        elif isinstance(msg, ToolMessage):
            st.markdown(f"**Tool ({msg.name}) output:** {msg.text}")

    # Display final results
    st.header("Final Results")
    final_places = result_state.get("final_results", [])
    if final_places:
        df = places_to_dataframe(final_places)
        st.table(df)
    else:
        st.write("No results found.")

if __name__ == "__main__":
    main()
