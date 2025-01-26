"""Model inference implementation."""
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer

class InferenceEngine:
    """Engine for running model inference."""
    
    def run(self, model: PreTrainedModel, input_data: str) -> str:
        """Run inference on input data.
        
        Args:
            model: Model to use for inference
            input_data: Input data to run inference on
            
        Returns:
            Model output
        """
        # Get tokenizer
        tokenizer = model.tokenizer
        
        # Set pad token if not set
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            tokenizer.pad_token_id = tokenizer.eos_token_id
        
        # Tokenize input
        inputs = tokenizer(
            input_data,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=model.config.max_position_embeddings
        )
        
        # Generate output
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_length=model.config.max_position_embeddings,
                pad_token_id=tokenizer.pad_token_id,
                eos_token_id=tokenizer.eos_token_id,
                do_sample=True,
                top_p=0.95,
                top_k=50,
                temperature=0.8,
                num_return_sequences=1
            )
        
        # Decode output
        return tokenizer.decode(outputs[0], skip_special_tokens=True)