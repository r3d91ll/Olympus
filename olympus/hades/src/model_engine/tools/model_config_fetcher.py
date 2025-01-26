#!/usr/bin/env python3
"""
Model Config Fetcher - Fetches the config.json for a specified model from HuggingFace Hub.
"""

import os
import yaml
import json
from pathlib import Path
from huggingface_hub import hf_hub_download, login


def load_config(config_path: str = "model_search_config.yaml") -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def authenticate_hf():
    """Authenticate with HuggingFace using token from environment."""
    token = os.getenv('HF_TOKEN')
    if not token:
        raise ValueError("HF_TOKEN environment variable not found")
        
    try:
        login(token)
        print("Successfully authenticated with HuggingFace")
    except Exception as e:
        raise Exception(f"Error authenticating: {str(e)}")


def fetch_model_config(model_id: str, output_dir: str = "model_configs") -> str:
    """
    Fetch config.json for the specified model.
    
    Args:
        model_id: The HuggingFace model ID (e.g., 'Qwen/Qwen2.5-Coder-14B-Instruct')
        output_dir: Directory to save the config file
        
    Returns:
        Path to the downloaded config file
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Download config.json
        config_path = hf_hub_download(
            repo_id=model_id,
            filename="config.json",
            local_dir=output_path,
            local_dir_use_symlinks=False
        )
        print(f"Successfully downloaded config.json to {config_path}")
        return config_path
        
    except Exception as e:
        raise Exception(f"Error downloading config.json: {str(e)}")


def display_model_info(config_json: dict):
    """Display relevant model configuration information."""
    important_fields = [
        'model_type',
        'architectures',
        'hidden_size',
        'intermediate_size',
        'num_attention_heads',
        'num_hidden_layers',
        'max_position_embeddings',
        'torch_dtype',
        'use_cache',
        'rope_scaling',
        'attention_bias',
        'attention_dropout'
    ]
    
    print("\nModel Configuration:")
    print("-" * 40)
    
    for field in important_fields:
        if field in config_json:
            value = config_json[field]
            if isinstance(value, dict):
                print(f"\n{field}:")
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"{field}: {value}")
    
    # Calculate approximate model size
    if 'hidden_size' in config_json and 'num_hidden_layers' in config_json:
        hidden_size = config_json['hidden_size']
        num_layers = config_json['num_hidden_layers']
        approx_size = (hidden_size * hidden_size * num_layers * 4) / (1024 * 1024 * 1024)  # in GB
        print(f"\nApproximate Model Size: {approx_size:.2f} GB")


def main():
    """Main function to run the config fetcher."""
    try:
        # Load configuration
        config = load_config()
        print("Loaded configuration successfully")
        
        # Get target model
        target_model = config.get('target_model')
        if not target_model:
            raise ValueError("No target_model specified in config")
            
        # Authenticate with HuggingFace
        authenticate_hf()
        
        # Fetch model config
        config_path = fetch_model_config(target_model)
        
        # Load and display config
        with open(config_path, 'r') as f:
            config_json = json.load(f)
            
        display_model_info(config_json)
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
