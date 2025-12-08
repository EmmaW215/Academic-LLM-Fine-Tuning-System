# modules/m6_fine_tuning/qlora_trainer.py
"""QLoRA training implementation."""

import torch
from pathlib import Path
from typing import Optional, Dict
from datasets import load_dataset, Dataset
from transformers import (
    TrainingArguments,
    DataCollatorForLanguageModeling
)
from trl import SFTTrainer, SFTConfig
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config, DATA_DIR, MODEL_DIR
from .model_loader import FineTuneModelLoader


class QLoRATrainer:
    """Handles QLoRA fine-tuning workflow."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.model_loader = FineTuneModelLoader(config)
        self.model = None
        self.tokenizer = None
        self.trainer = None
        
    def setup(self):
        """Initialize model and tokenizer."""
        self.model, self.tokenizer = self.model_loader.load_for_training()
        
    def load_dataset(
        self,
        data_path: Optional[str] = None
    ) -> Dataset:
        """Load training dataset."""
        data_path = data_path or str(DATA_DIR / "synthetic" / "synthetic_qa.jsonl")
        data_file = Path(data_path)
        
        # Check if file exists
        if not data_file.exists():
            raise FileNotFoundError(
                f"Dataset file not found: {data_path}\n"
                "Please run 'Synthetic Data Generation' first to create the training dataset."
            )
        
        # Check if file is empty
        if data_file.stat().st_size == 0:
            raise ValueError(
                f"Dataset file is empty: {data_path}\n"
                "The synthetic data generation may have failed. Please:\n"
                "1. Check if OpenAI API key is set (export OPENAI_API_KEY='your-key')\n"
                "2. Run 'Synthetic Data Generation' again\n"
                "3. Check the error messages in the Generation Status"
            )
        
        logger.info(f"Loading dataset from {data_path}")
        try:
            dataset = load_dataset("json", data_files=data_path, split="train")
            logger.info(f"Dataset size: {len(dataset)} examples")
            
            if len(dataset) == 0:
                raise ValueError(
                    f"Dataset loaded but contains 0 examples: {data_path}\n"
                    "Please regenerate the synthetic data."
                )
            
            return dataset
        except Exception as e:
            raise RuntimeError(
                f"Failed to load dataset from {data_path}: {str(e)}\n"
                "Please check the file format and try regenerating the data."
            ) from e
    
    def train(
        self,
        dataset: Dataset,
        output_dir: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Run fine-tuning."""
        if self.model is None:
            self.setup()
        
        output_dir = output_dir or self.config.training.output_dir
        
        # Training arguments
        training_args = SFTConfig(
            output_dir=output_dir,
            num_train_epochs=kwargs.get("epochs", self.config.training.num_train_epochs),
            per_device_train_batch_size=kwargs.get("batch_size", self.config.training.per_device_train_batch_size),
            gradient_accumulation_steps=self.config.training.gradient_accumulation_steps,
            learning_rate=self.config.training.learning_rate,
            warmup_ratio=self.config.training.warmup_ratio,
            max_grad_norm=self.config.training.max_grad_norm,
            weight_decay=self.config.training.weight_decay,
            optim=self.config.training.optim,
            lr_scheduler_type=self.config.training.lr_scheduler_type,
            logging_steps=self.config.training.logging_steps,
            save_strategy=self.config.training.save_strategy,
            bf16=self.config.training.bf16,
            fp16=self.config.training.fp16,
            seed=self.config.training.seed,
            max_length=self.config.model.max_seq_length,  # SFTConfig uses 'max_length' not 'max_seq_length'
            dataset_text_field="text",
            packing=False
        )
        
        # Create trainer
        # Note: SFTTrainer uses 'processing_class' instead of 'tokenizer'
        self.trainer = SFTTrainer(
            model=self.model,
            processing_class=self.tokenizer,  # SFTTrainer uses 'processing_class' not 'tokenizer'
            train_dataset=dataset,
            args=training_args,
            data_collator=DataCollatorForLanguageModeling(
                tokenizer=self.tokenizer,
                mlm=False
            )
        )
        
        logger.info("Starting fine-tuning...")
        
        # Train
        train_result = self.trainer.train()
        
        # Save model
        self.trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Model saved to {output_dir}")
        
        return {
            "train_loss": train_result.training_loss,
            "train_runtime": train_result.metrics.get("train_runtime"),
            "output_dir": output_dir
        }
    
    def run_full_pipeline(
        self,
        data_path: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> Dict:
        """Run complete fine-tuning pipeline."""
        # Setup
        self.setup()
        
        # Load data
        dataset = self.load_dataset(data_path)
        
        # Train
        results = self.train(dataset, output_dir)
        
        return results

