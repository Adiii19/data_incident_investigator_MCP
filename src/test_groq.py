import asyncio

from groq_provider import GroqLLMProvider
from tool_result_serializer import ToolResultSerializer


async def main():

    provider = GroqLLMProvider()

    response = await provider.generate(
        messages=[
            {
                "role": "user",
                "content": (
                    "What is the current status of "
                    "the customer_sync?"
                ),
            }
        ],
        tools=[
            {
                "name": "get_pipeline_status",
                "description": (
                    "Get the current status of a data pipeline."
                ),
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "request": {
                            "type": "object",
                            "properties": {
                                "pipeline_name": {
                                    "type": "string"
                                },
                                "limit": {
                                    "type": "integer"
                                },
                            },
                            "required": [
                                "pipeline_name"
                            ],
                        }
                    },
                    "required": [
                        "request"
                    ],
                },
            }
        ],
    )

    print("LLM response:")
    print(response)

    print("\nTool calls:")

    for tool_call in response.tool_calls:
        print("ID:", tool_call.id)
        print("Name:", tool_call.name)
        print("Arguments:", tool_call.arguments)


if __name__ == "__main__":
    asyncio.run(main())