import asyncio
import json
from langchain_core.messages import HumanMessage

from app.tools.registry import ToolRegistry
from app.tools.rss import rss_tool_definition, fetch_rss_headlines
from app.tools.director import director_tool_definition, check_director_instructions, init_log_file
from app.graph.workflow import build_radio_graph

async def run_test():
    print("1. Initializing Tool Registry & Director Log...")
    init_log_file() # Ensure the JSON file exists before we start
    
    registry = ToolRegistry()
    registry.register_tool(rss_tool_definition, fetch_rss_headlines)
    # Register the new director tool
    registry.register_tool(director_tool_definition, check_director_instructions)
    
    print(f"   Registered tools: {[t.name for t in registry.get_definitions()]}")
    
    print("2. Building Radio Graph...")
    graph = build_radio_graph(registry)
    
    print("3. Starting Continuous Radio Loop (Press Ctrl+C to stop)...\n")
    print("💡 TIP: While this runs, open 'director_log.json' in your editor, add an instruction with status 'pending', and save it!")
    
    segment_count = 1
    previous_topic = "None (Show Intro)"
    
    try:
        while True:
            print(f"\n{'='*60}")
            print(f"BROADCASTING SEGMENT {segment_count}")
            print(f"{'='*60}")
            
            state = {
                "current_time": "2026-10-02T19:00:00Z",
                "buffer_seconds": 110.0,
                "topic_queue": [],
                "recent_topics": [previous_topic],
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
                        # We simplified the alert. The system prompt now dictates the logic.
                        content=f"System alert: Buffer is dropping. The previous segment was about '{previous_topic}'. Please plan the next segment."
                    )
                ]
            }
            
            print("\n[System] Producer is checking logs and researching...")
            final_state = await graph.ainvoke(state)
            
            last_message = final_state["messages"][-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                brief_args = last_message.tool_calls[0].get("args", {})
                previous_topic = brief_args.get("topic", "General News")
                print(f"[System] Producer finalized topic: {previous_topic}")
            
            print("\n  LIVE AUDIO SCRIPT:")
            print("-" * 60)
            dialogue = final_state.get("dialogue")
            if dialogue:
                for line in dialogue.lines:
                    emotion = getattr(line, 'emotion', 'neutral')
                    print(f"[{line.speaker}] ({emotion}): {line.text}")
            else:
                print("No dialogue was generated.")
            print("-" * 60)
            
            segment_count += 1
            print("\n[System] Segment complete. Waiting 10 seconds before starting the next cycle...\n")
            await asyncio.sleep(10)
            
    except KeyboardInterrupt:
        print("\n Broadcast terminated by user. Shutting down gracefully.")
    except Exception as e:
        print(f"\nError during execution: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())