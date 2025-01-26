#!/usr/bin/env python3
"""
Model Finder - A tool to search for models on Hugging Face Hub based on configurable parameters.
"""

import os
import yaml
from typing import Dict, List, Any
from huggingface_hub import HfApi, login


def load_config(config_path: str = "model_search_config.yaml") -> Dict[str, Any]:
    """Load search configuration from YAML file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


def authenticate_hf():
    """Authenticate with HuggingFace using token from environment."""
    token = os.getenv('HF_TOKEN')
    if token:
        try:
            login(token)
            print("Successfully authenticated with HuggingFace")
        except Exception as e:
            print(f"Error authenticating: {str(e)}")
    else:
        print("Warning: HF_TOKEN not found in environment variables. Some features may be limited.")


def has_required_keywords(model_info: Dict, config: Dict[str, Any]) -> bool:
    """Check if model has all required keywords in its name or tags."""
    if 'filters' not in config or 'require_all' not in config['filters']:
        return True
        
    required_keywords = [kw.lower() for kw in config['filters']['require_all']]
    model_id = model_info['id'].lower()
    model_tags = [tag.lower() for tag in model_info['tags']]
    pipeline_tags = [tag.lower() for tag in model_info['pipeline_tags']]
    
    # Check each required keyword
    for keyword in required_keywords:
        # Look for keyword in model ID
        found_in_id = keyword in model_id
        
        # Look for keyword in tags
        found_in_tags = any(keyword in tag for tag in model_tags)
        
        # Look for keyword in pipeline tags
        found_in_pipeline = any(keyword in tag for tag in pipeline_tags)
        
        if not (found_in_id or found_in_tags or found_in_pipeline):
            return False
            
    return True


def check_model_size(model_id: str, min_size: float, max_size: float) -> tuple[bool, float]:
    """Check if model size falls within the specified range."""
    api = HfApi()
    try:
        model_info = api.model_info(model_id)
        size_gb = model_info.siblings_rpartition_size / (1024 * 1024 * 1024)  # Convert to GB
        return min_size <= size_gb <= max_size, size_gb
    except Exception as e:
        print(f"Error checking size for {model_id}: {str(e)}")
        return False, 0


def format_model_info(model: Dict) -> str:
    """Format model information for display."""
    info = []
    info.append(f"Model ID: {model['id']}")
    info.append(f"Downloads: {model['downloads']:,}")
    info.append(f"Likes: {model['likes']:,}")
    
    if model.get('tags'):
        info.append(f"Tags: {', '.join(model['tags'])}")
    
    if model.get('pipeline_tags'):
        info.append(f"Pipeline Tags: {', '.join(model['pipeline_tags'])}")
        
    if model.get('size_gb'):
        info.append(f"Size: {model['size_gb']:.2f} GB")
        
    return "\n".join(info)


def filter_results(models: List[Any], config: Dict[str, Any]) -> List[Dict]:
    """Filter models based on configuration criteria."""
    filtered_models = []
    
    # Get size constraints
    min_size = config.get('size', {}).get('min', 0)
    max_size = config.get('size', {}).get('max', float('inf'))
    
    # Get keyword filters
    keyword_filter = [kw.lower() for kw in config.get('keywordfilter', [])]
    
    for model in models:
        model_info = {
            'id': model.modelId,
            'downloads': model.downloads,
            'likes': model.likes,
            'tags': model.tags,
            'pipeline_tags': model.pipeline_tags
        }
        
        # Check required keywords
        if not has_required_keywords(model_info, config):
            continue
            
        # Check for filtered keywords
        model_id_lower = model_info['id'].lower()
        if any(kw in model_id_lower for kw in keyword_filter):
            continue
            
        # Check size constraints
        size_ok, size_gb = check_model_size(model_info['id'], min_size, max_size)
        if not size_ok:
            continue
            
        model_info['size_gb'] = size_gb
        filtered_models.append(model_info)
    
    # Sort by downloads
    filtered_models.sort(key=lambda x: x['downloads'], reverse=True)
    
    return filtered_models


def main():
    """Main function to run the model search."""
    try:
        # Load configuration
        config = load_config()
        print("Loaded configuration successfully")
        
        # Authenticate with HuggingFace
        authenticate_hf()
        
        # Initialize API
        api = HfApi()
        
        # Search for models
        print("\nSearching for models...")
        models = api.list_models(
            search=config.get('keywords', []),
            limit=100
        )
        
        # Filter results
        print("\nFiltering results...")
        filtered_models = filter_results(models, config)
        
        if not filtered_models:
            print("No models found matching the criteria")
            return
            
        # Display results
        print(f"\nFound {len(filtered_models)} matching models:\n")
        for i, model in enumerate(filtered_models, 1):
            print(f"\n--- Model {i} ---")
            print(format_model_info(model))
            
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
