# modules/m5_synthetic_data/qa_generator.py
"""Generate synthetic Q&A pairs using GPT-4."""

import json
from typing import List, Dict, Optional
from openai import OpenAI
from tqdm import tqdm
from loguru import logger

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config


class QAGenerator:
    """Generates Q&A pairs from academic papers using GPT-4."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        api_key = self.config.api.openai_api_key
        
        # Check if API key is set
        if not api_key or api_key.strip() == "":
            raise ValueError(
                "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.\n"
                "You can set it by running: export OPENAI_API_KEY='your-api-key-here'\n"
                "Or create a .env file in the project root with: OPENAI_API_KEY=your-api-key-here"
            )
        
        # Set timeout to prevent hanging (60 seconds for API calls)
        self.client = OpenAI(api_key=api_key, timeout=60.0)
        
    def generate_qa_pairs(
        self,
        paper: Dict,
        num_pairs: int = 5
    ) -> List[Dict]:
        """Generate Q&A pairs for a single paper."""
        
        prompt = f"""You are a research assistant creating quiz questions from academic papers.

Paper Title: {paper.get('title', 'Unknown')}

Abstract:
{paper.get('abstract', '')}

Content (first 2000 chars):
{paper.get('full_text', '')[:2000]}

Generate {num_pairs} high-quality question-answer pairs that:
1. Cover key findings, methods, and concepts
2. Range from factual to conceptual questions
3. Have detailed, accurate answers based only on the provided text
4. Use appropriate academic terminology

Return as JSON array with format:
[{{"question": "...", "answer": "...", "type": "factual|conceptual|methodological"}}]

IMPORTANT: Base answers ONLY on the provided text. If something isn't mentioned, don't invent it."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000,
                response_format={"type": "json_object"},
                timeout=60.0  # 60 second timeout
            )
            
            content = response.choices[0].message.content
            # Parse JSON
            result = json.loads(content)
            
            # Handle different response formats
            if isinstance(result, dict) and "questions" in result:
                qa_pairs = result["questions"]
            elif isinstance(result, list):
                qa_pairs = result
            else:
                qa_pairs = [result]
            
            # Add source metadata
            for qa in qa_pairs:
                qa["source_arxiv_id"] = paper.get("arxiv_id", "")
                qa["source_title"] = paper.get("title", "")
            
            return qa_pairs
            
        except Exception as e:
            logger.error(f"Failed to generate Q&A for {paper.get('arxiv_id')}: {e}")
            return []
    
    def generate_edge_cases(self, paper: Dict, num_cases: int = 1) -> List[Dict]:
        """Generate edge case Q&A (hallucination tests)."""
        
        prompt = f"""Create {num_cases} "trick" questions about this paper that test if a model hallucinates:

Paper Title: {paper.get('title', 'Unknown')}
Abstract: {paper.get('abstract', '')}

Generate questions that:
1. Ask about details NOT in the paper (fake statistics, made-up experiments)
2. Include plausible-sounding but incorrect premises
3. Have answers that CORRECTLY identify the misinformation

Format as JSON array:
[{{"question": "...", "answer": "The paper does not mention/contain...", "type": "edge_case"}}]"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=1000,
                response_format={"type": "json_object"},
                timeout=60.0  # 60 second timeout
            )
            
            content = response.choices[0].message.content
            result = json.loads(content)
            
            if isinstance(result, dict):
                edge_cases = result.get("questions", [result])
            else:
                edge_cases = result
            
            for ec in edge_cases:
                ec["source_arxiv_id"] = paper.get("arxiv_id", "")
                ec["type"] = "edge_case"
            
            return edge_cases
            
        except Exception as e:
            logger.error(f"Failed to generate edge cases: {e}")
            return []
    
    def generate_batch(
        self,
        papers: List[Dict],
        qa_per_paper: Optional[int] = None,
        include_edge_cases: bool = True
    ) -> List[Dict]:
        """Generate Q&A for multiple papers."""
        qa_per_paper = qa_per_paper or self.config.data.qa_pairs_per_paper
        all_qa = []
        
        for paper in tqdm(papers, desc="Generating Q&A pairs"):
            # Regular Q&A
            qa_pairs = self.generate_qa_pairs(paper, qa_per_paper)
            all_qa.extend(qa_pairs)
            
            # Edge cases
            if include_edge_cases:
                edge_cases = self.generate_edge_cases(paper, 1)
                all_qa.extend(edge_cases)
        
        logger.info(f"Generated {len(all_qa)} Q&A pairs from {len(papers)} papers")
        return all_qa

