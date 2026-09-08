from pydantic import BaseModel

class PipelineDependency(BaseModel):
    id:int
    pipeline_id:int
    dependency_name:str
    dependency_type:str
    connection_identifier:str|None
    