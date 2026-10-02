import json
import os
import asyncio
from app.schemas.tool import ToolDefinition, ToolResult

LOG_FILE = "director_log.json"

def init_log_file():
    """Creates the log file with a dummy instruction if it doesn't exist."""
    if not os.path.exists(LOG_FILE):
        dummy_log = [
            {
                "id": 1, 
                "text": "Talk about the history of synthesizer music.", 
                "status": "pending"
            }
        ]
        with open(LOG_FILE, "w") as f:
            json.dump(dummy_log, f, indent=4)

director_tool_definition = ToolDefinition(
    name="check_director_instructions",
    description="Checks the Director's log for manual topic requests or instructions. ALWAYS call this tool first before deciding on a topic.",
    timeout_seconds=5,
    risk_class="mutating" 
)

async def check_director_instructions() -> ToolResult:
    """Reads the FIRST pending instruction (FIFO queue) and marks it as consumed."""
    init_log_file()
    try:
        # Simulate slight file read delay
        await asyncio.sleep(0.5) 
        
        with open(LOG_FILE, "r+") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
            
            # Find ONLY the first pending instruction
            pending_instruction = next((log for log in logs if log.get("status") == "pending"), None)
            
            if not pending_instruction:
                return ToolResult(
                    success=True, 
                    data={"instructions": "No manual instructions. Proceed autonomously with RSS feeds or continue previous topic."}, 
                    error=None
                )
            
            # Mark ONLY the fetched instruction as consumed
            pending_instruction["status"] = "consumed"
            
            # Wipe the file and write the updated statuses back
            f.seek(0)
            json.dump(logs, f, indent=4)
            f.truncate()
            
            return ToolResult(
                success=True,
                data={"instructions": pending_instruction}, # Return just the single instruction
                error=None
            )
            
    except Exception as e:
        return ToolResult(success=False, data=None, error=str(e))