from typing import Any, Callable, Coroutine
from langchain_core.tools import BaseTool, StructuredTool
from app.schemas.tool import ToolDefinition, ToolResult

class ToolRegistry:
    """Central registry managing agent-facing tools."""

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._definitions: dict[str, ToolDefinition] = {}

    def register_tool(
        self,
        definition: ToolDefinition,
        func: Callable[..., Coroutine[Any, Any, ToolResult]],
    ) -> None:
        # By passing the raw 'func', LangChain automatically reads your 
        # Python type hints (feed_url: str) and builds the perfect schema.
        langchain_tool = StructuredTool.from_function(
            coroutine=func,
            name=definition.name,
            description=definition.description
        )

        self._tools[definition.name] = langchain_tool
        self._definitions[definition.name] = definition

    def get_langchain_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_definitions(self) -> list[ToolDefinition]:
        return list(self._definitions.values())