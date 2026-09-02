from incident_investigator.database.connection import engine
from incident_investigator.repositories.pipeline_repository import (
    PipelineRepository,
)

repository=PipelineRepository(engine)

pipeline=repository.get_pipeline_by_name(
    "customer_sync"
)

print(pipeline)
