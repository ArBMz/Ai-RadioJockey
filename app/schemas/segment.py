from pydantic import BaseModel, Field

class SegmentBrief(BaseModel):
    topic: str = Field(description="The main subject of the segment")
    segment_type: str = Field(description="Type of segment (e.g., 'discussion', 'news_update', 'transition')")
    target_duration_seconds: int = Field(description="Desired length of the audio segment in seconds")
    
    # --- Continuity Tracking ---
    is_follow_up: bool = Field(default=False, description="True if continuing the previous conversation")
    segment_part: int = Field(default=1, description="Which part of the current topic this is (1, 2, 3...)")
    previous_context: str | None = Field(default=None, description="Transition hint or recap from the prior segment")
    # ---------------------------
    
    tone: str = Field(description="Emotional or stylistic direction (e.g., 'relaxed, playful')")
    context: str = Field(description="Factual background information for the host")
    key_points: list[str] = Field(description="Specific items that must be mentioned")
    jokey_instructions: list[str] = Field(description="Specific performance directions for the Jokey agent")
    source_refs: list[str] = Field(default_factory=list, description="Reference URLs or citations")