import json
from typing import Any, Dict


def format_memory_for_prompt(memory_context: Dict[str, Any]) -> str:
    if not memory_context:
        return "No relevant memory available."

    return json.dumps(memory_context, indent=2, ensure_ascii=False)

def format_mcp_for_prompt(mcp_context: Dict[str, Any]) -> str:
    if not mcp_context:
        return "No MCP data available."

    return json.dumps(mcp_context, indent=2, ensure_ascii=False)