"""Unified inference engine for all model types."""
from typing import Any, Dict, List, Optional, Union
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer, AutoTokenizer

class InferenceEngine:
    """Unified inference engine for running models."""
    
    def __init__(self):
        """Initialize the inference engine."""
        self.tokenizer_cache: Dict[str, PreTrainedTokenizer] = {}
        
    def run(self, 
            model: PreTrainedModel,
            input_data: Union[str, List[str], Dict[str, Any]],
            **kwargs) -> Any:
        """Run inference on a model.
        
        Args:
            model: The model to run inference on
            input_data: Input data for the model
            **kwargs: Additional inference parameters
            
        Returns:
            Model output
        """
        model_id = model.config._name_or_path
        
        # Get or load tokenizer
        tokenizer = self._get_tokenizer(model_id)
        
        # Prepare inputs based on type
        if isinstance(input_data, (str, list)):
            # Text input for language models
            inputs = tokenizer(
                input_data,
                return_tensors="pt",
                padding=True,
                truncation=True
            )
        else:
            # Assume properly formatted inputs for other model types
            inputs = input_data
            
        # Move to GPU if available
        if torch.cuda.is_available():
            model = model.cuda()
            if isinstance(inputs, dict):
                inputs = {k: v.cuda() if hasattr(v, 'cuda') else v 
                         for k, v in inputs.items()}
            
        # Run inference
        with torch.no_grad():
            outputs = model(**inputs, **kwargs)
            
        # Post-process outputs if needed
        if hasattr(outputs, 'logits'):
            # Language model output
            if 'CausalLM' in model.config.architectures[0]:
                return self._process_causal_lm_output(outputs, tokenizer)
            else:
                return self._process_general_lm_output(outputs, tokenizer)
        else:
            # Other model types
            return outputs
    
    def _get_tokenizer(self, model_id: str) -> PreTrainedTokenizer:
        """Get or load tokenizer for model.
        
        Args:
            model_id: HuggingFace model ID
            
        Returns:
            Tokenizer instance
        """
        if model_id not in self.tokenizer_cache:
            self.tokenizer_cache[model_id] = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code=True
            )
        return self.tokenizer_cache[model_id]
    
    def _process_causal_lm_output(self,
                                outputs: Any,
                                tokenizer: PreTrainedTokenizer) -> str:
        """Process output from causal language models.
        
        Args:
            outputs: Model outputs
            tokenizer: Tokenizer for decoding
            
        Returns:
            Decoded text output
        """
        next_token_logits = outputs.logits[:, -1, :]
        next_token = torch.argmax(next_token_logits, dim=-1)
        return tokenizer.decode(next_token[0])
    
    def _process_general_lm_output(self,
                                 outputs: Any,
                                 tokenizer: PreTrainedTokenizer) -> str:
        """Process output from general language models.
        
        Args:
            outputs: Model outputs
            tokenizer: Tokenizer for decoding
            
        Returns:
            Decoded text output
        """
        predictions = torch.argmax(outputs.logits, dim=-1)
        return tokenizer.decode(predictions[0])
