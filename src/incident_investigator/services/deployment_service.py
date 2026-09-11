from datetime import datetime,timedelta

from incident_investigator.repositories.pipeline_repository import PipelineRepository

class DeploymentService:

    def __init__(self, repository: PipelineRepository):
        self.repository = repository

    def get_recent_deployments(
            self,
            environment:str,
            failure_time:datetime,
            window_minutes:int=120,
    ):

        start_time=(
            failure_time - timedelta(minutes=window_minutes)
        )

        return self.repository.get_recent_deployments(
            environment=environment,
            start_time=start_time,
            end_time=failure_time
        )