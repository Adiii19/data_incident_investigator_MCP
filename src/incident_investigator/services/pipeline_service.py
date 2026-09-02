from incident_investigator.models.pipeline import Pipeline
from incident_investigator.repositories.pipeline_repository import (
    PipelineRepository,
)
from datetime import datetime


class PipelineService:

    def __init__(self, repository: PipelineRepository):
        self.repository = repository

    def get_pipeline_status(self, pipeline_name: str):
        pipeline = self.repository.get_pipeline_by_name(pipeline_name)

        if pipeline is None:
            return None

        latest_run = self.repository.get_latest_run(pipeline.id)

        return {"pipeline": pipeline, "latest_run": latest_run}

    def get_recent_runs(self,pipeline_name:str,start_time:datetime|None=None,end_time:datetime|None=None,limit:int=10):

        pipeline=self.repository.get_pipeline_by_name(
            pipeline_name
        )

        if pipeline is None:
            return None

        return self.repository.get_recent_runs(
            pipeline.id,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )