import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from typing import List

def create_database_engine():
    """
    Creates a connection to the database using SQLAlchemy.

    Returns:
        Engine: SQLAlchemy engine object for database connection.
    """
    host = 'postgres'
    user = os.environ.get('POSTGRES_USER')
    password = os.environ.get('POSTGRES_PASSWORD')
    db = os.environ.get('POSTGRES_DB')
    port = 5432
    return create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")


# engine  - used in all functions.
engine = create_database_engine()


def load_data() -> None:
    """Loads data from CSV files into the database."""
    data_folder = "/app/data/datasets"

    for file in os.listdir(data_folder):
        if file.endswith(".csv"):
            table_name = os.path.splitext(file)[0].lower().replace('-', '_')
            print(f"processing {table_name} ...")

            file_path = os.path.join(data_folder, file)
            print(f"file_path: {file_path}")

            df = pd.read_csv(file_path)

            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()

            df.head(10000).to_sql(table_name, engine, index=False)

            print(f"Loaded data into table: {table_name}")
            print()


def get_table_names() -> List[str]:
    """
    Retrieves table names from the database.

    Returns:
        List[str]: List of table names.
    """
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_column_names(table_name: str) -> List[str]:
    """
    Retrieves column names from a table.

    Args:
        table_name (str): Name of the table.

    Returns:
        List[str]: List of column names.
    """
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [column['name'] for column in columns]


def get_sample_data(table_name: str) -> List[tuple]:
    """
    Retrieves sample data from a selected table.

    Args:
        table_name (str): Name of the table.

    Returns:
        List[tuple]: List of sample data rows.

    Raises:
        ValueError: If the table name is invalid or the sample data retrieval fails.
    """
    try:
        with engine.connect() as conn:
            sample_data = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3")).fetchall()
        return sample_data
    except Exception as e:
        raise ValueError(f"Failed to retrieve sample data for table '{table_name}': {str(e)}")
    