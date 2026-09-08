from pydantic import BaseModel

class Recommendation(BaseModel):
    priority:str
    action:str
    reason:str

    