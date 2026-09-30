import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():

    async with streamable_http_client(
        "http://127.0.0.1:8000/mcp"
    ) as (
        read_stream,
        write_stream,
        
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            print("Connected to MCP server!")

            tools = await session.list_tools()

            print("\nAvailable tools:")

            for tool in tools.tools:
                print(f"- {tool.name}")

            result=await session.call_tool(
                "get_pipeline_status",
                arguments={
                    "request":{
                        "pipeline_name":"customer_sync",
                        "limit":5
                    }
                }
            )
            print("\nTool result:")
            print(result)

            resources=await session.list_resources()
            print("\n Available resources:")

            incident_context=await session.read_resource(
                "incident://customer_sync/latest"
            )
            print("\nIncident context:")
            print(incident_context)
            


if __name__ == "__main__":
    asyncio.run(main())