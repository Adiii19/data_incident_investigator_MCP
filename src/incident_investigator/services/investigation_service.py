from datetime import timedelta

from incident_investigator.models.investigation import (
    DurationAnomaly,
    FailurePattern,
    Evidence,
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

        evidence=[]

        if ratio>=2.0:
            evidence.append(
                Evidence(
                      category="duration_anomaly",
                      description=(
                          f"The latest run took"
                          f"{ratio:.1f}x longer that the "
                          f"historical average."
                      )  ,
                      severity="high"
                )
            )


        return DurationAnomaly(
            detected=ratio>=2.0,
            latest_duration_seconds=latest_seconds,
            historical_average_seconds=historical_average,
            duration_ratio=ratio,
            evidence=evidence
        )
