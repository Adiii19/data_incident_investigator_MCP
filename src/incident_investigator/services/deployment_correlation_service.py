from incident_investigator.models.deployment_correlation import DeploymentCorrelation


class DeploymentCorrelationService:

    def calculate_confidence(self,score:int)->str:

        if score>=6:
            return "high"
        if score >=3:
            return "medium"

        return "low"

    def calculate_score(self,minutes_before_failure:float,is_dependency:bool,
                        referenced_in_logs:bool)->tuple[int,list[str]]:
        score=0
        reasons=[]

        if minutes_before_failure<=30:
            score+=2
            reasons.append(
                "Deployment occurred within 30 minutes of failure."
            )

        elif minutes_before_failure<=120:
            score+=1
            reasons.append(
                "Deployment occurred within 2 hours of failure."
            )

        if is_dependency:
            score+=2
            reasons.append(
                "Deployed service is a declared pipeline dependency."
            )
        if referenced_in_logs:
            score+=3
            reasons.append(
                "Deployment service was referenced in pipeline logs."
            )

        return score,reasons

    def is_pipeline_dependency(
            self,
            deployment,
            dependencies
    )->bool:

        deployment_service=deployment.service_name.lower()

        for dependency in dependencies:

            if(dependency.dependency_name.lower()==deployment_service):
                return True

        return False

    def referenced_in_logs(
            self,
            deployment,
            logs
    )->bool:

        service_name=deployment.service_name.lower()

        for log in logs:
            if service_name in log.message.lower():
                return True

        return False

    def correlate_deployments(
        self,
        deployments,
        failure_time,
        dependencies,
        logs,
    ) -> list[DeploymentCorrelation]:

        results = []

        for deployment in deployments:

            minutes_before_failure = (
                failure_time - deployment.deployed_at
            ).total_seconds() / 60

            is_dependency = (
                self.is_pipeline_dependency(
                    deployment,
                    dependencies,
                )
            )

            referenced = (
                self.referenced_in_logs(
                    deployment,
                    logs,
                )
            )

            score, reasons = (
                self.calculate_score(
                    minutes_before_failure,
                    is_dependency,
                    referenced,
                )
            )

            confidence = (
                self.calculate_confidence(score)
            )

            results.append(
                DeploymentCorrelation(
                    service_name=deployment.service_name,
                    version=deployment.version,
                    deployed_at=(
                        deployment.deployed_at.isoformat()
                    ),
                    minutes_before_failure=round(
                        minutes_before_failure,
                        2,
                    ),
                    score=score,
                    confidence=confidence,
                    reasons=reasons,
                )
            )

        return results