# AI Radio Jockey

AI Radio Jockey is an experimental, continuously running radio-show script generator. A LangGraph workflow coordinates a producer agent, research tools, and a host agent called Jokey. The producer prepares a segment brief; Jokey turns it into structured, line-by-line dialogue that can later be connected to a text-to-speech system.

> **Current status:** This project generates text scripts, not live audio. The RSS tool currently returns mock headlines, and TTS settings are reserved for future integration.

## How It Works

Each broadcast cycle runs these steps:

1. The producer checks `director_log.json` for the first instruction with status `pending`.
2. If it finds an instruction, it uses it for the next segment. Otherwise, it can research with the registered RSS tool or continue the previous topic.
3. The producer submits a structured `SegmentBrief` tool call with the topic, context, tone, key points, and host directions.
4. The Jokey agent generates a structured `Dialogue` containing spoken lines, speaker names, emotions, an estimated duration, and an optional transition hint.
5. `test.py` prints the dialogue and starts another cycle after 10 seconds.

The workflow and shared state live in `app/graph/`; the agents are in `app/agents/`; tool registration and implementations are in `app/tools/`; and Pydantic data models are in `app/schemas/`.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) for dependency and virtual-environment management
- An OpenAI-compatible chat-completions endpoint accessible from the machine running the project. The default is a local `llama.cpp` server at `http://localhost:8080/v1`.

The project dependencies are declared in `pyproject.toml` and pinned in `uv.lock`.

## Setup

From the repository directory, install the locked dependencies:

```powershell
uv sync
```

Create a `.env` file in the repository root to override model settings. For example:

```dotenv
LLM_PROVIDER=llama_cpp
LLAMA_CPP_BASE_URL=http://localhost:8080/v1
LLAMA_CPP_API_KEY=not-needed
PRODUCER_MODEL=local-model
JOKEY_MODEL=local-model
```

Start your OpenAI-compatible inference server and set the URL and model names to match its configuration. `LLAMA_CPP_API_KEY` is passed to the client; for a local server that does not require authentication, the default placeholder value is sufficient. Do not put real credentials in source control.

Run the continuous demonstration:

```powershell
uv run python test.py
```

Stop the loop with `Ctrl+C`. The script prints each generated dialogue line with its speaker and emotion. No audio is produced.

## Director Instructions

While the loop is running, edit `director_log.json` in the repository root and add an instruction with a `pending` status. Instructions are read in file order; the first pending item is changed to `consumed` when retrieved.

```json
[
  {
    "id": 1,
    "text": "Talk about the history of synthesizer music.",
    "status": "pending"
  }
]
```

The runner calls `init_log_file()` before starting. If `director_log.json` does not exist, it creates the file with a sample pending instruction. Keep the JSON valid when editing it; invalid JSON is treated as an empty instruction list by the director tool.

## Configuration

Settings are defined in `app/config.py`, loaded from `.env` and environment variables, and cached for the process lifetime.

| Variable | Default | Purpose |
| --- | --- | --- |
| `LLM_PROVIDER` | `llama_cpp` | Declares `llama_cpp` or `ollama` as the provider. The current agents use the configured OpenAI-compatible base URL directly; this setting does not select a separate client implementation. |
| `LLAMA_CPP_BASE_URL` | `http://localhost:8080/v1` | OpenAI-compatible model server URL. |
| `LLAMA_CPP_API_KEY` | `not-needed` | API key value supplied to the chat client. |
| `PRODUCER_MODEL` | `local-model` | Model name used for producer requests. |
| `JOKEY_MODEL` | `local-model` | Model name used for host dialogue generation. |
| `BUFFER_TARGET_SECONDS` | `300` | Intended target audio buffer duration. |
| `BUFFER_WARNING_SECONDS` | `120` | Intended low-buffer warning threshold. |
| `BUFFER_EMERGENCY_SECONDS` | `30` | Intended emergency buffer threshold. |
| `SEGMENT_MIN_SECONDS` | `90` | Intended minimum segment duration. |
| `SEGMENT_TARGET_SECONDS` | `180` | Intended target segment duration. |
| `SEGMENT_MAX_SECONDS` | `300` | Intended maximum segment duration. |
| `MAX_TOOL_CALLS_PER_CYCLE` | `8` | Intended per-cycle tool-call budget. |
| `MAX_RESEARCH_SECONDS` | `30` | Intended research time budget. |
| `MAX_AGENT_RETRIES` | `2` | Retry count supplied to the chat clients. |
| `TTS_PROVIDER` | `local` | Reserved text-to-speech provider setting; TTS is not implemented. |
| `TTS_DEFAULT_SPEED` | `1.0` | Reserved default speech speed; TTS is not implemented. |
| `LOG_LEVEL` | `INFO` | Reserved logging setting; the demonstration currently uses `print`. |

The buffer, segment, tool-call, research, TTS, and logging values are configuration groundwork and are not currently enforced by the demonstration workflow. The runner also initializes each cycle with example time and buffer values in `test.py`.

## Tools and Current Limitations

- `check_director_instructions` reads and consumes one pending item from the local JSON file.
- `fetch_rss_headlines` currently simulates a short delay and returns hard-coded sample headlines using the supplied feed URL. It does not fetch or parse a real RSS feed.
- If the producer does not submit a `SegmentBrief`, the graph creates an emergency fallback brief so Jokey can still attempt to generate dialogue.
- The application does not currently synthesize, stream, or play audio, and it does not expose a web interface or service API.
- `test.py` is the interactive demonstration runner, not an automated test suite.

## Project Layout

```text
app/
  agents/       Producer and Jokey model prompts/chains
  graph/        LangGraph workflow and shared radio state
  schemas/      Pydantic models for topics, segments, dialogue, and tools
  tools/        Tool registry, director log, and RSS placeholder
  config.py     Environment-backed application settings
test.py         Continuous console demonstration
director_log.json
pyproject.toml  Project metadata and dependencies
uv.lock        Locked dependency versions
```