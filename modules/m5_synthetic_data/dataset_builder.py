# modules/m5_synthetic_data/dataset_builder.py
"""Build training datasets in instruction-tuning format."""

import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config, DATA_DIR


class DatasetBuilder:
    """Builds instruction-tuning datasets."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.output_dir = DATA_DIR / "synthetic"
        
    def build_instruct_dataset(
        self,
        qa_pairs: List[Dict],
        system_prompt: Optional[str] = None
    ) -> List[Dict]:
        """Convert Q&A pairs to instruction format."""
        system_prompt = system_prompt or self.config.system_prompt
        
        dataset = []
        for qa in qa_pairs:
            # LLaMA 3 Instruct format
            formatted_text = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{qa['question']}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{qa['answer']}<|eot_id|>"""
            
            entry = {
                "text": formatted_text,
                "question": qa["question"],
                "answer": qa["answer"],
                "type": qa.get("type", "unknown"),
                "source": qa.get("source_arxiv_id", "")
            }
            dataset.append(entry)
        
        return dataset
    
    def save_jsonl(
        self,
        dataset: List[Dict],
        filename: str = "synthetic_qa.jsonl"
    ) -> Path:
        """Save dataset as JSONL."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for entry in dataset:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        logger.info(f"Saved {len(dataset)} entries to {filepath}")
        return filepath
    
    def load_jsonl(self, filename: str = "synthetic_qa.jsonl") -> List[Dict]:
        """Load dataset from JSONL."""
        filepath = self.output_dir / filename
        
        dataset = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                dataset.append(json.loads(line))
        
        return dataset
    
    def split_dataset(
        self,
        dataset: List[Dict],
        train_ratio: float = 0.9
    ) -> Tuple[List[Dict], List[Dict]]:
        """Split dataset into train and validation."""
        import random
        random.shuffle(dataset)
        
        split_idx = int(len(dataset) * train_ratio)
        train = dataset[:split_idx]
        val = dataset[split_idx:]
        
        logger.info(f"Split: {len(train)} train, {len(val)} validation")
        return train, val

