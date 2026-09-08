from datetime import timedelta
from incident_investigator.models.incident import IncidentAssessment
from incident_investigator.models.error_pattern import ErrorPattern
from incident_investigator.models.incident_report import IncidentReport
from incident_investigator.models.investigation import (
    DurationAnomaly,
    FailurePattern,
    Evidence,
    RowCountAnomaly,
)
from incident_investigator.models.recommendation import Recommendation
from incident_investigator.services import deployment_service, explanation_service


class InvestigationService:

    def __init__(self, pipeline_service, log_analysis_service, timeline_service):
        self.pipeline_service = pipeline_service
        self.log_analysis_service = log_analysis_service
        self.timeline_service = timeline_service
        self.explanation_service=explanation_service
        self.deployment_service=deployment_service

    def analyze_failure_pattern(self, runs):
        if not runs:
            return FailurePattern(
                failure_streak=0,
                total_runs_analyzed=0,
                latest_status=None,
                previous_success_found=False,
            )

        failure_streak = 0

        for run in runs:

            if run.status.upper() == "FAILED":
                failure_streak += 1
            else:
                break

        previous_success_found = any(
            run.status.upper() == "SUCCESS" for run in runs[failure_streak:]
        )

        evidence = []

        if failure_streak >= 2:
            evidence.append(
                Evidence(
                    category="failure_pattern",
                    description=(
                        f"The pipeline has failed"
                        f"{failure_streak} consecutive times."
                    ),
                    severity="high",
                )
            )

        if previous_success_found and failure_streak > 0:
            evidence.append(
                Evidence(
                    category="regression",
                    description=(
                        "The pipeline had successful runs"
                        "before the current failure streak."
                    ),
                    severity="medium",
                )
            )

        return FailurePattern(
            failure_streak=failure_streak,
            total_runs_analyzed=len(runs),
            latest_status=runs[0].status,
            previous_success_found=previous_success_found,
            evidence=evidence,
        )

    def calculate_duration(self, run) -> timedelta | None:

        if run.completed_at is None:
            return None

        return run.completed_at - run.started_at

    def calculate_average_duration(self, runs):

        durations = []

        for run in runs:

            duration = self.calculate_duration(run)

            if duration is not None:
                durations.append(duration.total_seconds())

        if not durations:
            return None

        return sum(durations) / len(durations)

    def calculate_average(
        self,
        values: list[int | float],
    ) -> float | None:

        if not values:
            return None

        return sum(values) / len(values)

    def analyze_duration(self, latest_run, historical_runs):

        latest_duration = self.calculate_duration(latest_run)

        if latest_duration is None:
            return DurationAnomaly(
                detected=False,
                latest_duration_seconds=None,
                historical_average_seconds=None,
                duration_ratio=None,
                evidence=[],
            )

        historical_average = self.calculate_average_duration(historical_runs)

        if historical_average is None:
            return DurationAnomaly(
                detected=False,
                latest_duration_seconds=(latest_duration.total_seconds()),
                historical_average_seconds=None,
                duration_ratio=None,
                evidence=[],
            )

        latest_seconds = latest_duration.total_seconds()

        ratio = latest_seconds / historical_average

        evidence = []

        if ratio >= 2.0:
            evidence.append(
                Evidence(
                    category="duration_anomaly",
                    description=(
                        f"The latest run took"
                        f"{ratio:.1f}x longer that the "
                        f"historical average."
                    ),
                    severity="high",
                )
            )

        return DurationAnomaly(
            detected=ratio >= 2.0,
            latest_duration_seconds=latest_seconds,
            historical_average_seconds=historical_average,
            duration_ratio=ratio,
            evidence=evidence,
        )

    def analyze_row_counts(self, latest_run, historical_runs):

        historical_rows_read = [
            run.rows_read for run in historical_runs if run.rows_read is not None
        ]

        historical_rows_written = [
            run.rows_written for run in historical_runs if run.rows_written is not None
        ]

        average_rows_read = self.calculate_average(historical_rows_read)
        average_rows_written = self.calculate_average(historical_rows_written)

        latest_rows_read = latest_run.rows_read
        latest_rows_written = latest_run.rows_written

        rows_read_ratio = None
        rows_written_ratio = None

        if average_rows_read is not None and average_rows_read > 0:
            rows_read_ratio = latest_rows_read / average_rows_read

        rows_read_anomaly = rows_read_ratio is not None and rows_read_ratio < 0.5

        if average_rows_written is not None and average_rows_written > 0:
            rows_written_ratio = latest_rows_written / average_rows_written

        rows_written_anomaly = (
            rows_written_ratio is not None and rows_written_ratio < 0.5
        )

        evidence = []

        if rows_read_anomaly:
            evidence.append(
                Evidence(
                    category="input_volume_anomaly",
                    description=(
                        f"The latest run processed only"
                        f"{rows_read_ratio:.1%} of the "
                        f"historical average input volume"
                    ),
                    severity="high",
                )
            )

        if rows_written_anomaly:
            evidence.append(
                Evidence(
                    category="output_volume_anomaly",
                    description=(
                        f"The latest run produced only "
                        f"{rows_written_ratio:.1%} of the "
                        f"historical average output volume."
                    ),
                    severity="high",
                )
            )

        return RowCountAnomaly(
            rows_read_anomaly=rows_read_anomaly,
            rows_written_anomaly=rows_written_anomaly,
            latest_rows_read=latest_rows_read,
            historical_average_rows_read=average_rows_read,
            latest_rows_written=latest_rows_written,
            historical_average_rows_written=average_rows_written,
            rows_read_ratio=rows_read_ratio,
            rows_written_ratio=rows_written_ratio,
            evidence=evidence,
        )

    def classify_error(self, error_message: str | None) -> str | None:

        if not error_message:
            return None

        message = error_message.lower()

        if "timeout" in message:
            return "connection_timeout"

        if "authentication" in message or "password" in message:
            return "schema_mismatch"

        if "duplicate" in message:
            return "duplicate_key"

        if "permission" in message or "denied" in message:
            return "permission_denied"

        if "out of memory" in message or "memory" in message:
            return "out_of_memory"

        if "rate limit" in message or "too many requests" in message:
            return "api_rate_limit"

        return "unknown"

    def analyze_error_patterns(self, runs):

        error_counts = {}
        latest_messages = {}

        for run in runs:
            category = self.classify_error(run.error_message)

            if category is None:
                continue

            error_counts[category] = error_counts.get(category, 0) + 1

            if category not in latest_messages:
                latest_messages[category] = run.error_message

        patterns = []

        for category, count in error_counts.items():

            evidence = []

            if count >= 2:
                evidence.append(
                    Evidence(
                        category="repeated_error",
                        description=(
                            f"The error pattern"
                            f"{category} occured"
                            f"{count} times in the analyzed runs."
                        ),
                        severity="high",
                    ),
                )

            patterns.append(
                ErrorPattern(
                    category=category,
                    occurrences=count,
                    latest_message=latest_messages.get(category),
                    evidence=evidence,
                )
            )

        return patterns

    def calculate_indicent_score(
        self, failure_analysis, duration_analysis, row_count_analysis, error_patterns
    ):
        score = 0

        evidence = []

        if failure_analysis.failure_streak >= 2:
            score += 2

            evidence.append(
                f"{failure_analysis.failure_streak}"
                "consecutive pipeline failure detected."
            )

        if (
            duration_analysis.duration_ratio is not None
            and duration_analysis.duration_ratio >= 2
        ):
            score += 2

            evidence.append(
                f"Latest run took "
                f"{duration_analysis.duration_ratio:.1f}x "
                "longer than the historical average."
            )

        if row_count_analysis.rows_read_anomaly:
            score += 2

        evidence.append(
            "Input volume is significantly lower " "than the historical average."
        )

        if row_count_analysis.rows_written_anomaly:
            score += 2

        evidence.append(
            "Output volume is significantly lower " "than the historical average."
        )

        for pattern in error_patterns:

            if pattern.occurrences >= 2:

                score += 3

                evidence.append(
                    f"Repeated error pattern detected: "
                    f"{pattern.category} "
                    f"({pattern.occurrences} occurrences)."
                )

        return score, evidence

    def determine_severity(self, score: int) -> str:

        if score >= 9:
            return "critical"
        if score >= 6:
            return "high"
        if score >= 3:
            return "medium"

        return "low"

    def generate_hypothesis(
        self, failure_analysis, duration_analysis, row_count_analysis, error_patterns
    ):

        hypothesis = []

        error_categories = {
            pattern.category for pattern in error_patterns if pattern.occurrences >= 2
        }

        if (
            "connection_timeout" in error_categories
            and failure_analysis.failure_streak >= 2
        ):
            hypothesis.append("Possible downstream connectivity issue.")

        if (
            "authentication_failure" in error_categories
            and failure_analysis.failure_streak >= 2
        ):
            hypothesis.append("Possible credential or authentication issue.")

        if (
            "schema_mismatch" in error_categories
            and failure_analysis.failure_streak >= 2
        ):
            hypothesis.append("Possible upstream or downstream schema change.")

        if (
            duration_analysis.duration_ratio is not None
            and duration_analysis.duration_ratio >= 2
            and row_count_analysis.rows_read_anomaly
        ):
            hypothesis.append(
                "Possible upstream data availability or " "source-system issue."
            )

        if (
            row_count_analysis.rows_read_anomaly
            and row_count_analysis.rows_written_anomaly
        ):
            hypothesis.append("Possible incomplete or degraded input dataset.")

        return hypothesis

    def determine_confidence(self, score: int) -> str:

        if score >= 7:
            return "high"

        if score >= 4:
            return "medium"

        return "low"

    def build_incident_assessment(
        self, failure_analysis, duration_analysis, row_count_analysis, error_patterns
    ):

        score, evidence = self.calculate_indicent_score(
            failure_analysis, duration_analysis, row_count_analysis, error_patterns
        )

        severity = self.determine_severity(score)

        confidence = self.determine_confidence(score)

        hypothesis = self.generate_hypothesis(
            failure_analysis, duration_analysis, row_count_analysis, error_patterns
        )

        return IncidentAssessment(
            severity=severity,
            score=score,
            confidence=confidence,
            hypothesis=hypothesis,
            evidence=evidence,
        )

    def generate_recommendation(
        self,
        hypothesis,
        error_pattterns,
    ):
        recommendations = []

        error_categories = {pattern.category for pattern in error_pattterns}

        if "connection_timeout" in error_categories:

            recommendations.append(
                Recommendation(
                    priority="high",
                    action="Check database availablity",
                    reason=("Repeated connection timeout" "errors were detected"),
                )
            )

            recommendations.append(
                Recommendation(
                    priority="high",
                    action="Check connection timeout configuration",
                    reason=(
                        "Pipeline execution is experiencing"
                        "connnection timeout failures"
                    ),
                )
            )

            recommendations.append(
                Recommendation(
                    priority="medium",
                    action="Check recent network or database errors.",
                    reason=(
                        "Connectivity-related failures may "
                        "indicate a downstream dependency issue."
                    ),
                )
            )

        if "authentication_failure" in error_categories:

            recommendations.append(
                recommendations.append(
                    Recommendation(
                        priority="high",
                        action="Verify database credentials.",
                        reason=("Authentication failures were detected."),
                    )
                )
            )

        if "schema_mismatch" in error_categories:

            recommendations.append(
                Recommendation(
                    priority="high",
                    action="Compare the current schema with the expected schema.",
                    reason=("Schema-related errors were detected."),
                )
            )

        if "permission_denied" in error_categories:

            recommendations.append(
                Recommendation(
                    priority="high",
                    action="Verify the pipeline's database permissions.",
                    reason=("Permission-related failures were detected."),
                )
            )

        return recommendations

    def investigate_pipeline(self, pipeline_name: str) -> IncidentReport:

        runs = self.pipeline_service.get_recent_runs(
            pipeline_name,
            limit=10,
        )

        if runs is None:
            return None

        failure_pattern = self.analyze_failure_pattern(runs)

        latest_run = runs[0]
        historical_runs = runs[1:]

        duration_anomaly = self.analyze_duration(latest_run, historical_runs)

        row_count_anomaly = self.analyze_row_counts(
            latest_run,
            historical_runs,
        )

        logs = self.pipeline_service.get_latest_run_logs(pipeline_name)

        error_patterns = self.log_analysis_service.analyze_error_patterns(logs)

        timeline = self.timeline_service.build_timeline(logs)

        dependencies = self.pipeline_service.get_pipeline_dependencies(pipeline_name)

        dependency_analysis = []

        if logs and dependencies:
            dependency_analysis = self.log_analysis_service.analyze_dependencies(
                logs, dependencies
            )

        root_cause_candidates = self.log_analysis_service.detect_root_cause_candidates(
            logs
        )

        assessment = self.build_incident_assessment(
            failure_pattern,
            duration_anomaly=duration_anomaly,
            row_count_anomaly=row_count_anomaly,
            error_patterns=error_patterns,
        )

        recommendation = self.generate_recommendation(
            assessment.hypotheses, error_patterns
        )

        evidence_chains=(
            self.explanation_service.build_evidence_chains(
                error_patterns=error_patterns,
                dependency_analysis=dependency_analysis,
                duration_anomaly=duration_anomaly,
                row_count_anomaly=row_count_anomaly
            )
        )

        failure_time=latest_run.completed_at
        if failure_time is None:
            failure_time=latest_run.started_at


        deployments=(
            self.deployment_service.get_recent_deployments(
                environment=self.pipeline_service.environment,
                failure_time=failure_time
            )
        )

        deployment_chains=(
            self.explanation_service.build_deployment_chains(
                deployments,
                failure_time
            )
        )

        evidence_chains.extend(
            deployment_chains
        )

        return IncidentReport(
            pipeline_name=pipeline_name,
            assessment=assessment,
            failure_pattern=failure_pattern,
            error_patterns=error_patterns,
            dependency_analysis=dependency_analysis,
            timeline=timeline,
            root_cause_candidates=root_cause_candidates,
            recommendations=recommendation,
            evidence=assessment.evidence,
            evidence_chains=evidence_chains,
        )
