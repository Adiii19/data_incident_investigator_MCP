class ToolSchemaAdapter:

    @staticmethod
    def to_groq(
        tools:list[dict],

    )->list[dict]:

        return [
            {
                "type":"function",
                "function":{
                    "name":tool["name"],
                    "description":(
                        tool["description"] or ""
                    ),
                    "parameters":(
                        tool["input_schema"]
                    ),
                    
                }
            }
            for tool in tools
        ]