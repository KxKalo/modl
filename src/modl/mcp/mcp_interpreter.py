"""
Model Context Protocol (MCP) interpreter implementation for modl.
Handles translation between structured context and LLM interactions.
"""

from typing import List, Dict, Any, Optional, Callable
from .mcp_context import MCPContext, Tool


class MCPInterpreter:
    """
    Interprets and executes MCP context, handling tool calls and context management.
    """

    def __init__(self):
        self.tool_registry: Dict[str, Callable] = {}

    def register_tool(self, tool_name: str, tool_func: Callable):
        """Registers a new tool function."""
        self.tool_registry[tool_name] = tool_func

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Executes a registered tool with the given arguments."""
        if tool_name not in self.tool_registry:
            raise ValueError(f"Tool {tool_name} not registered")
        return await self.tool_registry[tool_name](**kwargs)

    def prepare_prompt(self, context: MCPContext) -> str:
        """
        Prepares the final prompt for the LLM by combining all context elements.
        """
        return context.to_prompt()

    def parse_tool_calls(self, llm_response: str) -> List[Dict[str, Any]]:
        """
        Parses tool calls from the LLM's response.
        Expected format: <tool>tool_name</tool>{"arg1": "value1", "arg2": "value2"}
        """
        tool_calls = []
        import re
        tool_pattern = r'<tool>(.*?)</tool>(.*?)(?=<tool>|$)'
        matches = re.finditer(tool_pattern, llm_response, re.DOTALL)
        
        for match in matches:
            tool_name = match.group(1).strip()
            try:
                import json
                args = json.loads(match.group(2).strip())
                tool_calls.append({
                    "tool": tool_name,
                    "args": args
                })
            except json.JSONDecodeError:
                continue
                
        return tool_calls

    async def process_llm_response(
        self, 
        context: MCPContext, 
        llm_response: str
    ) -> Dict[str, Any]:
        """
        Processes the LLM's response, executing any tool calls and updating context.
        """
        result = {
            "response": llm_response,
            "tool_results": []
        }

        # Parse and execute tool calls
        tool_calls = self.parse_tool_calls(llm_response)
        for tool_call in tool_calls:
            try:
                tool_result = await self.execute_tool(
                    tool_call["tool"],
                    **tool_call["args"]
                )
                result["tool_results"].append({
                    "tool": tool_call["tool"],
                    "result": tool_result
                })
                
                # Update context with tool results
                context.update_memory(
                    f"{tool_call['tool']}_result",
                    tool_result
                )
            except Exception as e:
                result["tool_results"].append({
                    "tool": tool_call["tool"],
                    "error": str(e)
                })

        return result

    def update_context_from_response(
        self,
        context: MCPContext,
        llm_response: str,
        tool_results: List[Dict[str, Any]]
    ):
        """
        Updates the context based on the LLM's response and tool results.
        """
        # Add the assistant's response to chat history
        context.add_chat_message("assistant", llm_response)
        
        # Update context with tool results
        for tool_result in tool_results:
            if "error" not in tool_result:
                context.update_memory(
                    f"{tool_result['tool']}_result",
                    tool_result["result"]
                ) 