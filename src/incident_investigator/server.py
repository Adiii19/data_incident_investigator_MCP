from mcp.server import MCPServer

from incident_investigator.database.connection import engine
from incident_investigator.models.requests import PipelineStatusRequest,PipelineRunsRequest
from incident_investigator.models.responses import PipelineStatusResponse
from incident_investigator.repositories.pipeline_repository import PipelineRepository
from incident_investigator.services.pipeline_service import PipelineService
from incident_investigator.services.investigation_service import InvestigationService


mcp = MCPServer("Data Incident Investigator")
repository = PipelineRepository(engine)

service = PipelineService(repository)
investigation = InvestigationService()


@mcp.tool()
def get_pipeline_status(request: PipelineStatusRequest) -> PipelineStatusResponse:
    """
    Get the current status and latest execution information
    for a data pipeline.
    """
    result = service.get_pipeline_status(request.pipeline_name)

    if result is None:
        return PipelineStatusResponse(found=False)

    return PipelineStatusResponse(
        found=True, pipeline=result["pipeline"], latest_run=result["latest_run"]
    )


@mcp.tool()
def get_recent_runs(request:PipelineRunsRequest ) -> dict:
    """
    Get recent execution runs for a data pipeline.
    Use this when investigating pipeline history
    or looking for patterns across recent runs.
    """
    runs = service.get_recent_runs(pipeline_name=request.pipeline_name, start_time=request.start_time,end_time=request.end_time,limit=request.limit)

    if runs is None:
        return {
            "found": False,
            "pipeline_name": request.pipeline_name,
        }

    return {
        "found": True,
        "pipeline_name": request.pipeline_name,
        "runs": [run.model_dump(mode="json") for run in runs],
    }

@mcp.tool()
def investigate_pipeline(
    pipeline_name:str,
    limit:int=10
)->dict:
    """
    Investigate recent execution history of a pipeline and 
    identify failure patterns.
    
    """
    runs=service.get_recent_runs(
        pipeline_name,
        limit=limit
    )

    if runs is None:
        return{
            "found":False,
            "pipeline_name":pipeline_name
        }

    if not runs:
        return{
            "found":False,
            "pipeline_name":pipeline_name
        }

    latest_run=runs[0]
    historical_runs=runs[1:]

    failure_analysis=investigation.analyze_failure_pattern(
        runs
    )

    duration_analysis=(
        investigation.analyze_duration(
            
            latest_run=latest_run,
            historical_runs=historical_runs
        )
    )

    return {
        "found":True,
        "pipeline_name":pipeline_name,
        "analysis":{
            "failure_pattern":(
                failure_analysis.model_dump(
                    mode="json"
                )
            ),
            "duration_anomaly":(
                duration_analysis.model_dump(
                    mode="json"
                )
            )
        }
    }



if __name__ == "__main__":
    mcp.run()

