from datetime import datetime
from pydantic import BaseModel

class TimelineEvent(BaseModel):
    timestamp:datetime
    elapsed_seconds:float
    level:str
    message:str
    component:str|None