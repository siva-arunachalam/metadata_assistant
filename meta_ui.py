import streamlit as st
from database import get_table_names, get_sample_data, get_column_names
from llm import MetadataGenerator
from config import model_dict



# Streamlit app
def main():
    st.set_page_config(page_title="Metadata Assistant", layout="wide")
    st.title("Table Metadata Generator")

    # Sidebar with table selection
    table_names = get_table_names()
    selected_table = st.sidebar.selectbox(label="Select a table", options=table_names, key="selected_table")
    selected_model = st.sidebar.radio(
        "LLM model:",
        options=["GPT 3.5", "GPT 4", "GPT 4o"],
        horizontal=True,
        index=0,
        key="selected_model"
    )

    # Main area with sample data and generate button
    st.subheader(f"Sample Data from {selected_table}")
    sample_data = get_sample_data(selected_table)
    st.dataframe(sample_data)

    if "generated_metadata" not in st.session_state:
        st.session_state.generated_metadata = None

    if st.button("Generate Metadata"):
        metadata_generator = MetadataGenerator()
        columns = get_column_names(selected_table)
        model_name = model_dict[selected_model]
        response = metadata_generator.generate_metadata(table_name=selected_table, model_name=model_name)
        st.session_state.generated_metadata = response['metadata']

    if st.session_state.generated_metadata:
        md = st.session_state.generated_metadata
        columns = [item.name for item in md.columns]

        # Show column listing in dropdown
        selected_column = st.selectbox("Select a column", columns)

        # Show metadata associated with the selected column
        if selected_column:
            meta = next((item for item in md.columns if item.name == selected_column), None)
            st.subheader(f"Metadata for {selected_column}")
            st.write(f"Definition: {meta.description}")
            st.write(f"Data Type: {meta.data_type}")
            st.write(f"Sensitivity: {meta.sensitivity}")

if __name__ == "__main__":
    main()