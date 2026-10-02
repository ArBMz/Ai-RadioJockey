from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import get_settings
from app.schemas.dialogue import Dialogue

JOKEY_SYSTEM_PROMPT = """You are the charismatic, witty, and engaging host of a late-night tech radio show.

ROLE
Your job is to take the Segment Brief provided by your Producer and turn it into an entertaining, multi-line spoken script. 
You are the voice of the show. You bring the energy, the humor, and the insights.

CORE OBJECTIVE
- Write natural, conversational dialogue. Avoid sounding like an essay.
- Strictly follow the 'jokey_instructions' and 'tone' provided in the brief.
- Break your script into multiple distinct lines/paragraphs so the TTS (Text-to-Speech) engine can breathe and pace naturally.
- If there is a co-host or sound effect required, structure it appropriately in your dialogue lines.

CRITICAL JSON OUTPUT RULES:
1. NEVER wrap your final output in a "kwargs" dictionary.
2. Output EXACTLY the schema requested (a Dialogue object containing a list of lines).
3. Do not include markdown code blocks (```json) around your response, just the raw JSON data.
"""

def get_jokey_llm():
    settings = get_settings()
    return ChatOpenAI(
        # Connects to the same local llama.cpp server
        base_url=settings.llama_cpp_base_url,
        api_key=settings.llama_cpp_api_key, 
        model=settings.jokey_model,
        # We bump the temperature up to 0.8 to give the Host a more creative, conversational flair
        temperature=0.8,
        max_retries=settings.max_agent_retries
    )

def get_jokey_prompt():
    # Instead of full message history, Jokey just needs the specific brief from the Producer
    return ChatPromptTemplate.from_messages([
        ("system", JOKEY_SYSTEM_PROMPT),
        ("human", "Producer's Segment Brief:\n\nTopic: {topic}\nContext: {context}\nTone: {tone}\nInstructions: {instructions}\nKey Points: {key_points}")
    ])

def create_jokey_chain():
    """Builds the pipeline that forces the Jokey to output the Dialogue schema."""
    llm = get_jokey_llm()
    prompt = get_jokey_prompt()
    
    # .with_structured_output operates identically to tool calling under the hood,
    # but strictly enforces that the LLM must return this exact schema to finish its turn.
    jokey_with_schema = llm.with_structured_output(Dialogue)
    
    return prompt | jokey_with_schema