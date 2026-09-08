from pydantic import BaseModel

class IncidentAssessment(BaseModel):
    severity:str
    score:int
    confidence:str
    hypothesis:list[str]
    evidence:list[str]

    