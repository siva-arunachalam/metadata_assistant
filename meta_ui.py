import streamlit as st
from typing import List
from database import get_table_names, get_sample_data, get_column_names
from llm import MetadataGenerator
from config import model_dict

def render_sidebar() -> str:
    """
    Renders the sidebar with table and model selection.

    Returns:
        tuple: A tuple containing the selected table and selected model.
    """
    table_names = get_table_names()
    selected_table = st.sidebar.selectbox(label="Select a table", options=table_names, key="selected_table")
    selected_model = st.sidebar.radio(
        "LLM model:",
        options=["GPT 3.5", "GPT 4", "GPT 4o"],
        horizontal=True,
        index=0,
        key="selected_model"
    )
    return selected_table, selected_model


def display_sample_data(selected_table: str) -> None:
    """
    Displays the sample data for the selected table.

    Args:
        selected_table (str): The name of the selected table.
    """
    st.subheader(f"Sample Data from {selected_table}")
    sample_data = get_sample_data(selected_table)
    st.dataframe(sample_data)


def handle_generate_metadata(selected_table: str, selected_model: str) -> None:
    """
    Handles the "Generate Metadata" button click event.

    Args:
        selected_table (str): The name of the selected table.
        selected_model (str): The name of the selected LLM model.
    """
    if "generated_metadata" not in st.session_state:
        st.session_state.generated_metadata = None

    if st.button("Generate Metadata"):
        metadata_generator = MetadataGenerator()
        columns = get_column_names(selected_table)
        model_name = model_dict[selected_model]
        response = metadata_generator.generate_metadata(table_name=selected_table, model_name=model_name)
        st.session_state.generated_metadata = response['metadata']


def display_generated_metadata() -> None:
    """
    Displays the generated metadata for the selected column.
    """
    if st.session_state.generated_metadata:
        md = st.session_state.generated_metadata
        st.subheader("Dataset Description")
        st.write(f"{md.description}")
        columns = [item.name for item in md.columns]

        selected_column = st.selectbox("Select a column", columns)

        if selected_column:
            meta = next((item for item in md.columns if item.name == selected_column), None)
            st.subheader(f"Metadata for {selected_column}")
            st.write(f"Definition: {meta.description}")
            st.write(f"Data Type: {meta.data_type}")
            st.write(f"Sensitivity: {meta.sensitivity}")
            st.write(f"Tags: {meta.tags or 'n/a'}")
            st.write(f"Analysis: {meta.analysis or 'n/a'}")


def main() -> None:
    """
    The main function that sets up the Streamlit app and orchestrates the flow.
    """
    st.set_page_config(page_title="Metadata Assistant", layout="wide")
    st.title("Table Metadata Generator")

    selected_table, selected_model = render_sidebar()
    display_sample_data(selected_table)
    handle_generate_metadata(selected_table, selected_model)
    display_generated_metadata()

if __name__ == "__main__":
    main()