from typing import Any
import math
from strands.types.tools import ToolUse, ToolResult

TOOL_SPEC = {
    "name": "scientific_calc",
    "description": "Scientific calculator that performs various mathematical operations",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Mathematical operation to perform (add, subtract, multiply, divide, power, sqrt, sin, cos, tan, log)"
                },
                "x": {
                    "type": "number",
                    "description": "First number for the operation"
                },
                "y": {
                    "type": "number",
                    "description": "Second number for operations that require two numbers (optional for sqrt, sin, cos, tan, log)",
                }
            },
            "required": ["operation", "x"]
        }
    }
}

def scientific_calc(tool_use: ToolUse, **kwargs: Any) -> ToolResult:
    """
    Perform scientific calculator operations.
    
    Args:
        tool_use: Contains operation and numbers to process
        
    Returns:
        Result of the mathematical operation
    """
    tool_use_id = tool_use["toolUseId"]
    operation = tool_use["input"]["operation"]
    x = tool_use["input"]["x"]
    y = tool_use["input"].get("y")  # Optional parameter
    
    result = None
    
    try:
        if operation == "add":
            if y is None:
                raise ValueError("Second number required for addition")
            result = x + y
        elif operation == "subtract":
            if y is None:
                raise ValueError("Second number required for subtraction")
            result = x - y
        elif operation == "multiply":
            if y is None:
                raise ValueError("Second number required for multiplication")
            result = x * y
        elif operation == "divide":
            if y is None:
                raise ValueError("Second number required for division")
            if y == 0:
                raise ValueError("Division by zero")
            result = x / y
        elif operation == "power":
            if y is None:
                raise ValueError("Second number required for power operation")
            result = math.pow(x, y)
        elif operation == "sqrt":
            if x < 0:
                raise ValueError("Cannot calculate square root of negative number")
            result = math.sqrt(x)
        elif operation == "sin":
            result = math.sin(math.radians(x))
        elif operation == "cos":
            result = math.cos(math.radians(x))
        elif operation == "tan":
            result = math.tan(math.radians(x))
        elif operation == "log":
            if x <= 0:
                raise ValueError("Cannot calculate logarithm of non-positive number")
            result = math.log10(x)
        else:
            raise ValueError(f"Unknown operation: {operation}")
            
        return {
            "toolUseId": tool_use_id,
            "status": "success",
            "content": [{"text": f"Result of {operation}({x}{', ' + str(y) if y is not None else ''}): {result}"}]
        }
        
    except Exception as e:
        return {
            "toolUseId": tool_use_id,
            "status": "error",
            "content": [{"text": f"Error: {str(e)}"}]
        }