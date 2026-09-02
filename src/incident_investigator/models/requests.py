from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# class Environment(str,Enum):
#     DEVELOPMENT="development"
#     STAGING="staging"
#     PRODUCTION="production"


class PipelineStatusRequest(BaseModel):
    pipeline_name: str = Field(
        min_length=1,
        description="Name of the data pipeline to inspect.",
    )

   

    limit:int=Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum no of recent runs to return"
    )

    # environment:Environment=Field(
    #     description="Deployment environment of the pipeline"
    # )


class PipelineRunsRequest(BaseModel):
    pipeline_name:str=Field(
        min_length=1,
        description="Name  of the pipeline"
    )

    start_time:datetime|None=Field(
            default=None,
            description="Only include runs starting at or after this timestamp."
        )
    
    end_time:datetime|None=Field(
            default=None,
            description="Only include runs starting before or at this timestamp"
        )

    limit:int=Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of runs to return"
    )