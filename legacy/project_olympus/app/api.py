from fastapi import FastAPI
from transformers import pipeline

app = FastAPI()

# Load the selected model for inference
model = pipeline("text-generation", model="models/gpt2")

@app.post("/generate/")
async def generate(prompt: str):
    assistant_output = model(prompt, max_length=50, num_return_sequences=1)
    return {"response": assistant_output[0]['generated_text']}
