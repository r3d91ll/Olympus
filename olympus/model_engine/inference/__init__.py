"""Model inference implementation."""
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer

class InferenceEngine:
    """Engine for running model inference."""
    
    def run(self, model: PreTrainedModel, input_data: str, tokenizer: PreTrainedTokenizer = None) -> str:
        """Run inference on input data.
        
        Args:
            model: Model to use for inference
            input_data: Input data to run inference on
            tokenizer: Optional tokenizer to use. If not provided, will try to get from model.
            
        Returns:
            Model output
            
        Raises:
            ValueError: If no tokenizer is available
        """
        # Get tokenizer
        if tokenizer is None:
            if hasattr(model, 'tokenizer'):
                tokenizer = model.tokenizer
            else:
                raise ValueError("No tokenizer provided and model has no tokenizer attribute")
        
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
                top_k=5,  # Reduced from 50 to make output more focused
                temperature=0.2,  # Reduced from 0.8 to make output more deterministic
                num_return_sequences=1,
                min_length=20,  # Add minimum length to avoid short responses
                no_repeat_ngram_size=2,  # Prevent repetition
                early_stopping=True  # Stop when EOS token is generated
            )
        
        # Decode output
        return tokenizer.decode(outputs[0], skip_special_tokens=True)