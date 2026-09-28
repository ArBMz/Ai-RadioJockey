import operator
from typing import Annotated, Sequence, Optional
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

from app.schemas.topic import Topic
from app.schemas.segment import SegmentBrief
from app.schemas.dialogue import Dialogue

class RadioState(TypedDict):
    """
    The shared memory state for a single LangGraph execution cycle.
    This maintains the context across the Producer's research loop and the Jokey's performance.
    """
    # --- System & Buffer Context ---
    current_time: str
    buffer_seconds: float
    
    # --- Show Memory ---
    topic_queue: list[Topic]
    recent_topics: list[Topic]
    recent_segments: list[SegmentBrief]
    show_mood: str
    audience_context: str
    
    # --- Current Production Cycle ---
    active_topic: Optional[Topic]
    segment_brief: Optional[SegmentBrief]
    dialogue: Optional[Dialogue]
    
    # --- Safety & Execution Tracking ---
    tool_calls_this_cycle: int
    research_deadline: Optional[str]
    last_error: Optional[str]
    next_action: Optional[str]
    
    # --- LangGraph LLM Memory ---
    # This tracks the internal monologue and tool results of the agent during the current cycle.
    # The 'operator.add' reducer ensures new messages are appended rather than overwriting the list.
    messages: Annotated[Sequence[BaseMessage], operator.add]