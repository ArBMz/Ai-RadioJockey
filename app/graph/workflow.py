import asyncio
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END

from app.graph.state import RadioState
from app.tools.registry import ToolRegistry
from app.agents.producer_agent import get_producer_llm, get_producer_prompt
from app.schemas.segment import SegmentBrief

def build_radio_graph(registry: ToolRegistry):
    workflow = StateGraph(RadioState)
    
    llm = get_producer_llm()
    prompt = get_producer_prompt()
    tools = registry.get_langchain_tools()
    
    producer_with_tools = llm.bind_tools(tools + [SegmentBrief])
    producer_chain = prompt | producer_with_tools

    async def producer_node(state: RadioState):
        response = await producer_chain.ainvoke(state)
        return {"messages": [response]}

    async def tool_node(state: RadioState):
        last_message = state["messages"][-1]
        tool_responses = []
        
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "SegmentBrief":
                continue
                
            tool = next((t for t in tools if t.name == tool_call["name"]), None)
            if tool:
                try:
                    # Execute the tool with a 15-second timeout safety net
                    raw_result = await asyncio.wait_for(
                        tool.ainvoke(tool_call["args"]), 
                        timeout=15.0
                    )
                    # Convert the ToolResult Pydantic object into a JSON string for the LLM
                    content = raw_result.model_dump_json() if hasattr(raw_result, 'model_dump_json') else str(raw_result)
                    
                except asyncio.TimeoutError:
                    content = '{"success": false, "error": "Tool timed out"}'
                except Exception as e:
                    content = f'{{"success": false, "error": "{str(e)}"}}'

                tool_responses.append(
                    ToolMessage(
                        content=content, 
                        name=tool_call["name"], 
                        tool_call_id=tool_call["id"]
                    )
                )
        return {"messages": tool_responses}

    def route_producer_output(state: RadioState) -> str:
        last_message = state["messages"][-1]
        
        if last_message.tool_calls:
            if len(last_message.tool_calls) == 1 and last_message.tool_calls[0]["name"] == "SegmentBrief":
                return "jokey"
            return "tools"
            
        return "jokey"

    workflow.add_node("producer", producer_node)
    workflow.add_node("tools", tool_node)
    
    workflow.set_entry_point("producer")
    workflow.add_conditional_edges("producer", route_producer_output, {"tools": "tools", "jokey": END})
    workflow.add_edge("tools", "producer")

    return workflow.compile()