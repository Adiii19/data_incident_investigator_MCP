import json
from groq import AsyncGroq
from dotenv import load_dotenv

from agent_models import LLMResponse, ToolCall
from llm_provider import LLMProvider
from tool_schema_adapter import ToolSchemaAdapter

load_dotenv()


class GroqLLMProvider(LLMProvider):

    def __init__(self, model: str = "openai/gpt-oss-120b"):
        self.model = model
        self.client = AsyncGroq()

    async def generate(self, messages: list[dict], tools: list[dict]) -> LLMResponse:

        groq_tools = ToolSchemaAdapter.to_groq(tools)

        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, tools=groq_tools, tool_choice="auto"
        )

        message = response.choices[0].message

        tool_calls = []

        assistant_message = {"role": "assistant", "content": message.content}

        if message.tool_calls:

            tool_calls = [
                ToolCall(
                    id=call.id,
                    name=call.function.name,
                    arguments=json.loads(call.function.arguments),
                )
                for call in message.tool_calls
            ]

            assistant_message["tool_calls"] = [
                {
                    "id": call.id,
                    "type": "function",
                    "function": {
                        "name": call.function.name,
                        "arguments": call.function.arguments,
                    },
                }
                for call in message.tool_calls
            ]

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            assistant_message=assistant_message,
        )

    def build_assistant_tool_message(self, response) -> dict:

        tool_calls = []

        if response.choices[0].message.tool_calls:

            for call in response.choices[0].message.tool_calls:
                tool_calls.append(
                    {
                        "id": call.id,
                        "type": "function",
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                )

        return {
            "role": "assistant",
            "content": response.choices[0].message.content,
            "tool_calls": tool_calls,
        }
