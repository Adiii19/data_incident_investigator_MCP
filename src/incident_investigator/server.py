from mcp.server import MCPServer
import time
from datetime import datetime
from typing import Annotated

from pydantic import Field


from incident_investigator.database.connection import engine
from incident_investigator.models import recommendation
from incident_investigator.models.responses import PipelineStatusResponse
from incident_investigator.observablity import create_investigation_id
from incident_investigator.repositories.pipeline_repository import PipelineRepository
from incident_investigator.services import explanation_service, investigation_service
from incident_investigator.services import pipeline_service
from incident_investigator.services.deployment_service import DeploymentService
from incident_investigator.services.pipeline_service import PipelineService
from incident_investigator.services.investigation_service import InvestigationService
from incident_investigator.services.health_service import HealthService
from incident_investigator.services.log_analysis_service import LogAnalysisService
from incident_investigator.services.timeline_service import TimelineService
from incident_investigator.services.explanation_service import(
    ExplanationService
)
from incident_investigator.services.deployment_correlation_service import(
    DeploymentCorrelationService
)
from incident_investigator.services.risk_assessment_service import (
    RiskAssessmentService,
)
import logging
from incident_investigator.logging_config import (
    configure_logging
)


mcp = MCPServer("Data Incident Investigator")
repository = PipelineRepository(engine)
configure_logging()
service = PipelineService(repository)
logger=logging.getLogger(__name__)

health_service = HealthService(engine)
log_analysis_service = LogAnalysisService()
timeline_service=TimelineService()
explanation_service=ExplanationService()
deployment_service=DeploymentService(
    repository
)
deployment_correlation_service=(
    DeploymentCorrelationService()
)

risk_assessment_service=RiskAssessmentService()


investigation = InvestigationService(
     pipeline_service=service,
    log_analysis_service=log_analysis_service,
    timeline_service=timeline_service,

    deployment_service=deployment_service,
    deployment_correlation_service=(
        deployment_correlation_service
    ),
    explanation_service=explanation_service,
    risk_assessment_service=risk_assessment_service
)



@mcp.tool()
def get_pipeline_status(
    pipeline_name: Annotated[
        str,
        Field(
            min_length=1,
            description="Name of the data pipeline to inspect.",
        ),
    ],
) -> PipelineStatusResponse:
    """
    Get the current status and latest execution information
    for a data pipeline.
    """
    result = service.get_pipeline_status(pipeline_name)

    if result is None:
        return PipelineStatusResponse(found=False)

    return PipelineStatusResponse(
        found=True, pipeline=result["pipeline"], latest_run=result["latest_run"]
    )


@mcp.tool()
def get_recent_runs(
    pipeline_name: Annotated[
        str,
        Field(min_length=1, description="Name of the pipeline"),
    ],
    start_time: Annotated[
        datetime | None,
        Field(description="Only include runs starting at or after this timestamp."),
    ] = None,
    end_time: Annotated[
        datetime | None,
        Field(description="Only include runs starting before or at this timestamp."),
    ] = None,
    limit: Annotated[
        int,
        Field(
            ge=1,
            le=100,
            description="Maximum number of runs to return",
        ),
    ] = 10,
) -> dict:
    """
    Get recent execution runs for a data pipeline.
    Use this when investigating pipeline history
    or looking for patterns across recent runs.
    """
    runs = service.get_recent_runs(
        pipeline_name=pipeline_name,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )

    if runs is None:
        return {
            "found": False,
            "pipeline_name": pipeline_name,
        }

    return {
        "found": True,
        "pipeline_name": pipeline_name,
        "runs": [run.model_dump(mode="json") for run in runs],
    }


@mcp.tool()
def investigate_pipeline(pipeline_name: str, limit: int = 10) -> dict:
    """
    Investigate recent execution history of a pipeline and
    identify failure patterns.

    
    """
    investigation_id=create_investigation_id()
    start_time=time.perf_counter()

    logger.info(
        "event=investigation_started"
        "pipeline=%s"
        "investigation_id=%s",
        pipeline_name,
        investigation_id
    )

    investigation
    try:
        report = investigation.investigate_pipeline(
                pipeline_name,
                limit=limit,
            )
    except Exception:

        elapsed_ms=(
            time.perf_counter()-start_time
        )*1000

        logger.exception(
            "event=investigation_failed"
            "pipeline=%s"
            "investigation_id=%s"
            "duration_ms=%.2f",
            pipeline_name,
            investigation_id,
            elapsed_ms
        )

        raise

    elapsed_ms=(
        time.perf_counter()-start_time
    )*1000



    if report is None:
        return {
            "found":False,
            "pipeline_name":pipeline_name
        }

    logger.info(
        "event=investigation_completed "
        "pipeline=%s "
        "investigation_id=%s "
        "duration_ms=%.2f",
        pipeline_name,
        investigation_id,
        elapsed_ms,
    )

    return {
        "found": True,
        "investigation_id": investigation_id,
        "report": report.model_dump(mode="json"),
    }

   
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

@mcp.tool()
def get_recent_deployments(
    pipeline_name:str,
    window_minutes:int=120
)->dict:

    pipeline=service.get_pipeline(
        pipeline_name
    )

    if pipeline is None:
        return {
            "found":False,
            "pipeline_name":pipeline_name
        }

    latest_run=service.repository.get_latest_run(
        pipeline.id
    )

    if latest_run is None:
        return {

            "found":False,
            "pipeline_name":pipeline_name,
            "message":"No pipeline runs found."

        }

    failure_time=(
        latest_run.completed_at 
        or latest_run.started_at
    )

    deployments=(
        deployment_service.get_recent_deployments(
            environment=pipeline.environment,
            failure_time=failure_time,
            window_minutes=window_minutes
        )
    )

    return {

        "found":True,
        "pipeline_name":pipeline_name,
        "deployments":[
            deployment.model_dump(
                mode="json"
            )
            for deployment in deployments
        ]

    }

@mcp.resource(
    "pipeline://{pipeline_name}",
    name="pipeline_details",
    description="Get details about a data pipeline",
    mime_type="application/json"

)
def get_pipeline_resource(
    pipeline_name:str
)->dict:

    pipeline=service.get_pipeline(
        pipeline_name
    )

    if pipeline is None:
        return {
            "found":False,
            "pipeline_name":pipeline_name,
        }

    return{
        "found":True,
        "pipeline":pipeline.model_dump(
            mode="json"
        )
    }




@mcp.resource(
    "incident://{pipeline_name}/latest",
    name="latest_incident_context",
    description=(
        "Get the latest operational context"
        "for a pipeline incident"
    ),
    mime_type="application/json"
)
def get_latest_incident_context_resource(
    pipeline_name:str,
)->dict:

    context=(
        investigation.get_latest_incident_context(
            pipeline_name
        )
    
    )

    if context is None:
        return {
            "found":False,
            "pipeline_name":pipeline_name
        }

    return {
        "found":True,
        "context":context.model_dump(
            mode="json"
        )
    }

@mcp.prompt()
def investigate_incident(
    pipeline_name:str,
)->str:

    return f"""

Investigate the data pipeline incident for:

Pipeline:{pipeline_name}

Follow this investigation process:
1. Inspect the latest incident context.
2. Review the latest pipeline run and recent run history.
3. Analyse pipeline logs for recurring or significant errors.
4. Examine pipeline dependencies.
5. Review the incident timeline and events immediately 
    preceding the failure.
6. Check for recent deployments that may correlate with the incident.
7. Compare all available evidence.
8. Identify plausible root-cause hypotheses.
9. Clearly distinguish observation, evidence, correlations and hypotheses.
10. Provide actionable recommendations.

Do not claim a root cause as confirmed unless the evidence supports it.

"""


if __name__ == "__main__":
    mcp.run()
