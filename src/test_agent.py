import asyncio
import context_manager
from evidence_extractor import EvidenceExtractor
from mcp_client import MCPClient
from capability_registry import CapabilityRegistry
from missing_evidence_detector import MissingEvidenceDetector
from tool_executor import ToolExecutor
from groq_provider import GroqLLMProvider
from incident_agent import IncidentAgent
from evidence_extractor import EvidenceExtractor
from missing_evidence_detector import MissingEvidenceDetector
from investigation_context_builder import InvestigationContextBuilder
from final_answer_generator import FinalAnswerGenerator


async def main():

    client = MCPClient("http://127.0.0.1:8000/mcp")

    await client.connect()

    try:

        registry = CapabilityRegistry(client)
        evidence_extractor = EvidenceExtractor()
        missing_evidence_detector = MissingEvidenceDetector()
        context_builder = InvestigationContextBuilder()

        llm = GroqLLMProvider()
        final_answer_generator = FinalAnswerGenerator(
            llm=llm,
            context_builder=context_builder,
        )

        await registry.discover()

        executor = ToolExecutor(
            mcp_client=client,
            capability_registry=registry,
        )

        agent = IncidentAgent(
            llm=llm,
            tool_executor=executor,
            capability_registry=registry,
            evidence_extractor=evidence_extractor,
            missing_evidence_detector=missing_evidence_detector,
            mcp_client=client,
            context_manager=context_manager,
            final_answer_generator=final_answer_generator,
        )

        answer = await agent.run(
            pipeline_name="customer_sync",
            user_question=("why did customer_sync fail ?"),
        )

        print("\nFinal answer:")
        print(answer)

    finally:

        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
