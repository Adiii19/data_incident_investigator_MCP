from pydantic import BaseModel

class EvidenceChain(BaseModel):

    observation:str
    evidence:list[str]
    correlation:str|None
    hypothesis:str
    confidence:str
    recommendation:list[str]