from collections import Counter

class ToolResultCompactor:

    def compact_logs(
            self,
            logs:list[dict],
            max_events:int=20
    )->dict:

        if not logs:
            return {
                "total_logs":0,
                "error_count":0,
                "warning_count":0,
                "important_events":[]
            }

        level_counts=Counter(
            log.get("level","").upper()
            for log in logs
            
        )

        important_events = [
            log
            for log in logs
            if log.get("level", "").upper()
            in {"ERROR", "WARNING"}
        ]

        important_events=important_events[
            -max_events:
        ]

        return {

            "total_logs":len(logs),
            "error_count":level_counts.get(
                "ERROR",0,
            ),
            "warning_count":level_counts.get(
                "WARNING",0
            ),
            "important_events":important_events

        }
