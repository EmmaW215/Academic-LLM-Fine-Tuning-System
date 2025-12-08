# modules/m7_evaluation/comparator.py
"""Compare base and fine-tuned models."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json
from pathlib import Path
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config, MODEL_DIR, DATA_DIR
from .evaluator import ModelEvaluator, EvaluationResult


@dataclass
class ComparisonResult:
    """Comparison between two models."""
    question: str
    base_answer: str
    finetuned_answer: str
    expected_answer: str
    base_relevance: float
    finetuned_relevance: float
    winner: str  # "base", "finetuned", or "tie"


class ModelComparator:
    """Compares base vs fine-tuned model performance."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.base_evaluator = None
        self.ft_evaluator = None
        
    def setup_models(
        self,
        base_model,
        base_tokenizer,
        finetuned_model,
        finetuned_tokenizer
    ):
        """Setup both evaluators."""
        self.base_evaluator = ModelEvaluator(
            base_model, base_tokenizer, self.config
        )
        self.ft_evaluator = ModelEvaluator(
            finetuned_model, finetuned_tokenizer, self.config
        )
        
    def compare_single(
        self,
        question: str,
        expected_answer: str
    ) -> ComparisonResult:
        """Compare models on single question."""
        base_result = self.base_evaluator.evaluate_single(question, expected_answer)
        ft_result = self.ft_evaluator.evaluate_single(question, expected_answer)
        
        # Determine winner
        if ft_result.relevance_score > base_result.relevance_score + 0.1:
            winner = "finetuned"
        elif base_result.relevance_score > ft_result.relevance_score + 0.1:
            winner = "base"
        else:
            winner = "tie"
        
        return ComparisonResult(
            question=question,
            base_answer=base_result.model_answer,
            finetuned_answer=ft_result.model_answer,
            expected_answer=expected_answer,
            base_relevance=base_result.relevance_score,
            finetuned_relevance=ft_result.relevance_score,
            winner=winner
        )
    
    def compare_batch(
        self,
        test_data: List[Dict]
    ) -> Tuple[List[ComparisonResult], Dict]:
        """Compare models on multiple questions."""
        results = []
        
        for item in test_data:
            result = self.compare_single(
                question=item["question"],
                expected_answer=item["answer"]
            )
            results.append(result)
        
        # Aggregate stats
        stats = self._compute_comparison_stats(results)
        
        return results, stats
    
    def _compute_comparison_stats(self, results: List[ComparisonResult]) -> Dict:
        """Compute comparison statistics."""
        total = len(results)
        ft_wins = sum(1 for r in results if r.winner == "finetuned")
        base_wins = sum(1 for r in results if r.winner == "base")
        ties = sum(1 for r in results if r.winner == "tie")
        
        base_avg_rel = sum(r.base_relevance for r in results) / total
        ft_avg_rel = sum(r.finetuned_relevance for r in results) / total
        
        improvement = ((ft_avg_rel - base_avg_rel) / base_avg_rel * 100) if base_avg_rel > 0 else 0
        
        return {
            "total_questions": total,
            "finetuned_wins": ft_wins,
            "base_wins": base_wins,
            "ties": ties,
            "finetuned_win_rate": ft_wins / total,
            "base_avg_relevance": base_avg_rel,
            "finetuned_avg_relevance": ft_avg_rel,
            "improvement_percent": improvement
        }

