import asyncio
from pydantic import BaseModel, Field
from app.schemas.tool import ToolDefinition, ToolResult

# 1. The Strict Argument Schema for LangChain
class RSSInput(BaseModel):
    feed_url: str = Field(description="The URL of the RSS feed to read")
    limit: int = Field(default=5, description="Maximum number of headlines to return")

# 2. The Blueprint
rss_tool_definition = ToolDefinition(
    name="fetch_rss_headlines",
    description="Fetches the latest news headlines from a given RSS feed URL. Use this to discover current events.",
    timeout_seconds=15,
    risk_class="read_only"
)

# 3. The Implementation
async def fetch_rss_headlines(feed_url: str, limit: int = 5) -> ToolResult:
    try:
        await asyncio.sleep(1) # Simulate network delay
        
        mock_data = [
            {"title": "Local AI Models Achieve New Milestone", "link": f"{feed_url}/item1"},
            {"title": "Scientists Discover Coffee Alternative", "link": f"{feed_url}/item2"}
        ][:limit]
        
        return ToolResult(
            success=True,
            data={"headlines": mock_data},
            source_refs=[feed_url],
            error=None
        )
        
    except Exception as exc:
        return ToolResult(success=False, data=None, error=str(exc))