from langchain.prompts import ChatPromptTemplate
from textwrap import dedent

template = ChatPromptTemplate.from_messages(
    messages=[
        ("system", "you are an expert in analyzing data, generate meaningful definitions, categorize, apply tags and determine sensitivity of data"),
        ("human", dedent("""you are provided with a table or dataaset. Your tasks are to ..
         1. Get sample data for this table. Use tools if required:
        {table_name}
         2. Analyze the sample data, and create metadata for the dataset and ALL of its columns. 
         The metadata should include - definition, data type, associated tags, sensitivity and your analysis.
         Format your output as per the instructions: 
         {format_instructions}
         """))
    ]
)
