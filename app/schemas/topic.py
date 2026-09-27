from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Topic(BaseModel):
    """
    Represents a potential subject for the radio show, sourced from manual input, 
    RSS, or dynamic tools.
    """
    id: str = Field(description="Unique identifier for the topic")
    title: str = Field(description="Short headline or name of the topic")
    source: str = Field(description="Origin of the topic (e.g., 'manual', 'rss_feed', 'mcp_trend_tool')")
    
    # Priority allows manual inputs (e.g., 10) to jump ahead of auto-discovered news (e.g., 5)
    priority: int = Field(default=5, description="Priority level, higher is more urgent")

    # Topic duration
    duration_limit_seconds: int | None = Field(
        default=None, 
        description="Maximum total duration allowed for this topic across all segments"
    )

    # Freshness metric helps the Producer avoid stale news
    freshness: float | None = Field(default=None, description="Score indicating how recent/relevant this is")
    
    summary: str | None = Field(default=None, description="Optional brief description of the content")
    source_refs: list[str] = Field(default_factory=list, description="URLs or reference IDs for fact-checking")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the topic entered the queue")
    used_at: datetime | None = Field(default=None, description="When the topic was turned into a segment")