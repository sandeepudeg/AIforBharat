from typing import Any
import math
from strands.types.tools import ToolUse, ToolResult

TOOL_SPEC = {
    "name": "hypotenuse_calc",
    "description": "Calculate the hypotenuse of a right triangle given the base and perpendicular sides",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "base": {
                    "type": "number",
                    "description": "Length of the base (adjacent) side of the right triangle"
                },
                "perpendicular": {
                    "type": "number",
                    "description": "Length of the perpendicular (opposite) side of the right triangle"
                }
            },
            "required": ["base", "perpendicular"]
        }
    }
}

def hypotenuse_calc(tool_use: ToolUse, **kwargs: Any) -> ToolResult:
    """
    Calculate the hypotenuse of a right triangle using the Pythagorean theorem.
    
    Args:
        tool_use: Contains the base and perpendicular lengths
        
    Returns:
        The length of the hypotenuse
    """
    tool_use_id = tool_use["toolUseId"]
    base = tool_use["input"]["base"]
    perpendicular = tool_use["input"]["perpendicular"]
    
    try:
        if base <= 0 or perpendicular <= 0:
            raise ValueError("Both base and perpendicular must be positive numbers")
            
        # Calculate hypotenuse using the Pythagorean theorem: a² + b² = c²
        hypotenuse = math.sqrt(base**2 + perpendicular**2)
        
        return {
            "toolUseId": tool_use_id,
            "status": "success",
            "content": [{
                "text": f"For a right triangle with:\n" + 
                        f"Base = {base}\n" +
                        f"Perpendicular = {perpendicular}\n" +
                        f"The hypotenuse = {hypotenuse:.2f}"
            }]
        }
        
    except Exception as e:
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": f"Error: {str(e)}"}]
        }