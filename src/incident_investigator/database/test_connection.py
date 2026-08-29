from sqlalchemy import text

from incident_investigator.database.connection import engine

with engine.connect() as connection:
    result=connection.execute(
        text("""
                SELECT 
                    id,
                    owner,
                    schedule
                FROM pipelines
                ORDER BY id

""")
    )


    print(result)

    for row in result:
     print(row)