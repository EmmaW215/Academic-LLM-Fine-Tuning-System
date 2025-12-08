# modules/m7_evaluation/report_generator.py
"""Generate evaluation reports."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import asdict
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import DATA_DIR


class ReportGenerator:
    """Generates evaluation reports."""
    
    def __init__(self, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (DATA_DIR / "reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_comparison_report(
        self,
        comparison_results: List,
        stats: Dict,
        model_info: Optional[Dict] = None
    ) -> str:
        """Generate markdown comparison report."""
        report = f"""# Model Comparison Report

Generated: {datetime.now().isoformat()}

## Model Information
{json.dumps(model_info or {}, indent=2)}

## Summary Statistics

| Metric | Value |
|--------|-------|
| Total Questions | {stats['total_questions']} |
| Fine-tuned Wins | {stats['finetuned_wins']} ({stats['finetuned_win_rate']:.1%}) |
| Base Model Wins | {stats['base_wins']} |
| Ties | {stats['ties']} |
| Base Avg Relevance | {stats['base_avg_relevance']:.3f} |
| Fine-tuned Avg Relevance | {stats['finetuned_avg_relevance']:.3f} |
| **Improvement** | **{stats['improvement_percent']:.1f}%** |

## Detailed Results

"""
        for i, result in enumerate(comparison_results, 1):
            r = result if isinstance(result, dict) else asdict(result)
            report += f"""### Question {i}
**Q:** {r['question']}

**Expected:** {r['expected_answer'][:200]}...

| Model | Response | Relevance |
|-------|----------|-----------|
| Base | {r['base_answer'][:150]}... | {r['base_relevance']:.3f} |
| Fine-tuned | {r['finetuned_answer'][:150]}... | {r['finetuned_relevance']:.3f} |

**Winner:** {r['winner']}

---

"""
        return report
    
    def save_report(
        self,
        report: str,
        filename: str = "comparison_report.md"
    ) -> Path:
        """Save report to file."""
        filepath = self.output_dir / filename
        filepath.write_text(report)
        logger.info(f"Report saved to {filepath}")
        return filepath
    
    def save_json_results(
        self,
        results: List,
        stats: Dict,
        filename: str = "evaluation_results.json"
    ) -> Path:
        """Save results as JSON."""
        filepath = self.output_dir / filename
        
        data = {
            "generated_at": datetime.now().isoformat(),
            "statistics": stats,
            "results": [asdict(r) if hasattr(r, '__dataclass_fields__') else r for r in results]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Results saved to {filepath}")
        return filepath

