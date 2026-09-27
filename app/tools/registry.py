import asyncio
from datetime import datetime
from typing import Any, Callable, Coroutine
from langchain_core.tools import BaseTool, StructuredTool
from app.schemas.tool import ToolDefinition, ToolResult


class ToolRegistry:
    """Central registry managing agent-facing tools and runtime safety limits."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._definitions: dict[str, ToolDefinition] = {}

    def register_tool(
        self,
        definition: ToolDefinition,
        func: Callable[..., Coroutine[Any, Any, ToolResult]],
    ) -> None:
        """ Wrapper for an async function to be registered as a LangChain tool with timeout and safety handling. """
        async def safe_executor(**kwargs:Any) -> str:
            try:
                result: ToolResult = await asyncio.wait_for(func(**kwargs), timeout=definition.timeout_seconds)
                return result.model_dump_json()  # Return JSON string representation of the result
            except asyncio.TimeoutError:
                return ToolResult(success=False, error="Execution timed out").model_dump_json()
            except Exception as e:
                return ToolResult(success=False, data=None, error=f"An error occurred: {str(e)}").model_dump_json()
        langchain_tool = StructuredTool.from_function(
            coroutine=safe_executor,
            name=definition.name,
            description=definition.description,
            args_schema=None #Can be inferred or passed explicitly via pydantic model if needed
        )

        self._tools[definition.name] = langchain_tool
        self._definitions[definition.name] = definition
            
        
    def get_langchain_tools(self) -> list[BaseTool]:
        """Returns all registered tools ready for LangChain model binding."""
        return list(self._tools.values())

    def get_definitions(self) -> list[ToolDefinition]:
        """Returns metadata descriptions of all registered tools."""
        return list(self._definitions.values())