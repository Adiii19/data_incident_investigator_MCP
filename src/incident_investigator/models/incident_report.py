from pydantic import BaseModel

from incident_investigator.models.investigation import(
    FailurePattern,
    Evidence
)
from incident_investigator.models.error_pattern import(
    ErrorPattern,
)
from incident_investigator.models.dependency_analysis import (
    DependencyEvidence,
)
from incident_investigator.models.timeline import (
    TimelineEvent,
)
from incident_investigator.models.recommendation import (
    Recommendation,
)

from incident_investigator.models.incident import(
    IncidentAssessment
)

from incident_investigator.models.evidence_chain import(
    EvidenceChain
)

class IncidentReport(BaseModel):
    pipeline_name:str
    sassessment:IncidentAssessment

    failure_pattern:FailurePattern|None
    error_patterns:list[ErrorPattern]
    dependency_analysis:list[DependencyEvidence]

    timeline:list[TimelineEvent]

    root_cause_candidates:list[dict]

    evidence_chains:list[EvidenceChain]

    recommendations:list[Recommendation]
    evidence:list[str]