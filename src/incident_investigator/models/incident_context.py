from pydantic import BaseModel

from incident_investigator.models.pipeline_run import(
    PipelineRun
)
from incident_investigator.models.pipeline_log import(
    PipelineLog
)
from incident_investigator.models.dependency import(
    PipelineDependency
)

class IncidentContext(BaseModel):
    pipeline_name:str
    latest_run:PipelineRun|None
    recent_runs:list[PipelineRun]
    logs:list[PipelineLog]
    dependencies:list[PipelineDependency]