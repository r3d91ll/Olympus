import requests

def get_quantized_models():
    url = "https://huggingface.co/api/models"
    params = {
        "filter": "quantization",
        "sort": "downloads",
        "direction": "-1"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch models: {response.status_code} - {response.text}")

def download_model(model_id, destination_folder):
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import os

    model = AutoModelForCausalLM.from_pretrained(model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_id)

    model_path = os.path.join(destination_folder, model_id)
    if not os.path.exists(model_path):
        os.makedirs(model_path)

    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)
