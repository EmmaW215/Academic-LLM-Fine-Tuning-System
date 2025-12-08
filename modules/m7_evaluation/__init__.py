# modules/m7_evaluation/__init__.py
"""Module 7: Model Evaluation."""

from .evaluator import ModelEvaluator, EvaluationResult
from .comparator import ModelComparator, ComparisonResult
from .report_generator import ReportGenerator

__all__ = ["ModelEvaluator", "ModelComparator", "ReportGenerator", "EvaluationResult", "ComparisonResult"]

