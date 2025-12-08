# modules/m2_data_collection/arxiv_scraper.py
"""arXiv paper scraping and downloading."""

import arxiv
import requests
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
from tqdm import tqdm
from loguru import logger

import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.settings import get_config, DATA_DIR


@dataclass
class PaperMetadata:
    """Metadata for an arXiv paper."""
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published: str
    updated: str
    pdf_url: str
    local_pdf_path: Optional[str] = None


class ArxivScraper:
    """Scrapes and downloads papers from arXiv."""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.raw_dir = DATA_DIR / "raw"
        self.metadata_file = DATA_DIR / "processed" / "papers_metadata.json"
        self.papers: List[PaperMetadata] = []
        
    def search_papers(
        self, 
        category: Optional[str] = None,
        query: Optional[str] = None,
        max_results: Optional[int] = None
    ) -> List[PaperMetadata]:
        """Search arXiv for papers."""
        category = category or self.config.data.arxiv_category
        max_results = max_results or self.config.data.num_papers
        
        # Build search query
        if query:
            search_query = f"cat:{category} AND ({query})"
        else:
            search_query = f"cat:{category}"
        
        logger.info(f"Searching arXiv: {search_query}, max_results={max_results}")
        
        search = arxiv.Search(
            query=search_query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )
        
        client = arxiv.Client()
        results = list(client.results(search))
        
        self.papers = []
        for result in results:
            paper = PaperMetadata(
                arxiv_id=result.entry_id.split("/")[-1],
                title=result.title.replace("\n", " "),
                authors=[author.name for author in result.authors],
                abstract=result.summary.replace("\n", " "),
                categories=result.categories,
                published=result.published.isoformat(),
                updated=result.updated.isoformat(),
                pdf_url=result.pdf_url
            )
            self.papers.append(paper)
        
        logger.info(f"Found {len(self.papers)} papers")
        return self.papers
    
    def download_pdfs(self, papers: Optional[List[PaperMetadata]] = None) -> List[str]:
        """Download PDFs for all papers."""
        papers = papers or self.papers
        downloaded_paths = []
        
        logger.info(f"Downloading {len(papers)} PDFs...")
        
        for paper in tqdm(papers, desc="Downloading PDFs"):
            try:
                # Create filename from arxiv_id
                filename = f"{paper.arxiv_id.replace('/', '_')}.pdf"
                filepath = self.raw_dir / filename
                
                if filepath.exists():
                    logger.debug(f"Already exists: {filename}")
                    paper.local_pdf_path = str(filepath)
                    downloaded_paths.append(str(filepath))
                    continue
                
                # Download PDF
                response = requests.get(paper.pdf_url, timeout=60)
                response.raise_for_status()
                
                filepath.write_bytes(response.content)
                paper.local_pdf_path = str(filepath)
                downloaded_paths.append(str(filepath))
                
                logger.debug(f"Downloaded: {filename}")
                
            except Exception as e:
                logger.error(f"Failed to download {paper.arxiv_id}: {e}")
        
        logger.info(f"Downloaded {len(downloaded_paths)} PDFs")
        return downloaded_paths
    
    def save_metadata(self, filepath: Optional[Path] = None):
        """Save paper metadata to JSON."""
        filepath = filepath or self.metadata_file
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "scraped_at": datetime.now().isoformat(),
            "category": self.config.data.arxiv_category,
            "total_papers": len(self.papers),
            "papers": [asdict(p) for p in self.papers]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved metadata to {filepath}")
    
    def load_metadata(self, filepath: Optional[Path] = None) -> List[PaperMetadata]:
        """Load paper metadata from JSON."""
        filepath = filepath or self.metadata_file
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.papers = [PaperMetadata(**p) for p in data["papers"]]
        logger.info(f"Loaded {len(self.papers)} papers from {filepath}")
        return self.papers

