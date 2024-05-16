import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect

# Create a connection to the database using SQLAlchemy
# engine
host = 'postgres'
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
db = os.environ.get('POSTGRES_DB')
port = 5432
engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")


# load data
def load_data():
# Folder containing CSV files
    data_folder = "/app/data/datasets"

    # Iterate over CSV files in the folder
    for file in os.listdir(data_folder):
        if file.endswith(".csv"):
            table_name = os.path.splitext(file)[0].lower()
            print(f"processing {table_name} ..")
            
            file_path = os.path.join(data_folder, file)
            print(f"file_path: {file_path}")
            
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            
            # Drop the table if it exists
            with engine.connect() as conn:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                conn.commit()
            
            # Load the DataFrame into the database
            df.to_sql(table_name, engine, index=False)
            
            print(f"Loaded data into table: {table_name}")
            print()


# Function to retrieve table names from the database
def get_table_names():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    return table_names


# Function to retrieve column names from a table
def get_column_names(table_name):
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    column_names = [column['name'] for column in columns]
    return column_names


# Function to retrieve sample data from a selected table
def get_sample_data(table_name):
    with engine.connect() as conn:
        sample_data = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3")).fetchall()
    return sample_data


