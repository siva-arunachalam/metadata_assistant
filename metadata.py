from langchain.pydantic_v1 import BaseModel, Field
from typing import List

class ColumnMetadata(BaseModel):
    """Metadata containing descriptive information for a column"""
    name: str = Field(description="Name of the column or field")
    data_type: str = Field(description="Data type of the column such as int, double/float, string, date or datetime")
    description: str = Field(description="Generated description after analyzing data in this column in the context of the entire dataset")
    sensitivity: str = Field(description="'PII' if the column has values such as name, date of birth, phone number, address. 'PHI' if the column contains values related to medical or health records. Otherwise default to 'not sensitive'")


class DatasetMetadata(BaseModel):
    """Metadata containing descriptive information for the dataset and its columns"""
    name: str = Field(description="Name of the dataset. Default to the name of the table or dataset provided")
    description: str = Field(description="Generated description after analyzing the dataset as a whole across all columns and rows")
    columns: List[ColumnMetadata] = Field("List of column metadata. This list will have an item for each column in the dataset")
    