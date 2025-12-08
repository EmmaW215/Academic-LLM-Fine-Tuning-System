# modules/m1_langchain_llama/llm_loader.py
"""LLM loading utilities for LLaMA 3 models."""

import torch
from pathlib import Path
from typing import Optional, Tuple
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from peft import PeftModel
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config, MODEL_DIR


class LLMLoader:
    """Handles loading and managing LLaMA models."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def load_base_model(self) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load the base LLaMA model with 4-bit quantization."""
        logger.info(f"Loading base model: {self.config.model.base_model_name}")
        
        # Quantization config for 4-bit loading
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True
        )
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.config.model.base_model_name,
            trust_remote_code=True
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "right"
        
        # Determine device map - prefer GPU but allow CPU offloading if needed
        if torch.cuda.is_available():
            # Try to load on GPU first, but allow CPU offloading if GPU memory is insufficient
            device_map = "auto"
        else:
            device_map = "cpu"
        
        # Load model with low_cpu_mem_usage to handle memory efficiently
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model.base_model_name,
            quantization_config=bnb_config,
            device_map=device_map,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True,
            max_memory={0: "15GiB", "cpu": "30GiB"} if torch.cuda.is_available() else None
        )
        
        logger.info(f"Base model loaded on {self.device}")
        return self.model, self.tokenizer
    
    def load_finetuned_model(
        self, 
        adapter_path: Optional[str] = None
    ) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """Load a fine-tuned model with LoRA adapters."""
        adapter_path = adapter_path or self.config.training.output_dir
        
        logger.info(f"Loading fine-tuned model from: {adapter_path}")
        
        # First load base model if not loaded
        if self.model is None:
            self.load_base_model()
        
        # Load LoRA adapters
        self.model = PeftModel.from_pretrained(
            self.model,
            adapter_path,
            is_trainable=False
        )
        self.model = self.model.merge_and_unload()  # Merge for inference
        
        logger.info("Fine-tuned model loaded and merged")
        return self.model, self.tokenizer
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        do_sample: bool = True
    ) -> str:
        """Generate text from the loaded model."""
        if self.model is None:
            raise ValueError("Model not loaded. Call load_base_model() first.")
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        # Determine device for inputs
        # When device_map="auto" is used, model might be split across devices
        # Use the device of the first model parameter, or default to self.device
        try:
            # Get device from first model parameter
            first_param = next(self.model.parameters())
            input_device = first_param.device
        except (StopIteration, AttributeError):
            # Fallback to self.device if model has no parameters or device info
            input_device = self.device
        
        inputs = {k: v.to(input_device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Remove the input prompt from response
        response = response[len(self.tokenizer.decode(inputs['input_ids'][0], skip_special_tokens=True)):]
        return response.strip()
    
    def format_prompt(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """Format prompt using LLaMA 3 chat template."""
        system_prompt = system_prompt or self.config.system_prompt
        
        # LLaMA 3 Instruct format
        formatted = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        return formatted


# Convenience functions
def load_base_model(config=None):
    """Quick function to load base model."""
    loader = LLMLoader(config)
    return loader.load_base_model()

def load_finetuned_model(adapter_path=None, config=None):
    """Quick function to load fine-tuned model."""
    loader = LLMLoader(config)
    return loader.load_finetuned_model(adapter_path)

