import asyncio
from app.schemas.tool import ToolDefinition, ToolResult

# 1. The Blueprint (ToolDefinition)
# This tells LangChain and the LLM exactly what this tool does and how to use it.
rss_tool_definition = ToolDefinition(
    name="fetch_rss_headlines",
    description="Fetches the latest news headlines from a given RSS feed URL. Use this to discover current events.",
    input_schema={
        "type": "object",
        "properties": {
            "feed_url": {
                "type": "string", 
                "description": "The URL of the RSS feed to read"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of headlines to return"
            }
        },
        "required": ["feed_url"]
    },
    timeout_seconds=15,
    risk_class="read_only"
)

# 2. The Implementation (The Callable Coroutine)
# Notice how the arguments (feed_url, limit) match the input_schema above,
# and it returns exactly a ToolResult.
async def fetch_rss_headlines(feed_url: str, limit: int = 5) -> ToolResult:
    try:
        # In a real implementation, you would use aiohttp or feedparser here.
        # We simulate a brief network request:
        await asyncio.sleep(1)
        
        # Mocked data representing parsed XML items
        mock_data = [
            {"title": "New Local AI Model Drops", "link": f"{feed_url}/item1"},
            {"title": "Scientists Discover New Coffee Bean", "link": f"{feed_url}/item2"}
        ][:limit]
        
        # Always return the standardized ToolResult
        return ToolResult(
            success=True,
            data={"headlines": mock_data},
            source_refs=[feed_url],
            error=None
        )
        
    except Exception as exc:
        # If the parsing crashes, we catch it and return a failed ToolResult
        # so the registry wrapper can pass the error to the LLM safely.
        return ToolResult(
            success=False,
            data=None,
            error=str(exc)
        )