from incident_investigator.models.risk_assessment import(
    RiskAssessment,
    RiskFactor
)

class RiskAssessmentService:

    def calculate_risk_level(
            self,
            score:int
    )->str:

        if score>=75:
            return "critical"
        if score >= 50:
            return "high"

        if score >= 25:
            return "medium"

        return "low"

    def calculate_risk(
            self,
            failure_streak:int,
            duration_anomaly:bool,
            rows_read_anomaly:bool,
            rows_written_anomaly:bool,
            repeated_errors:int,
            dependency_issue:bool,
            deployment_correlation_score:int|None
    )->RiskAssessment:

        factors=[]
        score=0

        if failure_streak>=3:

            factors.append(
                RiskFactor(
                    name="failure_streak",
                    score=20,
                    reason=(
                        f"Pipeline has failed"
                        f"{failure_streak} consecutive times."
                    ),
                )
            )

            score+=20

        if duration_anomaly:

            factors.append(
                RiskFactor(
                    name="duration-_anomaly",
                    score=15,
                    reason=(
                        "latest pipeline run was significantly"
                        "slower than historical runs."
                    )
                )
            )

            score += 15

        if rows_read_anomaly:
            factors.append(
                RiskFactor(
                    name="input_volume_anomaly",
                    score=10,
                    reason=(
                        "lates run processed an abnormal"
                        "number of input rows."
                    )
                )
            )

            score += 10

        if rows_written_anomaly:

            factors.append(
                RiskFactor(
                    name="output_volume_anomaly",
                    score=10,
                    reason=(
                        "Latest run produced an abnormal "
                        "number of output rows."
                    ),
                )
            )

            score += 10

        if repeated_errors >= 2:

            factors.append(
                RiskFactor(
                    name="repeated_errors",
                    score=20,
                    reason=(
                        f"{repeated_errors} repeated error "
                        "events were detected."
                    ),
                )
            )

            score += 20

        if dependency_issue:

            factors.append(
                RiskFactor(
                    name="dependency_issue",
                    score=15,
                    reason=(
                        "A pipeline dependency was "
                        "associated with the incident."
                    ),
                )
            )

            score += 15

        if deployment_correlation_score is not None:

            deployment_points=self.deployment_risk_points(
                deployment_correlation_score
            )

            if deployment_points >0:

                factors.append(
                    RiskFactor(
                        name="deployment_correlation",
                        score=deployment_points,
                        reason=(
                             "A recent deployment showed "
                    f"a correlation score of "
                    f"{deployment_correlation_score} "
                    "with the incident."
                        )
                    )
                )

                score+=deployment_points

            

        score=min(score,100)

        risk_level=self.calculate_risk_level(score)

        return RiskAssessment(
            risk_level=risk_level,
            score=score,
            factors=factors
        )

    def deployment_risk_points(
            self,
            correlation_score:int,
    )->int:

        if correlation_score>=6:
            return 15
        if correlation_score>=4:
            return 10
        if correlation_score>=2:
            return 5

        return 0