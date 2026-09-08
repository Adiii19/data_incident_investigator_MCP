from pydantic import BaseModel

class DependencyEvidence(BaseModel):
    dependency_name:str
    dependency_type:str
    matched_logs:int
    confidenc:str
    evidence:list[str]
