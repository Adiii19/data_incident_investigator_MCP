from agent_errors import AgentError, ToolExecutionError

class ToolExecutor:

    def __init__(self,mcp_client,capability_registry):
        self.mcp_client=mcp_client
        self.capability_registry=capability_registry

    def tool_exists(self,tool_name:str)->bool:
            tools=self.capability_registry.get_tools()

            return any(
                 tool["name"]==tool_name
                 for tool in tools
            )

    async def execute(
            self,
            tool_name:str,
            arguments:dict
    ):

        if not self.tool_exists(tool_name):
        
         return {
             "success":False,
             "error":"unknown_tool",
             "message":(
                 f"Unknown MCP tool:{tool_name}"
             )
         }

        try:

            result=await self.mcp_client.call_tool(
                tool_name,
                arguments,
            )

            return result

        except Exception as exc:

            raise ToolExecutionError(
                tool_name=tool_name,
                message=str(exc),
                original_error=exc
            )