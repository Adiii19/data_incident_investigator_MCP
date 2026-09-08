from datetime import datetime
from pydantic import BaseModel

class Deployment(BaseModel):
    id:int
    service_name:str
    version:str
    deployed_at:datetime
    environment:str
    deployed_by:str|None
    