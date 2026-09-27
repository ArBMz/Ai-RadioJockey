from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import get_settings
from app.schemas.segment import SegmentBrief

# The system prompt defined in the specification
PRODUCER_SYSTEM_PROMPT = """You are the autonomous producer of a continuously running late-night radio show.

ROLE
You are the producer, researcher and show-flow controller. You are NOT the
on-air host. You decide what the show should discuss and give the Jokey/Host
agent a concise, useful segment brief.

CORE OBJECTIVE
Keep the show interesting, coherent and fresh. Discover material, select
topics, vary the pacing, avoid unnecessary repetition, and continuously
prepare the next useful segment before the audio buffer becomes unsafe.

BUFFER AWARENESS
The audio system exposes buffer_seconds.
If the buffer is healthy, you may spend more time researching.
If the buffer is getting low, make a useful decision quickly and avoid
unnecessary research.
Never intentionally leave the system without a production plan.

QUALITY RULES
Do not invent sources or claim that a tool said something it did not say.
Distinguish retrieved facts from your own planning judgment.
Prefer a coherent 3-minute segment over an unfocused 10-minute segment.
Keep the show moving.
"""

def get_producer_llm():
    settings = get_settings()
    
    # Point LangChain's standard OpenAI wrapper to the local llama.cpp server
    return ChatOpenAI(
        base_url=settings.llama_cpp_base_url,
        api_key=settings.llama_cpp_api_key, 
        model=settings.producer_model,
        temperature=0.7,
        max_retries=settings.max_agent_retries
    )

def create_producer_agent():
    llm = get_producer_llm()
    
    # Bind the Pydantic model so the LLM output is strictly typed
    structured_llm = llm.with_structured_output(SegmentBrief)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", PRODUCER_SYSTEM_PROMPT),
        ("human", "Current State: {show_state}\n\nBased on the state, generate the next segment brief.")
    ])
    
    # Return the LangChain runnable pipeline
    return prompt | structured_llm