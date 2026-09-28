from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END

from app.graph.state import RadioState
from app.tools.registry import ToolRegistry
from app.agents.producer_agent import create_producer_agent

def build_radio_graph(registry: ToolRegistry):
    # Initialize the graph using our complete shared memory state
    workflow = StateGraph(RadioState)
    
    # Initialize the Producer agent
    producer_llm = create_producer_agent()
    tools = registry.get_langchain_tools()
    
    # Bind the tools to the LLM so it knows it can call them during its cycle
    producer_with_tools = producer_llm.bind_tools(tools)

    def producer_node(state: RadioState):
        """The Producer evaluates the state and messages, then decides the next action."""
        # Invoke the LLM with the current message history
        response = producer_with_tools.invoke(state["messages"])
        
        # LangGraph's reducer (operator.add) will append this to the message list
        return {"messages": [response]}

    def tool_node(state: RadioState):
        """Executes the tools chosen by the Producer and returns the results."""
        last_message = state["messages"][-1]
        tool_responses = []
        
        # Loop through all tools the LLM requested in its last turn
        for tool_call in last_message.tool_calls:
            # Find the corresponding tool in our registry
            tool = next(t for t in tools if t.name == tool_call["name"])
            
            # Execute the tool safely using the registry's wrapper
            result = tool.invoke(tool_call["args"])
            
            # Package the result into a ToolMessage for the LLM to read on its next pass
            tool_responses.append(
                ToolMessage(
                    content=str(result), 
                    name=tool_call["name"], 
                    tool_call_id=tool_call["id"]
                )
            )
            
        return {"messages": tool_responses}

    def route_producer_output(state: RadioState) -> str:
        """Determines if the Producer is still researching or ready to hand off."""
        last_message = state["messages"][-1]
        
        # If the LLM output includes tool calls, route to the tool execution node
        if last_message.tool_calls:
            return "tools"
            
        # Otherwise, the research phase is complete. 
        # We route to the Jokey (mapped to END temporarily for Phase 1 testing).
        return "jokey"

    # Add the nodes to our graph
    workflow.add_node("producer", producer_node)
    workflow.add_node("tools", tool_node)
    
    # Define the execution flow starting with the Producer
    workflow.set_entry_point("producer")
    
    # The conditional edge creates the autonomous research loop
    workflow.add_conditional_edges(
        "producer",
        route_producer_output,
        {
            "tools": "tools",
            "jokey": END  # We will map this to the real 'jokey' node in Phase 2
        }
    )
    
    # After tools execute, always return to the Producer to evaluate the newly fetched data
    workflow.add_edge("tools", "producer")

    return workflow.compile()