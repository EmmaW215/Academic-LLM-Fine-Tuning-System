# modules/m7_evaluation/evaluator.py
"""Model evaluation utilities."""

import torch
from typing import List, Dict, Optional
from dataclasses import dataclass
import json
from tqdm import tqdm
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config


@dataclass
class EvaluationResult:
    """Single evaluation result."""
    question: str
    expected_answer: str
    model_answer: str
    is_correct: bool
    relevance_score: float
    latency_ms: float


class ModelEvaluator:
    """Evaluates model responses."""
    
    def __init__(self, model, tokenizer, config=None):
        self.config = config or get_config()
        self.model = model
        self.tokenizer = tokenizer
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    def generate_response(
        self,
        question: str,
        max_new_tokens: int = 256
    ) -> tuple:
        """Generate response and measure latency."""
        import time
        
        # Format prompt
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{self.config.system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{question}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        
        start_time = time.time()
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.1,  # Low for deterministic eval
                do_sample=False,
                pad_token_id=self.tokenizer.pad_token_id
            )
        
        latency = (time.time() - start_time) * 1000  # ms
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract assistant response
        if "<|start_header_id|>assistant<|end_header_id|>" in response:
            response = response.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
        
        return response, latency
    
    def evaluate_single(
        self,
        question: str,
        expected_answer: str
    ) -> EvaluationResult:
        """Evaluate single question."""
        model_answer, latency = self.generate_response(question)
        
        # Simple relevance scoring (can be enhanced with semantic similarity)
        relevance = self._calculate_relevance(model_answer, expected_answer)
        is_correct = relevance > 0.5
        
        return EvaluationResult(
            question=question,
            expected_answer=expected_answer,
            model_answer=model_answer,
            is_correct=is_correct,
            relevance_score=relevance,
            latency_ms=latency
        )
    
    def _calculate_relevance(self, generated: str, expected: str) -> float:
        """Calculate relevance score between generated and expected."""
        # Simple word overlap (can be improved with embeddings)
        gen_words = set(generated.lower().split())
        exp_words = set(expected.lower().split())
        
        if not exp_words:
            return 0.0
        
        overlap = len(gen_words & exp_words)
        return overlap / len(exp_words)
    
    def evaluate_batch(
        self,
        test_data: List[Dict]
    ) -> List[EvaluationResult]:
        """Evaluate multiple questions."""
        results = []
        
        for item in tqdm(test_data, desc="Evaluating"):
            result = self.evaluate_single(
                question=item["question"],
                expected_answer=item["answer"]
            )
            results.append(result)
        
        return results
    
    def compute_metrics(self, results: List[EvaluationResult]) -> Dict:
        """Compute aggregate metrics."""
        if not results:
            return {}
        
        accuracy = sum(1 for r in results if r.is_correct) / len(results)
        avg_relevance = sum(r.relevance_score for r in results) / len(results)
        avg_latency = sum(r.latency_ms for r in results) / len(results)
        
        return {
            "accuracy": accuracy,
            "avg_relevance": avg_relevance,
            "avg_latency_ms": avg_latency,
            "total_evaluated": len(results)
        }

