class CapabilityRegistry:

    def __init__(self,client):
        self.client=client

        self.tools=[]
        self.resources=[]
        self.resource_templates=[]

    

    async def discover(self):

        tool_result=await self.client.list_tools()

        self.tools=[

            {
                "name":tool.name,
                "description":tool.description,
                "input_schema":tool.input_schema,
            }

            for tool in tool_result.tools

        ]

        resource_result = await self.client.list_resources()

        self.resources=[
            {
                "uri":str(resource.uri),
                "name":resource.name,
                "description":resource.description
            }
            for resource in resource_result.resources
        ]

        template_result = await self.client.list_resource_templates()

        self.resource_templates=[
            {
                "uri_template":template.uri_template,
                "description":template.description,
                "mime_type":template.mime_type,
            }
            for template in template_result.resource_templates
        ]

    def get_tools(self):
        return self.tools

    def get_resources(self):
        return self.resources

    def get_resource_templates(self):
        return self.resource_templates