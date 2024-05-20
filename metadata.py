from langchain.pydantic_v1 import BaseModel, Field
from typing import List


class ColumnMetadata(BaseModel):
    """Metadata containing descriptive information for a column"""
    name: str = Field(description="Name of the column or field")
    data_type: str = Field(description="Data type of the column such as int, double/float, string, date or datetime")
    description: str = Field(description="Generated description after analyzing data in this column in the context of the entire dataset. Description should be detailed.")
    tags: List[str] = Field(default=[], description="""List of tags applied to the column. A tag can be one of the following:
        PII: if it is Personally Identifiable Information.
        PHI: if it is health information, as defined by HIPAA regulations.
        Financial: If it is financial information, such as account numbers, transaction amounts, or credit card details.
        Geospatial: it it is location-related information, like addresses, coordinates, or postal codes.
        Temporal: If it is associated with time, such as timestamps, durations, or intervals.
        Categorical: if it belongs to specific categories or classifications.
        Demographic: If it is related to population characteristics, such as age, gender, income, or education level.
        Behavioral: if it is related to behaviors.
        Metadata: If it provides information about other data, such as data types, data sources, or data owners.
    """)
    sensitivity: str = Field(description="'PII' if the column has values such as name, date of birth, phone number, address. 'PHI' if the column contains values related to medical or health records. Otherwise default to 'not sensitive'")
    analysis: str = Field(description="Summary of your analysis for this column with your justification to how you arrived at the description, data type, sensitivity and tags")


class DatasetMetadata(BaseModel):
    """Metadata containing descriptive information for the dataset and its columns."""
    name: str = Field(description="Name of the dataset. Default to the name of the table or dataset provided")
    description: str = Field(description="Generated description after analyzing the dataset as a whole across all columns and rows")
    columns: List[ColumnMetadata] = Field("List of column metadata. This list will have an item for each column in the dataset")
