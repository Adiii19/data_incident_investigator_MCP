from pydantic import BaseModel, Field, field_validator
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
        default=50,
        ge=1,
        le=500,
        description="Maximum no of recent runs to return"
    )

    

class PipelineLogsRequest(BaseModel):
    pipeline_name: str = Field(
        min_length=1,
        description="Name of the data pipeline to inspect.",
    )

   

    limit:int=Field(
        default=50,
        ge=1,
        le=500,
        description="Maximum no of recent runs to return"
    )

    @field_validator("pipeline_name")
    @classmethod
    def validate_pipeline_name(cls,value:str)->str:
        value=value.strip()

        if not value:
            raise ValueError(
                "pipeline_name cannot be empty"
            )

        return value






   


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