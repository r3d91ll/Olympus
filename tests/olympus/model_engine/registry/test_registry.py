import pytest
from olympus.model_engine.registry import ModelRegistry
from huggingface_hub import HfApi

def test_model_registry_init():
    registry = ModelRegistry()
    assert isinstance(registry.config_dir, Path)
    assert isinstance(registry.hf_api, HfApi)

def test_get_model_config(mocker):
    mock_hf_api = mocker.patch('huggingface_hub.HfApi')
    mock_hf_api.download_file.return_value = "path/to/config.json"
    
    registry = ModelRegistry()
    config = registry._get_model_config("Salesforce/codegen-350M-mono")
    
    assert isinstance(config, dict)

def test_load_model(mocker):
    mock_hf_api = mocker.patch('huggingface_hub.HfApi')
    mock_hf_api.download_file.return_value = "path/to/config.json"
    mock_model_class = mocker.patch('transformers.AutoModelForCausalLM.from_pretrained')
    
    registry = ModelRegistry()
    model = registry._load_model("Salesforce/codegen-350M-mono", {"model_type": "causal"}, None)
    
    assert isinstance(model, PreTrainedModel)

def test_search_models(mocker):
    mock_hf_api = mocker.patch('huggingface_hub.HfApi')
    mock_hf_api.list_models.return_value = [
        {'id': 'model1', 'siblings_rpartition_size': 1024 * 1024 * 1024},
        {'id': 'model2', 'siblings_rpartition_size': 2048 * 1024 * 1024}
    ]
    
    registry = ModelRegistry()
    models = registry.search_models(min_size=1, max_size=3)
    
    assert len(models) == 2