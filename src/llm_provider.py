from abc import ABC,abstractmethod

class LLMProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        messages:list[dict],
        tools:list[dict]
    ):
        pass