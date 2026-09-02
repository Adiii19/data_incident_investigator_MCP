from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from incident_investigator.models.pipeline import Pipeline
from incident_investigator.models.pipeline_run import PipelineRun


class PipelineRepository:

    def __init__(self, engine: Engine):
        self.engine = engine

    def get_pipeline_by_name(self, pipeline_name: str):
        query = text("""
                SELECT
                    id,
                    name,
                    description,
                    owner,
                    schedule,
                    source,
                    destination,
                    created_at
                FROM pipelines
                WHERE name = :pipeline_name
        """)

        try:
            with self.engine.connect() as connection:
                result = connection.execute(query, {"pipeline_name": pipeline_name})
                row = result.fetchone()

                if row is None:
                    return None

                return Pipeline(
                    id=row.id,
                    name=row.name,
                    description=row.description,
                    owner=row.owner,
                    schedule=row.schedule,
                    source=row.source,
                    destination=row.destination,
                    created_at=row.created_at,
                )
        except SQLAlchemyError:
            return None

    def get_latest_run(self, pipeline_id: int):
        query = text("""
            SELECT
                id,
                run_id,
                started_at,
                completed_at,
                status,
                rows_read,
                rows_written,
                error_message
            FROM pipeline_runs
            WHERE pipeline_id = :pipeline_id
            ORDER BY started_at DESC
            LIMIT 1
        """)

        try:
            with self.engine.connect() as connection:
                result = connection.execute(query, {"pipeline_id": pipeline_id})
                row = result.fetchone()

                if row is None:
                    return None

                return PipelineRun(
                    id=row.id,
                    run_id=row.run_id,
                    started_at=row.started_at,
                    completed_at=row.completed_at,
                    status=row.status,
                    rows_read=row.rows_read,
                    rows_written=row.rows_written,
                    error_message=row.error_message,
                )
        except SQLAlchemyError:
            return None

    def get_recent_runs(self,pipeline_id:int,start_time=None,end_time=None,limit:int=10):

       query="""
        SELECT
            id,
            run_id,
            started_at,
            completed_at,
            status,
            rows_read,
            rows_written,
            error_message
        FROM pipeline_runs
        WHERE pipeline_id = :pipeline_id
        
    """
       params={
           "pipeline_id":pipeline_id,
           "limit":limit
       }

       if start_time is not None:
           query+="""
            AND started_at>=:start_time
"""
           params["start_time"]=start_time

       if end_time is not None:
           query+="""
                AND started_at<:end_time
"""
           params["end_time"]=end_time

       query+="""
                ORDER BY started_at DESC
                LIMIT :limit
        """

       statement=text(query)

       with self.engine.connect() as connection:
            result = connection.execute(
                statement,
                params
            )

            rows = result.fetchall()

            return [
                PipelineRun(
                    id=row.id,
                    run_id=row.run_id,
                    started_at=row.started_at,
                    completed_at=row.completed_at,
                    status=row.status,
                    rows_read=row.rows_read,
                    rows_written=row.rows_written,
                    error_message=row.error_message,
                )
                for row in rows
            ]


    