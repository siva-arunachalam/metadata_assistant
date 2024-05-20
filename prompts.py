from langchain.prompts import ChatPromptTemplate
from textwrap import dedent

template = ChatPromptTemplate.from_messages(
    messages=[
        ("system", "you are an expert in analyzing data, generate meaningful definitions, categorize, apply tags and determine sensitivity of data. You always pay attention to the output format."),
        ("human", dedent("""Get sample data from this table: {table_name}. Analyze the sample data for the columns: {next_column_batch} and generate output strictly following these instructions: {format_instructions}
         This is very IMPORTANT: Your output should NOT contain anything other than json formatted to the provided instructions.
         """))
    ]
)