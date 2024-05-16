import pandas as pd
from langchain.tools import tool
from database import get_sample_data as sample_data

@tool
def get_sample_data(table_name: str) -> str:
    """Get sample data for a given table"""
    return pd.DataFrame(sample_data(table_name)).head(3).to_csv(index=False, header=True)
