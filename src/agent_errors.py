class AgentError(Exception):
    """Base exception for agent errors."""

class ToolExecutionError(AgentError):
    """Raised when an MCP tool cannot be executed"""

    def __init__(
            self,
            tool_name:str,
            message:str,
            original_error:Exception|None=None
    ):
        self.tool_name=tool_name
        self.original_error=original_error

        super().__init__(
            f"Tool '{tool_name}' failed:{message} "
        )