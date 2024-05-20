"""Dictionary of models to map friendly names of LLMs to the specific versions"""

model_dict = {
    "GPT 3.5": "gpt-3.5-turbo-0125",
    "GPT 4": "gpt-4-turbo-preview",
    "GPT 4o": "gpt-4o-2024-05-13",
    # "Haiku": "haiku",
    # "Sonnet": "sonnet",
    # "Llama 3": "llama3",
    # "Mistral 7B": "mistral"
}


color_map = {
    "PII": "#FF5630",  # Red
    "PHI": "#00A9D4",  # Light Blue
    "Financial": "#FFC300",  # Yellow
    "Geospatial": "#36B37E",  # Green
    "Temporal": "#6554C0",  # Purple
    "Categorical": "#F63366",  # Pink
    "Behavioral": "#00B8A9",  # Teal
    "Demographic": "#FF8B00",  # Orange
    "Metadata": "#00B8D9",  # Blue
    "Other": "#ABB8C3"  # Gray
}