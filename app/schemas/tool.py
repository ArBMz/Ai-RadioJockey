from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str = Field(description="Unique name of the tool")
    description: str = Field(description="Detailed explanation of the capability and use cases")
    input_schema: dict[str, Any] = Field(default_factory=dict, description="JSON schema for inputs")
    timeout_seconds: int = Field(default=10, description="Execution timeout in seconds")
    risk_class: Literal["read_only", "mutating", "external_publish"] = Field(
        default="read_only",
        description="Risk level for permission scoping"
    )


class ToolResult(BaseModel):
    success: bool = Field(description="Whether the tool execution succeeded")
    data: Any = Field(default=None, description="Returned payload or summary")
    source_refs: list[str] = Field(default_factory=list, description="Citations, URLs, or references")
    fetched_at: datetime = Field(default_factory=datetime.now, description="Timestamp of execution")
    error: str | None = Field(default=None, description="Error message if execution failed")