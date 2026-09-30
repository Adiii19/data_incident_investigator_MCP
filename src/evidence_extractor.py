import json

from investigation_state import EvidenceItem
from tool_result_serializer import ToolResultSerializer


class EvidenceExtractor:

    def extract(
            self,
            tool_name:str,
            result
        )->list[EvidenceItem]:

        evidence=[]

        structured = getattr(result, "structured_content", None)
        if structured is None and isinstance(result, dict):
            structured = result

        if structured is None:
            summary = ToolResultSerializer.serialize(result)
        else:
            summary = json.dumps(structured, default=str, sort_keys=True)

        if summary and summary != "{}":
            evidence.append(
                EvidenceItem(
                    source=tool_name,
                    summary=summary,
                    category=self._category_for(tool_name),
                )
            )

        if tool_name!="investigate_pipeline":
            return evidence

        report =self ._get_report(result)

        if report is None:
            return evidence

        self._extract_failure_pattern(
            report,
            evidence
        )

        self._extract_error_patterns(
            report,
            evidence,
        )

        self._extract_dependencies(
            report,
            evidence,
        )

        return evidence

    def _category_for(self, tool_name):
        categories = {
            "get_pipeline_status": "pipeline_status",
            "get_recent_runs": "run_history",
            "get_pipeline_logs": "log",
            "get_pipeline_dependencies": "dependency",
            "get_incident_timeline": "timeline",
            "get_recent_deployments": "deployment",
            "check_database_health": "health",
        }
        return categories.get(tool_name, "tool_result")


    def _get_report(self,result):

        if hasattr(result,"structured_content"):

            structured=result.structured_content

            if structured:
                return structured.get(
                    "report"
                )

        return None

    def _extract_failure_pattern(
            self,report,evidence
    ):

        failure_pattern=report.get(
            "failure_pattern"
        )

        if not failure_pattern:
            return

        streak=failure_pattern.get(
            "failure_streak",
            0
        )

        if streak<=0:
            return

        evidence.append(
            EvidenceItem(
                source="investigate_pipeline",
                summary=(
                    f"Pipeline has failed"
                    f"{streak} consecutive times."
                ),
                category="failure_pattern"
            )
        )

    def _extract_error_patterns(
            self,report,evidence
    ):

        error_patterns=report.get(
            "error_patterns",
            []
        )

        for pattern in error_patterns:
            category=pattern.get(
                "category"
            )

            occurences=pattern.get(
                "occurences",
                0
            )

            if not category:
                continue

            evidence.append(
                EvidenceItem(
                    source="investigate_pipeline",
                    summary=(
                        f"Error category"
                        f"'{category}' occured"
                        f"{occurences} times"
                    ),
                    category="error"
                )
            )

    def _extract_dependencies(
    self,
    report,
    evidence,
):

     dependencies = report.get(
        "dependency_analysis",
        [],
    )

     for dependency in dependencies:

        name = dependency.get(
            "dependency_name"
        )

        matched_logs = dependency.get(
            "matched_logs",
            0,
        )

        if not name:
            continue

        evidence.append(
            EvidenceItem(
                source="investigate_pipeline",
                summary=(
                    f"Dependency '{name}' "
                    f"was associated with "
                    f"{matched_logs} relevant log events."
                ),
                category="dependency",
            )
        )
        

    