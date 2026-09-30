from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

class MCPClient:

    def __init__(self,server_url:str):
        self.server_url = server_url

        self._transport = None
        self._session = None

    async def connect(self):
        self._transport=streamable_http_client(
            self.server_url
        )

        (

            self.read_stream,
            self.write_stream,

        )= await self._transport.__aenter__()

        self._session=ClientSession(
            self.read_stream,
            self.write_stream,
        )

        await self._session.__aenter__()

        await self._session.initialize()

    async def disconnect(self):

        if self._session is not None:
            await self._session.__aexit__(
                None,None,None
            )
        if self._transport is not None:
            await self._transport.__aexit__(
                None,None,None
            )

    async def list_tools(self):
        return await self._session.list_tools()

    async def call_tool(
                self,
                name:str,
                arguments:dict
        ):
            return await self._session.call_tool(
                name,
                arguments=arguments
            )

    async def list_resources(self):

        return await self._session.list_resources()

    async def list_resource_templates(self):

        return await self._session.list_resource_templates()

    async def read_resources(
                self,
                uri:str,
        ):

            return await self._session.read_resource(uri)