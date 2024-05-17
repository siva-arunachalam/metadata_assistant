import pandas as pd
from langchain.tools import tool
from typing import Optional
from database import get_sample_data as func_get_sample_data

@tool
def get_sample_data(table_name: str) -> Optional[str]:
    """
    Get sample data for a given table.

    Args:
        table_name (str): Name of the table.

    Returns:
        Optional[str]: Sample data in CSV format, or None if an error occurs.
    """
    df = pd.DataFrame(func_get_sample_data(table_name))
    return df.head(3).to_csv(index=False, header=True)
