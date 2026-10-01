import asyncio
from langchain_core.messages import HumanMessage

from app.tools.registry import ToolRegistry
from app.tools.rss import rss_tool_definition, fetch_rss_headlines
from app.graph.workflow import build_radio_graph

async def run_test():
    print("1. Initializing Tool Registry...")
    registry = ToolRegistry()
    
    # Simple, clean registration
    registry.register_tool(rss_tool_definition, fetch_rss_headlines)
    print(f"   Registered tools: {[t.name for t in registry.get_definitions()]}")
    
    print("2. Building Radio Graph...")
    graph = build_radio_graph(registry)
    
    print("3. Setting up initial RadioState...")
    initial_state = {
        "current_time": "2026-10-01T19:00:00Z",
        "buffer_seconds": 110.0,
        "topic_queue": [],
        "recent_topics": [],
        "recent_segments": [],
        "show_mood": "late-night, relaxed",
        "audience_context": "tech enthusiasts tuning in after hours",
        "active_topic": None,
        "segment_brief": None,
        "dialogue": None,
        "tool_calls_this_cycle": 0,
        "research_deadline": None,
        "last_error": None,
        "next_action": None,
        "messages": [
            HumanMessage(
                content="System alert: Buffer is dropping (110s). Please check the RSS feed for new headlines and plan the next segment."
            )
        ]
    }
    
    print("4. Invoking the graph...")
    
    try:
        final_state = await graph.ainvoke(initial_state)
        
        print("\n" + "="*50)
        print("EXECUTION COMPLETE. MESSAGE HISTORY:")
        print("="*50)
        
        for msg in final_state["messages"]:
            print(f"\n--- {msg.__class__.__name__} ---")
            if msg.content:
                print(msg.content)
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                print(f"🛠️  Tool Calls Requested: {msg.tool_calls}")
                
    except Exception as e:
        print(f"\n❌ Error during execution: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())