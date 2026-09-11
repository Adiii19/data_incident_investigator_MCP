from pydantic import BaseModel

class DependencyEvidence(BaseModel):
    dependency_name:str
    dependency_type:str
    matched_logs:int
    confidence:str
    evidence:list[str]
