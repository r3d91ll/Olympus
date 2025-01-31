# ModernBERT: The Next Generation of BERT Models

## Overview

ModernBERT represents a significant advancement in encoder-only models, offering a modern replacement for BERT while maintaining full backward compatibility. It introduces dramatic improvements through architectural innovations and achieves state-of-the-art performance across various tasks.

## Key Features

### Architecture

- **Rotary Positional Embeddings (RoPE)**
- **Alternating Attention Patterns**
- **Hardware-optimized Design**
- **8192 Sequence Length**
- **Flash Attention 2 Support** (recommended for optimal efficiency)

### Model Variants

1. **ModernBERT Base**
   - 149M parameters
   - Ideal for most applications

2. **ModernBERT Large**
   - 395M parameters
   - Higher performance for demanding tasks

### Performance Improvements

- 2-4x faster than previous encoder models
- State-of-the-art results in:
  - Classification tasks
  - Retrieval tasks
  - Code understanding
  - High-throughput production applications

### Training Data

- Trained on 2 trillion tokens of diverse data including:
  - Web documents
  - Code
  - Scientific articles
- Broader knowledge base compared to traditional BERT models

## Implementation

### Installation

```python
# Install from main branch (until v4.48.0 release)
pip install git+https://github.com/huggingface/transformers.git

# Optional: Install Flash Attention for maximum efficiency
pip install flash-attn
```

### Basic Usage

```python
from transformers import AutoTokenizer, AutoModelForMaskedLM

model_id = "answerdotai/ModernBERT-base"
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForMaskedLM.from_pretrained(model_id)

# Example masked language modeling
text = "The capital of France is [MASK]."
inputs = tokenizer(text, return_tensors="pt")
outputs = model(**inputs)

# Get predictions
masked_index = inputs["input_ids"][0].tolist().index(tokenizer.mask_token_id)
predicted_token_id = outputs.logits[0, masked_index].argmax(axis=-1)
predicted_token = tokenizer.decode(predicted_token_id)
```

### Fine-tuning Best Practices

- Use bfloat16 training for improved efficiency
- Leverage the `adamw_torch_fused` optimizer
- Recommended hyperparameters:

  ```python
  training_args = TrainingArguments(
      per_device_train_batch_size=32,
      per_device_eval_batch_size=16,
      learning_rate=5e-5,
      num_train_epochs=5,
      bf16=True,
      optim="adamw_torch_fused"
  )
  ```

## Advantages Over Traditional BERT

1. **Performance**
   - Consistent improvements across all metrics
   - No trade-offs in capabilities

2. **Efficiency**
   - Significantly faster processing
   - Better hardware utilization
   - Optimized for modern GPU architectures

3. **Versatility**
   - Drop-in replacement for BERT-like models
   - Maintains backward compatibility
   - Suitable for both research and production

## Use Cases

- LLM routing
- Classification tasks
- Information retrieval
- Code understanding
- High-throughput production applications
- Scientific text analysis

## Benchmarks

In comparative testing:

- ModernBERT achieves F1 scores of 0.993 vs BERT's 0.99
- Training time: 321 seconds (ModernBERT) vs 1048 seconds (BERT)
- 3% improvement on complex datasets like banking77 (F1 0.93 vs 0.90)
