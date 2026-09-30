from agent_models import LLMResponse
from investigation_policy import INVESTIGATION_POLICY
from tool_executor import ToolExecutor
from tool_result_serializer import ToolResultSerializer
from investigation_state import InvestigationState
from context_manager import ContextManager
from agent_errors import ToolExecutionError


class IncidentAgent:

    def __init__(
        self,
        mcp_client,
        capability_registry,
        tool_executor,
        llm,
        evidence_extractor,
        missing_evidence_detector,
        context_manager,
        final_answer_generator,
    ):
        self.llm = llm
        self.tool_executor = tool_executor
        self.capability_registry = capability_registry
        self.context_manager = context_manager
        self.final_answer_generator = final_answer_generator
        self.evidence_extractor = evidence_extractor
        self.missing_evidence_detector = missing_evidence_detector

    async def run(
        self, pipeline_name: str, user_question: str, max_iterations: int = 10
    ):

        state = InvestigationState(pipeline_name=pipeline_name)

        messages = [
            {"role": "system", "content": INVESTIGATION_POLICY},
            {"role": "user", "content": user_question},
        ]

        tools = self.capability_registry.get_tools()

        for _ in range(max_iterations):
            state.increment_iteration()
            response = await self.llm.generate(messages=messages, tools=tools)

            if not response.tool_calls:
                state.completed = True
                return await self.final_answer_generator.generate(state)

            assistant_message = getattr(response, "assistant_message", None)
            if assistant_message is not None:
                messages.append(response.assistant_message)

            for tool_call in response.tool_calls:

                if state.already_executed(tool_call.name, tool_call.arguments):
                    continue

                state.record_tool(tool_call.name, tool_call.arguments)

                print(f"Executing tool: {tool_call.name}")

                try:
                    result = await self.tool_executor.execute(
                        tool_call.name, tool_call.arguments
                    )

                except ToolExecutionError as exc:
                    print(f"Tool execution failed:{exc.tool_name}")

                    state.record_evidence(
                        source=exc.tool_name,
                        summary=(f"Tool execution failed" f"{str(exc)}"),
                        category="tool_failure",
                    )

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": (
                                f"Tool execution failed. "
                                f"Tool: {exc.tool_name}. "
                                f"Error: {str(exc)}"
                            ),
                        }
                    )

                    continue

                evidence_items = self.evidence_extractor.extract(tool_call.name, result)

                for evidence in evidence_items:
                    state.record_evidence(
                        source=evidence.source,
                        summary=evidence.summary,
                        category=evidence.category,
                    )

                missing_evidence = self.missing_evidence_detector.detect(state)

                tool_content = ToolResultSerializer.serialize(result)

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": tool_content,
                    }
                )

                if missing_evidence:

                    missing_summary = "\n".join(
                        (f"={item.category}:" f"{item.reason}")
                        for item in missing_evidence
                    )

                    messages.append(
                        {
                            "role": "system",
                            "content": (
                                "Additional evidence may be "
                                "required before concluding "
                                "the investigation.\n\n"
                                "Potential missing evidence:\n"
                                f"{missing_summary}\n\n"
                                "Use your judgment to determine "
                                "whether additional MCP tools "
                                "are necessary."
                            ),
                        }
                    )
                    messages = self.context_manager.trim(messages)

        raise RuntimeError("Investigation exceeded tha maximum number of iterations")
