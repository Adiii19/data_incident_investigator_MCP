class FakeToolExecutor:

    """
    Fake ToolExecutor used by agent tests.

    It does not communicate with MCP.

    Instead , it returns predefined results for specific 
    tool names.
    
    """


    def __init__(self,results=None):
        self.results=results or []
        self.calls=[]


    async def execute(
            self,
            tool_name,
            arguments
    ):
        self.calls.append(
            {
                "tool_name":tool_name,
                "arguments":arguments
            }
        )

        if tool_name not in self.results:
            raise RuntimeError(
                f"No fake result configured "
                f"for {tool_name}"
            )

        result = self.results[tool_name]

        if isinstance(result, Exception):
            raise result

        return result