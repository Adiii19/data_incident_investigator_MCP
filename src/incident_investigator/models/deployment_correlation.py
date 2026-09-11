from pydantic import BaseModel

class DeploymentCorrelation(BaseModel):
    service_name:str
    version:str
    deployed_at:str
    minutes_before_failure:float
    score:int
    confidence:str
    reasons:list[str]