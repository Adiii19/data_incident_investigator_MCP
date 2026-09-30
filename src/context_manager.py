class ContextManager:

    def __init__(
            self,
            max_messages:int=12
    ):
        self.max_messages=max_messages

    def trim(
            self,
            messages:list[dict]
    )->list[dict]:

        if len(messages)<=self.max_messages:
            return messages

        system_messages=[
            message
            for message in messages
            if message.get("role")=="system"
        ]

        non_system_messages=[
            message
            for message in messages
            if message.get("role")!="system"
        ]

        recent_messages=non_system_messages[
            -(self.max_messages - len(system_messages)):
        ]

        return system_messages+recent_messages