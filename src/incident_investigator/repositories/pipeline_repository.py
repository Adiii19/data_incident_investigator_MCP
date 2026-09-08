from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from incident_investigator.models.dependency import PipelineDependency
from incident_investigator.models.pipeline import Pipeline
from incident_investigator.models.pipeline_run import PipelineRun
from incident_investigator.models.pipeline_log import PipelineLog
from incident_investigator.models.deployment import Deployment


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

    def get_recent_runs(
        self, pipeline_id: int, start_time=None, end_time=None, limit: int = 10
    ):

        query = """
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
        params = {"pipeline_id": pipeline_id, "limit": limit}

        if start_time is not None:
            query += """
            AND started_at>=:start_time
"""
            params["start_time"] = start_time

        if end_time is not None:
            query += """
                AND started_at<:end_time
"""
            params["end_time"] = end_time

        query += """
                ORDER BY started_at DESC
                LIMIT :limit
        """

        statement = text(query)

        with self.engine.connect() as connection:
            result = connection.execute(statement, params)

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

    def get_pipeline_logs(self, pipeline_run_id: int, limit: int = 50):
        query = text("""

            SELECT
            id,
            pipeline_run_id,
            timestamp,
            level,
            message,
            component
            FROM pipeline_logs
            WHERE pipeline_run_id=:pipeline_run_id
            ORDER BY timestamp ASC
            LIMIT :limit

""")
        try:
            with self.engine.connect() as connection:
                result = connection.execute(
                    query, {"pipeline_run_id": pipeline_run_id, "limit": limit}
                )

                rows = result.fetchall()

                return [
                    PipelineLog(
                        id=row.id,
                        pipeline_run_id=row.pipeline_run_id,
                        timestamp=row.timestamp,
                        level=row.level,
                        message=row.message,
                        component=row.component,
                    )
                    for row in rows
                ]

        except SQLAlchemyError:
            return []

    def get_pipeline_dependencies(self,pipeline_id:int):

        query=text(
            """
            SELECT
                id,
                pipeline_id,
                dependency_name,
                dependency_type,
                connection_identifier
            FROM pipeline_dependencies
            WHERE pipeline_id=:pipeline_id
            ORDER BY dependency_name

"""
        )

        try:
            with self.engine.connect() as connection:
                result=connection.execute(
                    query,
                    {"pipeline_id":pipeline_id}
                )

                rows=result.fetchall()

                return [
                    PipelineDependency(
                          id=row.id,
                    pipeline_id=row.pipeline_id,
                    dependency_name=row.dependency_name,
                    dependency_type=row.dependency_type,
                    connection_identifier=row.connection_identifier,
                    )
                    for row in rows
                ]

        except SQLAlchemyError:
            return []

    def get_recent_deployments(
            self,environment:str,
            start_time,
            end_time,
            limit:int=20
    ):
        query=text(
            """
            SELECT 
            id,
            service_name,
            version
            deployed_at,
            environment,
            deployed_by,
            commit_sha
            FROM deployments
            WHERE environment =:environment
            AND deployed_at>=:start_time
            AND deployed_at<:end_time
            ORDER BY deployed_at DESC
            LIMIT :limit

"""
        )

        try:
            with self.engine.connect() as connection:

                result=connection.execute(
                    query,
                    {
                        "environment":environment,
                        "start_time":start_time,
                        "end_time":end_time,
                        "limit":limit
                    }
                )

                rows=result.fetchall()

                return [
                    Deployment(
                        id=row.id,
                        service_name=row.service_name,
                        version=row.version,
                        deployed_at=row.deployed_at,
                        environment=row.environment,
                        deployed_by=row.deployed_by,
                        commit_sha=row.commit_sha,
                    )
                    for row in rows
                ]

        except SQLAlchemyError:
            return []