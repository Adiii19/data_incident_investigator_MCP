from datetime import datetime
from pydantic import BaseModel

class PipelineLog(BaseModel):
    id:int
    pipeline_run_id:int
    timestamp:datetime
    level:str
    message:str
    component:str|None

    
