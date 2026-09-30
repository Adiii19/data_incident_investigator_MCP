import asyncio

from capability_registry import CapabilityRegistry
import context_manager
from evidence_extractor import EvidenceExtractor
from final_answer_generator import FinalAnswerGenerator
from groq_provider import GroqLLMProvider
from incident_agent import IncidentAgent
from investigation_context_builder import InvestigationContextBuilder
from mcp_client import MCPClient
from missing_evidence_detector import MissingEvidenceDetector
from tool_executor import ToolExecutor

async def main():
    client = MCPClient("http://127.0.0.1:8000/mcp")
    try:
        await client.connect()

        registry = CapabilityRegistry(client)
        evidence_extractor = EvidenceExtractor()
        missing_evidence_detector = MissingEvidenceDetector()
        context_builder = InvestigationContextBuilder()

        await registry.discover()

        llm = GroqLLMProvider()
        final_answer_generator = FinalAnswerGenerator(
            llm=llm,
            context_builder=context_builder,
        )

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

        print("Starting end-to-end investigation.....")

        result = await agent.run(
            pipeline_name="customer_sync",
            user_question="Investigate the customer_sync and determine why it is failing.",
        )

        print("\n")
        print("=" * 60)
        print("FINAL INVESTIGATION RESULT")
        print("=" * 60)
        print(result)
    finally:
        await client.disconnect()


if __name__=="__main__":
    asyncio.run(main())

