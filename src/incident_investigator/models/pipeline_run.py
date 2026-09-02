from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class PipelineRun(BaseModel):
    id:int
    run_id:UUID
    started_at:datetime
    completed_at:datetime|None
    status:str
    rows_read:int
    rows_written:int
    error_message:str|None