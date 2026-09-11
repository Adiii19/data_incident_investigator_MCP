from collections import Counter
from datetime import timedelta
from incident_investigator.models.dependency import PipelineDependency
from incident_investigator.models.dependency_analysis import DependencyEvidence
from incident_investigator.models.pipeline_log import PipelineLog
from incident_investigator.models.pipeline_log import PipelineLog

class LogAnalysisService:

    def classify_log(self,log:PipelineLog)->None:
        message=log.message.lower()

        if "timeout" in message:
            return "connection_timeout"

        if "authenctication" in message or "password" in message:
            return "authentication failure"

        if "schema" in message or "column" in message:
            return "schema_mismatch"

        if "permission" in message or "denied" in message:
            return "permission_denied"
        if "out of memory" in message or "memory" in message:
            return "out_of_memory"

        if "rate limit" in message or "too many requests" in message:
            return "api_rate_limit"

        if "duplicate" in message:
            return "duplicate_key"

        return None 

    def analyze_logs(self,logs:list[PipelineLog])->dict:

        counts=Counter()

        for log in logs:
            category=self.classify_log(log)

            if category is not None:
                counts[category]+=1

        return dict(counts)

    def find_errors_before_failure(
            self,
            logs:list[PipelineLog],
            window_seconds:int=120
    )->list[PipelineLog]:
         if not logs:
             return []

         failure_logs=[
             log
             for log in logs
             if log.level.upper()=="ERROR"
             and "failed" in log.message.lower()

         ]

         if not failure_logs:
             return []

         failure_time=failure_logs[-1].timestamp

         return [
             log
             for log in logs
             if(
                 log.timestamp<=failure_time
                 and failure_time-log.timestamp
                 <=timedelta(seconds=window_seconds)
                 and log.level.upper() in {"ERROR","WARNING"}
             )
         ]

    def detect_root_cause_candidates(
            self,
            logs:list[PipelineLog],
    )->list[dict]:

        relevant_logs=self.find_errors_before_failure(logs)

        if not relevant_logs:
            return []

        categories=Counter()

        latest_messages={}

        for log in relevant_logs:
            category=self.classify_log(log)

            if category is None:
                continue

            categories[category]+=1
            latest_messages[category]=log.message

        candidates=[]

        for category,occurrences in categories.items():

            confidence="low"

            if occurrences>=3:
                confidence="high"
            elif occurrences>=2:
                confidence="medium"

            candidates.append(
                {
                    "category":category,
                    "occurrences":occurrences,
                    "confidence":confidence,
                    "latest_message":latest_messages[category],
                    "evidence":(
                        f"{occurrences} {category.replace('_','')}"
                        "events occured shortly before the pipeline failed."
                    )
                }
            )

        return candidates

    def normalize_text(self,value:str)->str:
          return(
            value.lower()
            .replace("_", " ")
        .replace("-", " ")
        )

    def analyze_dependencies(
            self,
            logs:list[PipelineLog],
            dependencies:list[PipelineDependency]
    )->list[DependencyEvidence]:

        relevant_logs=self.find_errors_before_failure(
            logs
        )

        if not relevant_logs:
            return []


        results=[]

        for dependency in dependencies:
            matched_logs=[]

            for log in relevant_logs:
                message=self.normalize_text(log.message)

                dependency_name=self.normalize_text(
                    dependency.dependency_name
                )

                connection_identifier=(
                    self.normalize_text(
                        dependency.connection_identifier
                    )
                    if dependency.connection_identifier
                    else None
                )

                if dependency_name in message:
                    matched_logs.append(log)

                elif(
                    connection_identifier
                    and connection_identifier in message
                ):
                    matched_logs.append(log)

            if not matched_logs:
                continue

            if len(matched_logs)>=3:
                confidence="high"
            elif len(matched_logs)>=2:
                confidence="medium"
            else:
                confidence="low"

            evidence=[
                f"{len(matched_logs)} logs referenced"
                f"the dependency '{dependency.dependency_name}'."
            ]

            results.append(
                DependencyEvidence(
                    dependency_name=dependency.dependency_name,
                    dependency_type=dependency.dependency_type,
                    matched_logs=len(matched_logs),
                    confidence="low",
                    evidence=evidence
                )
            )

        return results



   