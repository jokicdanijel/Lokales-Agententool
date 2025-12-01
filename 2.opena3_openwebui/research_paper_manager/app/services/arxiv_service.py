"""
arXiv Service - Integration mit arXiv API
"""

import requests
import feedparser
from typing import List, Dict, Optional
from datetime import datetime
import json


class ArxivService:
    """Service für arXiv API Zugriff"""

    BASE_URL = "https://export.arxiv.org/api/query"

    def __init__(self, max_results: int = 100, timeout: int = 30):
        self.max_results = max_results
        self.timeout = timeout

    def search(self, query: str, category: Optional[str] = None,
               max_results: Optional[int] = None, sort_by: str = "submittedDate",
               sort_order: str = "descending") -> List[Dict]:
        """
        Suche nach Papers in arXiv

        Args:
            query: Suchbegriff (z.B. "machine learning")
            category: arXiv Kategorie (z.B. "cs.AI")
            max_results: Maximale Ergebnisse
            sort_by: Sortierung (relevance, submittedDate, lastUpdatedDate)
            sort_order: ascending oder descending

        Returns:
            Liste von Paper-Daten
        """
        max_results = max_results or self.max_results

        # Query-String zusammenbauen
        search_query = query
        if category:
            search_query += f" AND cat:{category}"

        params = {
            "search_query": search_query,
            "start": 0,
            "max_results": max_results,
            "sortBy": sort_by,
            "sortOrder": sort_order
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            feed = feedparser.parse(response.text)
            papers = []

            for entry in feed.entries:
                paper = self._parse_entry(entry)
                papers.append(paper)

            return papers

        except requests.RequestException as e:
            print(f"Error querying arXiv: {e}")
            return []

    def fetch_paper(self, arxiv_id: str) -> Optional[Dict]:
        """
        Fetch spezifisches Paper von arXiv

        Args:
            arxiv_id: arXiv ID (z.B. "2505.09388" oder "2505.09388v1")

        Returns:
            Paper-Daten oder None
        """
        # Bereinige arXiv ID (entferne Version)
        clean_id = arxiv_id.split('v')[0] if 'v' in arxiv_id else arxiv_id

        params = {
            "id_list": clean_id,
            "start": 0,
            "max_results": 1
        }

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            response.raise_for_status()

            feed = feedparser.parse(response.text)

            if feed.entries:
                return self._parse_entry(feed.entries[0])
            return None

        except requests.RequestException as e:
            print(f"Error fetching paper {arxiv_id}: {e}")
            return None

    def get_pdf_url(self, arxiv_id: str) -> Optional[str]:
        """
        Hole PDF URL für Paper

        Args:
            arxiv_id: arXiv ID

        Returns:
            PDF URL oder None
        """
        clean_id = arxiv_id.split('v')[0]
        return f"https://arxiv.org/pdf/{clean_id}.pdf"

    def download_pdf(self, arxiv_id: str, save_path: str) -> bool:
        """
        Download PDF von arXiv Paper

        Args:
            arxiv_id: arXiv ID
            save_path: Speicherpath

        Returns:
            True wenn erfolgreich
        """
        pdf_url = self.get_pdf_url(arxiv_id)

        try:
            response = requests.get(pdf_url, timeout=self.timeout)
            response.raise_for_status()

            with open(save_path, 'wb') as f:
                f.write(response.content)

            print(f"PDF downloaded to {save_path}")
            return True

        except Exception as e:
            print(f"Error downloading PDF: {e}")
            return False

    def parse_arxiv_id(self, text: str) -> Optional[str]:
        """
        Parse arXiv ID aus Text

        Erkennt Formate wie:
        - 2505.09388
        - arXiv:2505.09388
        - arXiv:2505.09388v1
        - https://arxiv.org/abs/2505.09388

        Args:
            text: Text mit arXiv ID

        Returns:
            Gereinigte arXiv ID oder None
        """
        import re

        # Pattern für arXiv ID
        pattern = r'(?:arXiv:|arxiv\.org/(?:abs|pdf)/)(\d{4}\.\d{4,5})'

        match = re.search(pattern, text)
        if match:
            arxiv_id = match.group(1)
            # Entferne Version
            return arxiv_id.split('v')[0]

        # Versuche direktes Format
        direct_pattern = r'(\d{4}\.\d{4,5})'
        match = re.search(direct_pattern, text)
        if match:
            return match.group(1)

        return None

    @staticmethod
    def _parse_entry(entry) -> Dict:
        """Parse feedparser entry zu Paper-Dict"""

        # Extrahiere Autoren
        authors = []
        if 'authors' in entry:
            authors = [author.name for author in entry.authors]

        # Extrahiere arXiv ID
        arxiv_id = entry.id.split('/abs/')[-1]

        # Extrahiere Kategorien
        categories = []
        if 'tags' in entry:
            categories = [tag['term'] for tag in entry.tags]

        primary_category = categories[0] if categories else None

        # Zusammenfassung bereinigen
        summary = entry.summary.replace('\n', ' ').strip() if 'summary' in entry else ""

        return {
            'arxiv_id': arxiv_id,
            'title': entry.title,
            'authors': json.dumps(authors),
            'abstract': summary,
            'category': primary_category,
            'url': entry.id,
            'pdf_url': f"https://arxiv.org/pdf/{arxiv_id}.pdf",
            'published_date': entry.published[:10] if 'published' in entry else None,
            'metadata': {
                'all_categories': categories,
                'arxiv_url': entry.id,
                'updated': entry.updated if 'updated' in entry else None
            }
        }


# Hilfsfunktionen

def validate_arxiv_id(arxiv_id: str) -> bool:
    """
    Validiere arXiv ID Format

    Args:
        arxiv_id: arXiv ID zu validieren

    Returns:
        True wenn gültig
    """
    import re
    # Format: YYMM.NNNNN (neue Nummern) oder YYMM.NNNN (alte)
    pattern = r'^\d{4}\.\d{4,5}(?:v\d+)?$'
    return bool(re.match(pattern, arxiv_id))


def parse_arxiv_date(date_string: str) -> Optional[datetime]:
    """
    Parse arXiv Datum

    Args:
        date_string: Datum-String von arXiv

    Returns:
        datetime oder None
    """
    try:
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except:
        return None
