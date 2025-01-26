"""RAG chain implementation."""
from typing import Dict, List, Optional, Union
from loguru import logger

from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    BitsAndBytesConfig
)

from .retriever import Retriever

# Available models with their configurations
MODEL_CONFIGS = {
    "deepseek-r1-distill": {
        "name": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "max_length": 2048,
        "temperature": 0.7,
        "top_p": 0.95,
        "repetition_penalty": 1.15,
        "quantization": "4bit"  # More efficient than 8bit
    },
    "llama2-7b": {
        "name": "meta-llama/Llama-2-7b-chat-hf",
        "max_length": 2000,
        "temperature": 0.7,
        "top_p": 0.95,
        "repetition_penalty": 1.15,
        "quantization": "8bit"
    }
}

# System prompt template
SYSTEM_PROMPT = """You are a helpful AI assistant. Use the following context to answer the user's question.
If you don't know the answer or can't find it in the context, say so.

Context:
{context}

Question: {question}

Answer: Let me help you with that."""

# Default prompt template
DEFAULT_PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template=SYSTEM_PROMPT
)

class RAGChain:
    """RAG chain for question answering."""
    
    def __init__(
        self,
        retriever: Retriever,
        model_key: str = "deepseek-r1-distill",
        device: str = "cuda",
        prompt_template: Optional[PromptTemplate] = None
    ):
        """Initialize RAG chain.
        
        Args:
            retriever: Retriever instance
            model_key: Key for model configuration in MODEL_CONFIGS
            device: Device to run model on
            prompt_template: Custom prompt template
        """
        self.retriever = retriever
        self.prompt = prompt_template or DEFAULT_PROMPT
        
        # Get model configuration
        if model_key not in MODEL_CONFIGS:
            raise ValueError(f"Unknown model key: {model_key}")
        
        config = MODEL_CONFIGS[model_key]
        self.max_length = config["max_length"]
        
        # Initialize model and tokenizer
        try:
            # Configure quantization
            if config["quantization"] == "4bit":
                quantization_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_compute_dtype="float16",
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_use_double_quant=True
                )
            else:  # 8bit
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True
                )
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                config["name"],
                cache_dir=".cache/huggingface"
            )
            
            self.model = AutoModelForCausalLM.from_pretrained(
                config["name"],
                cache_dir=".cache/huggingface",
                device_map=device,
                quantization_config=quantization_config,
                trust_remote_code=True  # Required for some models
            )
            
            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_length=config["max_length"],
                temperature=config["temperature"],
                top_p=config["top_p"],
                repetition_penalty=config["repetition_penalty"]
            )
            
            # Create LLM chain
            self.llm = HuggingFacePipeline(pipeline=pipe)
            self.chain = LLMChain(
                llm=self.llm,
                prompt=self.prompt
            )
            
            logger.info(f"Initialized RAG chain with model: {config['name']}")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG chain: {str(e)}")
            raise
            
    def _format_sources(self, sources: List[str]) -> str:
        """Format sources for response."""
        if not sources:
            return "No sources found."
            
        return "Sources:\n" + "\n".join(f"- {s}" for s in sources)
        
    async def _get_context(
        self,
        query: str,
        metadata_filter: Optional[Dict] = None
    ) -> Dict:
        """Get relevant context for query."""
        try:
            return await self.retriever.get_relevant_context(
                query=query,
                metadata_filter=metadata_filter,
                max_length=self.max_length
            )
        except Exception as e:
            logger.error(f"Failed to get context: {str(e)}")
            return {
                "context": "",
                "sources": [],
                "relevance_scores": []
            }
            
    async def generate_response(
        self,
        query: str,
        metadata_filter: Optional[Dict] = None,
        return_sources: bool = True
    ) -> Union[str, Dict]:
        """Generate response using RAG."""
        try:
            # Get relevant context
            context_data = await self._get_context(
                query,
                metadata_filter
            )
            
            if not context_data["context"]:
                response = (
                    "I apologize, but I couldn't find any relevant "
                    "information to answer your question."
                )
                
                if return_sources:
                    return {
                        "response": response,
                        "sources": [],
                        "relevance_scores": []
                    }
                return response
                
            # Generate response
            chain_response = await self.chain.arun(
                context=context_data["context"],
                question=query
            )
            
            if return_sources:
                return {
                    "response": chain_response,
                    "sources": context_data["sources"],
                    "relevance_scores": context_data["relevance_scores"]
                }
                
            return chain_response
            
        except Exception as e:
            logger.error(f"Failed to generate response: {str(e)}")
            error_msg = (
                "I apologize, but I encountered an error while "
                "processing your question. Please try again."
            )
            
            if return_sources:
                return {
                    "response": error_msg,
                    "sources": [],
                    "relevance_scores": []
                }
            return error_msg
            
    async def generate_response_with_history(
        self,
        query: str,
        chat_history: List[Dict],
        metadata_filter: Optional[Dict] = None,
        return_sources: bool = True
    ) -> Union[str, Dict]:
        """Generate response using RAG with chat history."""
        try:
            # Format chat history
            history_text = "\n".join([
                f"User: {msg['user']}\nAssistant: {msg['assistant']}"
                for msg in chat_history[-3:]  # Use last 3 messages
            ])
            
            # Add history to prompt
            history_prompt = PromptTemplate(
                input_variables=["context", "question", "history"],
                template=(
                    "Previous conversation:\n{history}\n\n"
                    "Context:\n{context}\n\n"
                    "Question: {question}\n\n"
                    "Answer: Let me help you with that."
                )
            )
            
            # Create new chain with history
            history_chain = LLMChain(
                llm=self.llm,
                prompt=history_prompt
            )
            
            # Get context
            context_data = await self._get_context(
                query,
                metadata_filter
            )
            
            if not context_data["context"]:
                response = (
                    "I apologize, but I couldn't find any relevant "
                    "information to answer your question."
                )
                
                if return_sources:
                    return {
                        "response": response,
                        "sources": [],
                        "relevance_scores": []
                    }
                return response
                
            # Generate response with history
            chain_response = await history_chain.arun(
                context=context_data["context"],
                question=query,
                history=history_text
            )
            
            if return_sources:
                return {
                    "response": chain_response,
                    "sources": context_data["sources"],
                    "relevance_scores": context_data["relevance_scores"]
                }
                
            return chain_response
            
        except Exception as e:
            logger.error(
                f"Failed to generate response with history: {str(e)}"
            )
            error_msg = (
                "I apologize, but I encountered an error while "
                "processing your question. Please try again."
            )
            
            if return_sources:
                return {
                    "response": error_msg,
                    "sources": [],
                    "relevance_scores": []
                }
            return error_msg
