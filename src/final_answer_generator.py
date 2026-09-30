from final_answer_prompt import FINAL_ANSWER_INSTRUCTIONS


class FinalAnswerGenerator:

    def __init__(self, llm, context_builder):
        self.llm = llm
        self.context_builder = context_builder

    async def generate(self, state) -> str:

        investigation_context = self.context_builder.build_final_context(state)

        messages = [
            {"role": "system", "content": (FINAL_ANSWER_INSTRUCTIONS)},
            {"role": "user", "content": (investigation_context)},
        ]

        response = await self.llm.generate(messages=messages, tools=[])

        content=response.content

        if not content:
            return (
                "Unable to generate a final"
                "investigation summary."
            )

        return self._clean_report(content)

    @staticmethod
    def _clean_report(content:str)->str:
            """
            Perform lightweight cleanup on the LLM Response.
             We intentionally do not rewrite  the report's
             meaning or alter investigation findings
            
            """
            content=content.strip()
        
            content=content.replace("\r\n","\n")
        
            while "\n\n\n" in content:
                content=content.replace(
                    "\n\n\n",
                    "\n\n"
                )
        
            return content

    