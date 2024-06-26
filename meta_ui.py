import streamlit as st
from typing import List
from database import get_table_names, get_sample_data, get_column_names
from llm import MetadataGenerator
from config import model_dict, color_map


def load_css(css_file_name):
    with open(css_file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


def render_sidebar() -> str:
    """
    Renders the sidebar with table and model selection.

    Returns:
        tuple: A tuple containing the selected table and selected model.
    """
    table_names = get_table_names()
    with st.sidebar:
        st.markdown("<div class='sidebar-content'>", unsafe_allow_html=True)
        st.header("Options")
        selected_table = st.selectbox("Select a table", table_names)
        selected_model = st.radio("LLM model:", ["GPT 3.5", "GPT 4", "GPT 4o"], index=1)
        st.markdown("</div>", unsafe_allow_html=True)

    return selected_table, selected_model


def display_sample_data(selected_table: str) -> None:
    """
    Displays the sample data for the selected table.

    Args:
        selected_table (str): The name of the selected table.
    """
    sample_data = get_sample_data(selected_table)
    st.subheader(f"Sample Data from {selected_table}")
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

    st.markdown("<div class='generate-metadata-section'>", unsafe_allow_html=True)
    if st.button("Generate Metadata", key='generate_metadata_btn'):
        metadata_generator = MetadataGenerator()
        columns = get_column_names(selected_table)
        model_name = model_dict[selected_model]
        response = metadata_generator.generate_metadata(table_name=selected_table, model_name=model_name)
        st.session_state.generated_metadata = response['metadata']
    st.markdown("</div>", unsafe_allow_html=True)


def display_generated_metadata() -> None:
    """
    Displays the generated metadata for the selected column.
    """
    if st.session_state.generated_metadata:
        md = st.session_state.generated_metadata

        st.markdown("<div class='metadata-section'>", unsafe_allow_html=True)
        st.subheader("Dataset Description")
        st.write(md.description)

        columns = [item.name for item in md.columns]
        selected_column = st.selectbox("Select a column", columns)

        if selected_column:
            meta = next((item for item in md.columns if item.name == selected_column), None)
            
            st.subheader(f"Metadata for {selected_column}")
            st.markdown("<div class='metadata-content'>", unsafe_allow_html=True)
            st.write(f"<b>Definition:</b> {meta.description}", unsafe_allow_html=True)
            st.write(f"<b>Data Type:</b> {meta.data_type}", unsafe_allow_html=True)
            st.write(f"<b>Sensitivity:</b> {meta.sensitivity}", unsafe_allow_html=True)
            if meta.tags:
                tags_html = " ".join([f'<span class="tag" style="background-color: {color_map.get(tag, "#ABB8C3")};">{tag}</span>' for tag in meta.tags])
                st.write(f"<b>Tags:</b> {tags_html}", unsafe_allow_html=True)
            else:
                st.write("<b>Tags:</b> n/a", unsafe_allow_html=True)
            st.write(f"<b>Analysis:</b> {meta.analysis or 'n/a'}", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
            

def main() -> None:
    """
    The main function that sets up the Streamlit app and orchestrates the flow.
    """
    st.set_page_config(page_title="Metadata Assistant", layout="wide")

    load_css("styles.css")
    st.markdown("<div class='header'>Table Metadata Generator</div>", unsafe_allow_html=True)

    selected_table, selected_model = render_sidebar()
    display_sample_data(selected_table)
    handle_generate_metadata(selected_table, selected_model)
    display_generated_metadata()
    st.markdown("<div class='footer'>© 2024 Table Metadata Generator. All rights reserved.</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()