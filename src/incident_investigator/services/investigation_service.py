from datetime import timedelta

from incident_investigator.models.error_pattern import ErrorPattern
from incident_investigator.models.investigation import (
    DurationAnomaly,
    FailurePattern,
    Evidence,
    RowCountAnomaly,
)


class InvestigationService:

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

        if average_rows_written is not None and average_rows_written>0:
            rows_written_ratio=latest_rows_written/average_rows_written

        rows_written_anomaly = (
            rows_written_ratio is not None and rows_written_ratio < 0.5
        )

        evidence=[]

        if rows_read_anomaly:
            evidence.append(
                Evidence(
                    category="input_volume_anomaly",
                    description=(
                        f"The latest run processed only"
                        f"{rows_read_ratio:.1%} of the "
                        f"historical average input volume"
                    ),
                    severity="high"
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
            rows_ready_anomaly=rows_read_anomaly,
            rows_written_anomaly=rows_written_anomaly,

            latest_rows_read=latest_rows_read,
            historical_average_rows_read=average_rows_read,

            latest_rows_written=latest_rows_written,
            historical_average_rows_written=average_rows_written,

            rows_read_ratio=rows_read_ratio,
            rows_written_ratio=rows_written_ratio,

            evidence=evidence
        )

    def classify_error(self,error_message:str|None)->str|None:

        if not error_message:
            return None

        message=error_message.lower()

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

    def analyze_error_patterns(self,runs):

        error_counts={}
        latest_messages={}

        for run in runs:
            category=self.classify_error(run.error_message)

            if category is None:
                continue

            error_counts[category]=(
                error_counts.get(category,0)+1
            )

            if category not in latest_messages:
                latest_messages[category]=run.error_message

        patterns=[]

        for category,count in error_counts.items():

            evidence=[]

            if count>=2:
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
                    evidence=evidence
                )
            )

        return patterns