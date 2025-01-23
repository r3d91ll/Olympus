import streamlit as st
from transformers import pipeline
import torch
from app.services.model_service import download_model, get_quantized_models

st.title("Project Olympus Chat Interface")

# Function to list quantized models from Hugging Face
def list_quantized_models():
    models = get_quantized_models()
    return [model['id'] for model in models]

# Route to download a specific model
@st.cache_data
class ModelDownloader:
    def __init__(self):
        self.models = {}

    def download(self, model_id):
        if model_id not in self.models:
            download_model(model_id, "models/")
            self.models[model_id] = True

model_downloader = ModelDownloader()

# Dropdown to select a model
selected_model = st.sidebar.selectbox("Select a quantized model", list_quantized_models())

if st.sidebar.button("Download Model"):
    model_downloader.download(selected_model)
    st.sidebar.write(f"Model {selected_model} downloaded successfully.")

# Load the selected model for inference
model = pipeline("text-generation", model=f"models/{selected_model}")

# Chat history
if "history" not in st.session_state:
    st.session_state.history = []

# Function to generate a response from the model
def generate_response(prompt):
    assistant_output = model(prompt, max_length=50, num_return_sequences=1)
    return assistant_output[0]['generated_text']

# User input form
with st.form(key='chat_form'):
    user_input = st.text_area("You:", value="", height=100)
    submit_button = st.form_submit_button(label="Send")

if submit_button and user_input:
    # Add user message to history
    st.session_state.history.append({"role": "user", "content": user_input})
    
    # Generate assistant response
    assistant_response = generate_response(user_input)
    
    # Add assistant message to history
    st.session_state.history.append({"role": "assistant", "content": assistant_response})
