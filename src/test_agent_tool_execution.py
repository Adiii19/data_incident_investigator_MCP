import asyncio

from mcp_client import MCPClient
from capability_registry import CapabilityRegistry
from tool_executor import ToolExecutor
from groq_provider import GroqLLMProvider

async def main():

    client=MCPClient(
        "http://127.0.0.1:8000/mcp"
    )

    await client.connect()

    try:

        registry=CapabilityRegistry(client)
        await registry.discover()

        executor=ToolExecutor(
            mcp_client=client,
            capability_registry=registry
        )

        llm=GroqLLMProvider()

        response=await llm.generate(

            messages=[
                {
                    "role":"user",
                    "content":(
                        "what is the current status of"
                        "the customer_sync ?"
                    )
                }
            ],
            tools=registry.get_tools()

        )

        print("\n LLM Response")
        print(response)

        for tool_call in response.tool_calls:
            print(

                f"\n Executing tool:"
                f"{tool_call.name}"

            )


            result = await executor.execute(
                tool_call.name,
                tool_call.arguments,
            )

            print("\nTool result:")
            print(result)

    finally:
        await client.disconnect()

if __name__=="__main__":
    asyncio.run(main())
