import asyncio

from mcp_client import MCPClient
from capability_registry import CapabilityRegistry
from tool_executor import ToolExecutor\

async def main():
    client=MCPClient(
        "http://127.0.0.1:8000/mcp"
    )

    await client.connect()

    try:

        registry=CapabilityRegistry(client)

        await registry.discover()

        executor=ToolExecutor(
            client,
            registry,
        )

        result=await executor.execute(
            "get_pipeline_status",
            {
                "request":{
                    "pipeline_name":"customer_sync",
                    "limit":5,
                }
            }
        )

        print(result)

        # print("Available tools:")

        # for tool in registry.get_tools():
        #     print(f"-{tool['name']}")

        #     print(
        #         f"Description: "
        #         f"{tool['description']}"
        #     )

        #     print(
        #         f"Input schema: "
        #         f"{tool['input_schema']}"
        #     )

        # print("\nAvailable resources:")

        # for resource in registry.get_resources():

        #     print(
        #         f"\nURI: {resource['uri']}"
        #     )

        #     print(
        #         f"Name: {resource['name']}"
        #     )

        #     print(
        #         f"Description: "
        #         f"{resource['description']}"
        #     )

        # print("\nAvailable resource templates:")

        # for template in registry.get_resource_templates():

        #     print(
        #         f"\nURI template: {template['uri_template']}"
        #     )

        #     print(
        #         f"Description: "
        #         f"{template['description']}"
        #     )

        #     print(
        #         f"MIME type: "
        #         f"{template['mime_type']}"
        #     )

    finally:
        await client.disconnect()


if __name__=="__main__":
    asyncio.run(main())
