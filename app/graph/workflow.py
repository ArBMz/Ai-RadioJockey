import asyncio
from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, END

from app.graph.state import RadioState
from app.tools.registry import ToolRegistry
from app.agents.producer_agent import get_producer_llm, get_producer_prompt
from app.agents.jokey_agent import create_jokey_chain
from app.schemas.segment import SegmentBrief

def build_radio_graph(registry: ToolRegistry):
    workflow = StateGraph(RadioState)
    
    producer_llm = get_producer_llm()
    producer_prompt = get_producer_prompt()
    tools = registry.get_langchain_tools()
    producer_with_tools = producer_llm.bind_tools(tools + [SegmentBrief])
    producer_chain = producer_prompt | producer_with_tools

    jokey_chain = create_jokey_chain()

    async def producer_node(state: RadioState):
        response = await producer_chain.ainvoke(state)
        return {"messages": [response]}

    async def tool_node(state: RadioState):
        last_message = state["messages"][-1]
        tool_responses = []
        
        # Safety check: if there are no tool calls, don't execute anything
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return {"messages": []}
            
        for tool_call in last_message.tool_calls:
            if tool_call["name"] == "SegmentBrief":
                continue
                
            tool = next((t for t in tools if t.name == tool_call["name"]), None)
            if tool:
                try:
                    raw_result = await asyncio.wait_for(
                        tool.ainvoke(tool_call["args"]), 
                        timeout=15.0
                    )
                    content = raw_result.model_dump_json() if hasattr(raw_result, 'model_dump_json') else str(raw_result)
                except asyncio.TimeoutError:
                    content = '{"success": false, "error": "Tool timed out"}'
                except Exception as e:
                    content = f'{{"success": false, "error": "{str(e)}"}}'

                tool_responses.append(
                    ToolMessage(content=content, name=tool_call["name"], tool_call_id=tool_call["id"])
                )
        return {"messages": tool_responses}

    async def jokey_node(state: RadioState):
        last_message = state["messages"][-1]
        
        # 1. Safely try to find the SegmentBrief tool call
        brief_args = None
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            for tc in last_message.tool_calls:
                if tc["name"] == "SegmentBrief":
                    brief_args = tc.get("args")
                    break
        
        # 2. If the Producer panicked and didn't use the tool, create a Fallback Brief!
        if not brief_args:
            raw_producer_text = last_message.content if last_message.content else "Total system silence."
            brief_args = {
                "topic": "ON-AIR EMERGENCY / PRODUCER MELTDOWN",
                "context": f"The Producer just sent a panicked, unformatted message to the studio: '{raw_producer_text}'",
                "tone": "confused, slightly panicked, breaking the fourth wall",
                "jokey_instructions": [
                    "Acknowledge that things are going completely off the rails.", 
                    "Read the producer's raw message to the audience.",
                    "Try to keep the broadcast alive."
                ],
                "key_points": ["Technical malfunction", "Producer breakdown"]
            }
        
        jokey_inputs = {
            "topic": brief_args.get("topic", "Unknown"),
            "context": brief_args.get("context", ""),
            "tone": brief_args.get("tone", ""),
            "instructions": ", ".join(brief_args.get("jokey_instructions", [])),
            "key_points": ", ".join(brief_args.get("key_points", []))
        }
        
        dialogue = await jokey_chain.ainvoke(jokey_inputs)
        return {"dialogue": dialogue}

    def route_producer_output(state: RadioState) -> str:
        last_message = state["messages"][-1]
        
        # If the LLM just yelled raw text (no tool calls), route straight to Jokey for the fallback response
        if not hasattr(last_message, 'tool_calls') or not last_message.tool_calls:
            return "jokey"
            
        # If the ONLY tool called was SegmentBrief, route to Jokey
        if len(last_message.tool_calls) == 1 and last_message.tool_calls[0]["name"] == "SegmentBrief":
            return "jokey"
            
        # Otherwise, execute external tools (like checking the director log or RSS)
        return "tools"

    workflow.add_node("producer", producer_node)
    workflow.add_node("tools", tool_node)
    workflow.add_node("jokey", jokey_node)
    
    workflow.set_entry_point("producer")
    workflow.add_conditional_edges("producer", route_producer_output, {"tools": "tools", "jokey": "jokey"})
    workflow.add_edge("tools", "producer")
    workflow.add_edge("jokey", END)

    return workflow.compile()