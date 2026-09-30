from sqlalchemy import text

from incident_investigator.database.connection import engine


def main():
    with engine.connect() as connection:
        result = connection.execute(
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


if __name__ == "__main__":
    main()