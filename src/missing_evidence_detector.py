from dataclasses import dataclass

@dataclass
class MissingEvidence:

    category:str
    reason:str
    suggested_capability:str|None=None

class MissingEvidenceDetector:

    def detect(
            self,state
    )->list[MissingEvidence]:

        missing=[]

        categories={
            evidence.category
            for evidence in state.evidence_collected
        }

        executed_tools={
            execution.name
            for execution in state.tool_executions
        }

        if(
            "error" in categories
            and "timeline" not in categories
            and "get_incident_timeline"
            not in executed_tools
        ):
            missing.append(
                MissingEvidence(
                    category="timeline",
                    reason=(
                         "Error evidence exists, but "
                        "the event sequence before "
                        "failure has not been examined."
                    ),
                    suggested_capability=(
                        "get_incident_timeline"
                    )
                )
            )

        if (
            "error" in categories
            and "dependency" not in categories
            and "get_pipeline_dependencies"
            not in executed_tools
        ):
            missing.append(
                MissingEvidence(
                    category="dependency",
                    reason=(
                        "An error was detected, but "
                        "the pipeline dependencies have "
                        "not yet been examined."
                    ),
                    suggested_capability=(
                        "get_pipeline_dependencies"
                    ),
                )
            )


        return missing
    