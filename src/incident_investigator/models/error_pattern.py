from pydantic import BaseModel
from incident_investigator.models.investigation import Evidence

class ErrorPattern(BaseModel):
    category:str
    occurrences:int
    latest_message:str|None
    evidence:list[Evidence]

    
