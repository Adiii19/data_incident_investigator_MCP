from sqlalchemy import create_engine


DATABASE_URL = (
    "postgresql+psycopg://"
    "incident_user:"
    "incident_password@"
    "localhost:5432/"
    "incident_db"
    "?connect_timeout=5"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

