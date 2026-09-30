class FakeLLM:

    def __init__(self,responses):
        self.responses=list(responses)
        self.calls=[]

    async def generate(
            self,
            messages,
            tools=None
    ):

        self.calls.append(
            {
                "messages":messages,
                "tools":tools
            }
        )

        if not self.responses:
            raise RuntimeError(
                "FakeLLM has no more responses"
            )

        return self.responses.pop(0)

class FakeFinalAnswerGenerator:
    """
    Fake Final Answer generator.

    Used to verify that IncidentAgent calls the final
    synthesis stage when the investigation is complete
    
    """

    def __init__(self,response="Final investigation report."):
        self.response=response
        self.called=False
        self.states=[]

    async def generate(self,state):
        self.states.append(state)
        self.called=True

        return self.response
        