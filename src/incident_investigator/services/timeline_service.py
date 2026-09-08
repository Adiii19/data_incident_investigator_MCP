from datetime import timedelta

from incident_investigator.models.pipeline_log import PipelineLog
from incident_investigator.models.timeline import TimelineEvent


class TimelineService:

    def build_timeline(
        self,
        logs: list[PipelineLog],
    ) -> list[TimelineEvent]:

        sorted_logs = sorted(logs, key=lambda log: log.timestamp)
        if not sorted_logs:
            return []

        start_time = sorted_logs[0].timestamp

        return [
            TimelineEvent(
                timestamp=log.timestamp,
                elapsed_seconds=(log.timestamp - start_time).total_seconds(),
                level=log.level,
                message=log.message,
                component=log.component,
            )
            for log in sorted_logs
        ]

    def find_failure_event(
        self,
        timeline: list[TimelineEvent],
    ) -> TimelineEvent | None:

        for event in reversed(timeline):
            if event.level.upper() == "ERROR" and "failed" in event.message.lower():
                return event

        return None

    def get_pre_failure_events(
            self,
            timeline:list[TimelineEvent],
            window_seconds:int=120,
    )->list[TimelineEvent]:

        failure_event=self.find_failure_event(
            timeline
        )

        if failure_event is None:
            return []

        return[
            event
            for event in timeline

            if(event.timestamp<=failure_event.timestamp
                and failure_event.timestamp-event.timestamp
                <=timedelta(seconds=window_seconds)
               )
        ]