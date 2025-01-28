import pytest
from olympus.model_engine.inference.engine import InferenceEngine
from transformers import PreTrainedModel, AutoTokenizer

def test_inference_engine_init():
    engine = InferenceEngine()
    assert isinstance(engine.tokenizer_cache, dict)

def test_run(mocker):
    mock_model = mocker.Mock(spec=PreTrainedModel)
    mock_tokenizer = mocker.patch('transformers.AutoTokenizer.from_pretrained')
    mock_tokenizer.return_value = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
    
    engine = InferenceEngine()
    inputs = "def fibonacci(n):"
    outputs = engine.run(mock_model, inputs)
    
    assert isinstance(outputs, str)

def test_get_tokenizer(mocker):
    mock_tokenizer = mocker.patch('transformers.AutoTokenizer.from_pretrained')
    mock_tokenizer.return_value = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
    
    engine = InferenceEngine()
    tokenizer = engine._get_tokenizer("Salesforce/codegen-350M-mono")
    
    assert isinstance(tokenizer, AutoTokenizer)