from datetime import datetime
from unittest.mock import MagicMock

from sqlalchemy.exc import OperationalError

from incident_investigator.models.pipeline import Pipeline
from incident_investigator.models.pipeline_run import PipelineRun
from incident_investigator.repositories.pipeline_repository import PipelineRepository
from incident_investigator.server import get_pipeline_status, get_recent_runs


def test_get_pipeline_by_name_returns_none_when_pipeline_is_missing():
    engine = MagicMock()
    connection = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    connection.execute.return_value.fetchone.return_value = None

    repo = PipelineRepository(engine)

    assert repo.get_pipeline_by_name("missing_pipeline") is None


def test_get_latest_run_returns_none_when_no_run_exists():
    engine = MagicMock()
    connection = MagicMock()
    engine.connect.return_value.__enter__.return_value = connection
    connection.execute.return_value.fetchone.return_value = None

    repo = PipelineRepository(engine)

    assert repo.get_latest_run(42) is None


def test_get_pipeline_by_name_returns_none_when_database_is_unavailable():
    engine = MagicMock()
    engine.connect.side_effect = OperationalError("stmt", {}, "database unavailable")

    repo = PipelineRepository(engine)

    assert repo.get_pipeline_by_name("demo") is None


def test_get_pipeline_status_serializes_model_instances():
    pipeline = Pipeline(
        id=1,
        name="customer_sync",
        description="sync customers",
        owner="data-team",
        schedule="0 * * * *",
        source="crm",
        destination="warehouse",
        created_at=datetime(2024, 1, 2, 3, 4, 5),
    )
    latest_run = PipelineRun(
        id=10,
        run_id="123e4567-e89b-12d3-a456-426614174000",
        started_at=datetime(2024, 1, 2, 3, 0, 0),
        completed_at=datetime(2024, 1, 2, 3, 10, 0),
        status="success",
        rows_read=150,
        rows_written=150,
        error_message=None,
    )

    import incident_investigator.server as server

    server.service.get_pipeline_status = MagicMock(return_value={"pipeline": pipeline, "latest_run": latest_run})

    response = get_pipeline_status("customer_sync")

    assert response["found"] is True
    assert response["pipeline"]["name"] == "customer_sync"
    assert response["latest_run"]["status"] == "success"


def test_get_recent_runs_returns_not_found_when_pipeline_is_missing():
    import incident_investigator.server as server

    server.service.get_recent_runs = MagicMock(return_value=None)

    response = get_recent_runs("missing_pipeline", limit=5)

    assert response == {"found": False, "pipeline_name": "missing_pipeline"}
