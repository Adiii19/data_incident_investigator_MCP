from pydantic import BaseModel

class RiskFactor(BaseModel):
    name:str
    score:int
    reason:str

class RiskAssessment(BaseModel):
    risk_level:str
    score:int
    factors:list[RiskFactor]