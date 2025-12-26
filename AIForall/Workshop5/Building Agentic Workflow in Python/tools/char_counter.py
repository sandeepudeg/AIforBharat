from typing import Any
from strands.types.tools import ToolUse, ToolResult

TOOL_SPEC = {
    "name": "char_counter",
    "description": "Counts the number of characters in the provided text",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to count characters in"
                }
            },
            "required": ["text"]
        }
    }
}

def char_counter(tool_use: ToolUse, **kwargs: Any) -> ToolResult:
    """
    Count the number of characters in the provided text.
    
    Args:
        tool_use: The tool use object containing the input text
        
    Returns:
        ToolResult containing the character count
    """
    tool_use_id = tool_use["toolUseId"]
    text = tool_use["input"]["text"]
    
    char_count = len(text)
    
    return {
        "toolUseId": tool_use_id,
        "status": "success",
        "content": [{"text": f"Character count: {char_count}"}]
    }