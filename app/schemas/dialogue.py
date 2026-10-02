from pydantic import BaseModel, Field

class DialogueLine(BaseModel):
    speaker: str = Field(description="Identifier of the configured voice/character")
    emotion: str = Field(default="neutral", description="The emotional delivery or tone for this specific line (e.g., 'laughing', 'sarcastic', 'excited')")
    text: str = Field(description="The spoken text, free of stage directions or markdown")

class Dialogue(BaseModel):
    lines: list[DialogueLine] = Field(description="Sequential list of spoken lines")
    estimated_duration_seconds: int = Field(description="Approximate duration of the generated dialogue")
    transition_hint: str | None = Field(default=None, description="Optional thematic bridge to the next segment")

class Speaker(BaseModel):
    id: str = Field(description="Internal ID of the speaker")
    display_name: str = Field(description="Public facing name")
    tts_voice: str = Field(description="Identifier used by the TTS engine")
    speaking_rate: float = Field(default=1.0, description="Speed multiplier for the voice")
    pitch: float = Field(default=0.0, description="Pitch adjustment")