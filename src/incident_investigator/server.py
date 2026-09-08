from mcp.server import MCPServer

from incident_investigator.database.connection import engine
from incident_investigator.models import recommendation
from incident_investigator.models.requests import (
    PipelineStatusRequest,
    PipelineRunsRequest,
)
from incident_investigator.models.responses import PipelineStatusResponse
from incident_investigator.repositories.pipeline_repository import PipelineRepository
from incident_investigator.services import explaination_service, investigation_service
from incident_investigator.services import pipeline_service
from incident_investigator.services.pipeline_service import PipelineService
from incident_investigator.services.investigation_service import InvestigationService
from incident_investigator.services.health_service import HealthService
from incident_investigator.services.log_analysis_service import LogAnalysisService
from incident_investigator.services.timeline_service import TimelineService
from incident_investigator.services.explanation_service import(
    ExplanationService
)

mcp = MCPServer("Data Incident Investigator")
repository = PipelineRepository(engine)

service = PipelineService(repository)

health_service = HealthService(engine)
log_analysis_service = LogAnalysisService()
timeline_service=TimelineService()
explanation_service=ExplanationService()

investigation = InvestigationService(
     pipeline_service=service,
    log_analysis_service=log_analysis_service,
    timeline_service=pipeline_service,
    explanation_service=explanation_service,
)

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
def get_recent_runs(request: PipelineRunsRequest) -> dict:
    """
    Get recent execution runs for a data pipeline.
    Use this when investigating pipeline history
    or looking for patterns across recent runs.
    """
    runs = service.get_recent_runs(
        pipeline_name=request.pipeline_name,
        start_time=request.start_time,
        end_time=request.end_time,
        limit=request.limit,
    )

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
def investigate_pipeline(pipeline_name: str, limit: int = 10) -> dict:
    """
    Investigate recent execution history of a pipeline and
    identify failure patterns.

    
    """

    report=investigation_service.investigate_pipeline(
        pipeline_name
    )

    if report is None:
        return {
            "found":False,
            "pipeline_name":pipeline_name
        }

    return {
        "found": True,
        "report": report.model_dump(mode="json"),
    }

    # runs = service.get_recent_runs(pipeline_name, limit=limit)

    # if runs is None:
    #     return {"found": False, "pipeline_name": pipeline_name}

    # if not runs:
    #     return {"found": False, "pipeline_name": pipeline_name}

    # latest_run = runs[0]
    # historical_runs = runs[1:]

    # failure_analysis = investigation.analyze_failure_pattern(runs)

    # duration_analysis = investigation.analyze_duration(
    #     latest_run=latest_run, historical_runs=historical_runs
    # )

    # rows_count_analysis = investigation.analyze_row_counts(
    #     latest_run,
    #     historical_runs,
    # )

    # error_analysis = investigation.analyze_error_patterns(runs)

    # incident_assessment = investigation.build_incident_assessment(
    #     failure_analysis,
    #     duration_analysis,
    #     rows_count_analysis,
    #     error_analysis,
    # )

    # recommendations = investigation.generate_recommendation(
    #     incident_assessment.hypothesis, error_analysis
    # )

    # logs = service.get_latest_run_logs(pipeline_name)
    # root_cause_candidates = []

    # if logs:
    #     root_cause_candidates = log_analysis_service.detect_root_cause_candidates(logs)

    # dependencies = service.get_pipeline_dependencies(pipeline_name)

    # logs = service.get_latest_run_logs(pipeline_name)

    # dependency_analysis = []

    # if logs and dependencies:
    #     dependency_analysis = log_analysis_service.analyze_dependencies(
    #         logs, dependencies
    #     )

    # return {
    #     "found": True,
    #     "pipeline_name": pipeline_name,
    #     "analysis": {
    #         "failure_pattern": (failure_analysis.model_dump(mode="json")),
    #         "duration_anomaly": (duration_analysis.model_dump(mode="json")),
    #         "row_count_anomaly": (rows_count_analysis.model_dump(mode="json")),
    #         "error_patterns": (
    #             pattern.model_dump(mode="json") for pattern in error_analysis
    #         ),
    #         "incident": incident_assessment.model_dump(mode="json"),
    #         "recommendations": [
    #             recommendation.model_dump(mode="json")
    #             for recommendation in recommendations
    #         ],
    #         "root_cause_candidates": root_cause_candidates,
    #     },

    #     "dependency_analysis":[
    #         result.model_dump(mode="json")
    #         for result in dependency_analysis
    #     ]
    # }




@mcp.tool()
def check_database_health() -> dict:
    """
    Check whether the application's database connection is healthy.

    """
    return health_service.check_database_health()


@mcp.tool()
def get_pipeline_logs(pipeline_name: str, limit: int = 50) -> dict:
    """
    Get logs from the latest pipeline run.
    """

    logs = service.get_pipeline_logs(pipeline_name, limit)

    if logs is None:
        return {"found": False, "pipeline_name": pipeline_name}

    return {
        "found": True,
        "pipeline_name": pipeline_name,
        "logs": [log.model_dump(mode="json") for log in logs],
    }


@mcp.tool()
def get_pipeline_dependencies(
    pipeline_name: str,
) -> dict:
    """
    Get the external systems and services
    that a pipeline depends on.

    """

    dependencies = service.get_pipeline_dependencies(pipeline_name)

    if dependencies is None:
        return {"found": False, "pipeline_name": pipeline_name}

    return {
        "found": True,
        "pipeline_name": pipeline_name,
        "dependencies": [
            dependency.model_dump(mode="json") for dependency in dependencies
        ],
    }


@mcp.tool()
def get_incident_timeline(
    pipeline_name:str,
    limit:int=100
)->dict:

    """
    Reconstruct the timeline of the latest
    pipeline run.
    """

    logs=service.get_latest_run_logs(
        pipeline_name,
        limit
    )

    if logs is None:
        return {
            "found":False,
            "pipeline_name":pipeline_name
        }

    timeline=timeline_service.build_timeline(
        logs
    )
    pre_failure_events=(
        timeline_service.get_pre_failure_events(
            timeline
        )
    )

    return{

        "found":True,
        "pipeline_name":pipeline_name,
        "timeline":[
            event.model_dump(mode="json")
            for event in timeline
        ],
        "pre_failure_events":[
            event.model_dump(mode="json")
            for event in pre_failure_events
        ]

    }


if __name__ == "__main__":
    mcp.run()
