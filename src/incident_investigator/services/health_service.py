from sqlalchemy import text
from sqlalchemy.engine import Engine
import time


class HealthService:

    def __init__(self, engine: Engine):
        self.engine = engine

    def check_database_health(self):

        start = time.perf_counter()

        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))

                elapsed = time.perf_counter() - start

            return {
                "healthy": True,
                "response_time_ms": round(elapsed * 1000, 2),
                "message": "Database connection is healthy.",
            }

        except Exception as exc:

            elapsed = time.perf_counter() - start

            return {
                "healthy": False,
                "response_time_ms": round(elapsed * 1000, 2),
                "message": "Database connection failed.",
                "error": str(exc),
            }
