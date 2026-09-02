from incident_investigator.models.pipeline import Pipeline
from incident_investigator.models.pipeline_run import PipelineRun
from pydantic import BaseModel

class PipelineStatusResponse(BaseModel):
    found:bool
    pipeline:Pipeline|None=None
    latest_run:PipelineRun|None=None
    
