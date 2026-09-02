from pydantic import BaseModel
from datetime import timedelta

class FailurePattern(BaseModel):
    failure_streak:int
    total_runs_analyzed:int
    latest_status:str|None
    previous_success_found:bool

class Evidence(BaseModel):
    category:str
    description:str
    severity:str

class DurationAnomaly(BaseModel):
    detected:bool
    latest_duration_seconds:float|None
    historical_average_seconds:float|None
    duration_ratio:float|None
    evidence:list[Evidence]

  