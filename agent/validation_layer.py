#!/usr/bin/env python3
"""
NXT Research Agent - Validation Layer

Handles credibility scoring and semantic deduplication of research findings.
Uses Claude for semantic similarity analysis when needed.
"""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from anthropic import Anthropic


class ValidationLayer:
    """
    Validates research findings for credibility and uniqueness.
    
    Credibility scoring based on:
    - Source type (primary vs secondary)
    - Source authority (SEC, government, official company)
    - Corroboration from multiple sources
    - Recency of information
    - Contradiction detection
    """
    
    # Source credibility weights
    SOURCE_SCORES = {
        # Primary sources (highest credibility)
        "sec.gov": 90,
        "commerce.gov": 85,
        "energy.gov": 85,
        "epa.gov": 80,
        "state.gov": 80,
        "nist.gov": 85,
        
        # Grid operators (primary for queue data)
        "pjm.com": 85,
        "ercot.com": 85,
        "caiso.com": 85,
        "misoenergy.org": 85,
        "nyiso.com": 85,
        "spp.org": 85,
        
        # Major business news (secondary, high quality)
        "reuters.com": 75,
        "wsj.com": 75,
        "ft.com": 75,
        "bloomberg.com": 75,
        
        # Trade publications (secondary, specialized)
        "semianalysis.com": 70,
        "electrek.co": 65,
        "datacenterdynamics.com": 70,
        "utilitydive.com": 70,
        "theelec.co.kr": 65,
        
        # Local news (secondary, lower)
        "local_news": 55,
        
        # Unknown sources
        "unknown": 40,
    }
    
    # Filing type authority
    FILING_AUTHORITY = {
        "10-K": 95,  # Annual report
        "10-Q": 90,  # Quarterly report
        "8-K": 85,   # Current report (material events)
        "S-1": 85,   # IPO registration
        "DEF 14A": 80,  # Proxy statement
        "4": 75,     # Insider transactions
    }
    
    def __init__(self, anthropic_client: Optional[Anthropic] = None):
        """Initialize the validation layer."""
        self.client = anthropic_client
        self.semantic_cache = {}  # Cache semantic similarity results
    
    def verify_credibility(self, finding: Dict) -> Dict:
        """
        Calculate credibility score for a finding.
        
        Returns dict with:
        - score: 0-100 credibility score
        - flags: list of credibility factors
        - corroborating_sources: list of supporting sources
        - contradicting_sources: list of conflicting sources
        - recommendation: 'approve', 'hold', or 'reject'
        """
        credibility = {
            "score": 0,
            "flags": [],
            "corroborating_sources": [],
            "contradicting_sources": [],
            "recommendation": "reject"
        }
        
        raw_data = finding.get("raw_data", {})
        source_url = raw_data.get("source_url", "")
        source_type = raw_data.get("source_type", "secondary")
        source_name = raw_data.get("source_name", "")
        
        # 1. Base score from source type
        if source_type == "primary":
            credibility["score"] += 40
            credibility["flags"].append("PRIMARY_SOURCE")
        else:
            credibility["score"] += 20
            credibility["flags"].append("SECONDARY_SOURCE")
        
        # 2. Source authority score
        source_score = self._get_source_score(source_url)
        credibility["score"] += source_score * 0.4  # 40% weight
        
        if source_score >= 85:
            credibility["flags"].append("HIGH_AUTHORITY_SOURCE")
        elif source_score >= 70:
            credibility["flags"].append("MODERATE_AUTHORITY_SOURCE")
        else:
            credibility["flags"].append("LOW_AUTHORITY_SOURCE")
        
        # 3. SEC filing bonus
        if "sec.gov" in source_url.lower():
            filing_type = self._detect_filing_type(source_name)
            if filing_type:
                filing_score = self.FILING_AUTHORITY.get(filing_type, 70)
                credibility["score"] += filing_score * 0.2
                credibility["flags"].append(f"SEC_FILING_{filing_type}")
        
        # 4. Government source bonus
        gov_domains = [".gov", "commerce.gov", "energy.gov", "epa.gov"]
        if any(domain in source_url.lower() for domain in gov_domains):
            credibility["score"] += 10
            credibility["flags"].append("GOVERNMENT_SOURCE")
        
        # 5. Recency check
        pub_date = raw_data.get("publication_date", "")
        recency_score = self._calculate_recency_score(pub_date)
        credibility["score"] += recency_score * 0.1
        
        if recency_score >= 90:
            credibility["flags"].append("VERY_RECENT")
        elif recency_score >= 70:
            credibility["flags"].append("RECENT")
        elif recency_score < 50:
            credibility["flags"].append("STALE_DATA")
        
        # 6. Content quality check
        content = raw_data.get("extracted_text", "")
        quality_score = self._assess_content_quality(content)
        credibility["score"] += quality_score * 0.1
        
        if quality_score >= 80:
            credibility["flags"].append("HIGH_QUALITY_CONTENT")
        elif quality_score < 50:
            credibility["flags"].append("LOW_QUALITY_CONTENT")
        
        # Normalize score to 0-100
        credibility["score"] = min(100, max(0, int(credibility["score"])))
        
        # Set recommendation
        if credibility["score"] >= 80:
            credibility["recommendation"] = "approve"
        elif credibility["score"] >= 60:
            credibility["recommendation"] = "approve_moderate"
        elif credibility["score"] >= 40:
            credibility["recommendation"] = "hold_for_corroboration"
        else:
            credibility["recommendation"] = "reject"
        
        return credibility
    
    def _get_source_score(self, url: str) -> int:
        """Get credibility score for a source URL."""
        url_lower = url.lower()
        
        for domain, score in self.SOURCE_SCORES.items():
            if domain in url_lower:
                return score
        
        # Check for local news indicators
        local_indicators = [
            "gazette", "tribune", "herald", "times", "news",
            "post", "journal", "chronicle", "dispatch"
        ]
        if any(indicator in url_lower for indicator in local_indicators):
            return self.SOURCE_SCORES["local_news"]
        
        return self.SOURCE_SCORES["unknown"]
    
    def _detect_filing_type(self, source_name: str) -> Optional[str]:
        """Detect SEC filing type from source name."""
        source_upper = source_name.upper()
        
        for filing_type in self.FILING_AUTHORITY.keys():
            if filing_type in source_upper:
                return filing_type
        
        return None
    
    def _calculate_recency_score(self, pub_date: str) -> int:
        """Calculate recency score based on publication date."""
        if not pub_date:
            return 50  # Unknown date gets neutral score
        
        try:
            if "T" in pub_date:
                pub_datetime = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
            else:
                pub_datetime = datetime.strptime(pub_date, "%Y-%m-%d")
            
            days_old = (datetime.utcnow() - pub_datetime.replace(tzinfo=None)).days
            
            if days_old <= 1:
                return 100
            elif days_old <= 3:
                return 95
            elif days_old <= 7:
                return 90
            elif days_old <= 14:
                return 80
            elif days_old <= 30:
                return 70
            elif days_old <= 60:
                return 60
            elif days_old <= 90:
                return 50
            else:
                return 40
                
        except (ValueError, TypeError):
            return 50
    
    def _assess_content_quality(self, content: str) -> int:
        """Assess content quality based on various signals."""
        if not content:
            return 30
        
        score = 50  # Base score
        
        # Length check
        word_count = len(content.split())
        if word_count >= 100:
            score += 15
        elif word_count >= 50:
            score += 10
        elif word_count < 20:
            score -= 10
        
        # Contains specific data points
        data_indicators = [
            "$", "billion", "million", "percent", "%",
            "2024", "2025", "2026", "2027",
            "Q1", "Q2", "Q3", "Q4",
            "MW", "GW", "employees", "jobs", "workforce"
        ]
        data_count = sum(1 for ind in data_indicators if ind.lower() in content.lower())
        score += min(data_count * 3, 20)
        
        # Contains quotes (indicates direct sources)
        if '"' in content or "said" in content.lower() or "announced" in content.lower():
            score += 10
        
        # Spam indicators (reduce score)
        spam_indicators = [
            "click here", "subscribe", "sign up",
            "limited time", "act now", "exclusive offer"
        ]
        spam_count = sum(1 for ind in spam_indicators if ind.lower() in content.lower())
        score -= spam_count * 10
        
        return min(100, max(0, score))
    
    def check_semantic_duplicate(self, finding: Dict, 
                                  recent_findings: List[Dict]) -> bool:
        """
        Use Claude to check if finding is semantically similar to recent findings.
        
        This catches duplicates that have different wording but same meaning,
        e.g., "Intel delays Ohio fab to 2030" vs "Intel pushes back Ohio timeline 5 years"
        """
        if not self.client or not recent_findings:
            return False
        
        # Create cache key
        finding_hash = hashlib.md5(
            finding["raw_data"]["extracted_text"][:500].encode()
        ).hexdigest()
        
        if finding_hash in self.semantic_cache:
            return self.semantic_cache[finding_hash]
        
        # Build comparison prompt
        finding_summary = self._summarize_finding(finding)
        recent_summaries = [self._summarize_finding(f) for f in recent_findings[:5]]
        
        prompt = f"""Analyze if the NEW FINDING below is semantically equivalent to any of the EXISTING FINDINGS.
Two findings are equivalent if they report the same core fact or development, even if worded differently.

NEW FINDING:
Project: {finding.get('project_name', 'Unknown')}
Category: {finding.get('category', 'Unknown')}
Content: {finding_summary}

EXISTING FINDINGS (last 30 days for same project):
{chr(10).join(f'- {s}' for s in recent_summaries)}

Is the NEW FINDING semantically equivalent to any existing finding? 
Respond with only "DUPLICATE" or "UNIQUE" followed by a brief explanation."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result_text = response.content[0].text.strip().upper()
            is_duplicate = result_text.startswith("DUPLICATE")
            
            # Cache result
            self.semantic_cache[finding_hash] = is_duplicate
            
            return is_duplicate
            
        except Exception as e:
            print(f"    Semantic check failed: {e}")
            return False
    
    def _summarize_finding(self, finding: Dict) -> str:
        """Create a brief summary of a finding for comparison."""
        content = finding.get("raw_data", {}).get("extracted_text", "")
        source = finding.get("raw_data", {}).get("source_name", "Unknown")
        date = finding.get("raw_data", {}).get("publication_date", "Unknown")
        
        # Truncate content
        if len(content) > 300:
            content = content[:300] + "..."
        
        return f"[{date}] [{source}] {content}"
    
    def find_corroborating_sources(self, finding: Dict, 
                                    all_findings: List[Dict]) -> List[Dict]:
        """
        Find other findings that corroborate this one.
        
        Corroboration requires:
        - Same project
        - Same general topic/category
        - Different source
        - Similar timeframe
        """
        corroborating = []
        
        project_id = finding.get("project_id")
        category = finding.get("category")
        source_url = finding.get("raw_data", {}).get("source_url", "")
        
        for other in all_findings:
            if other.get("finding_id") == finding.get("finding_id"):
                continue
            
            # Same project
            if other.get("project_id") != project_id:
                continue
            
            # Same or related category
            if other.get("category") != category:
                continue
            
            # Different source
            other_url = other.get("raw_data", {}).get("source_url", "")
            if self._same_source(source_url, other_url):
                continue
            
            corroborating.append(other)
        
        return corroborating
    
    def find_contradicting_sources(self, finding: Dict,
                                    all_findings: List[Dict]) -> List[Dict]:
        """
        Find findings that contradict this one.
        
        This is a simplified check. A more robust version would use
        Claude to detect semantic contradictions.
        """
        contradicting = []
        
        # For now, just return empty list
        # Full implementation would use Claude to detect contradictions
        
        return contradicting
    
    def _same_source(self, url1: str, url2: str) -> bool:
        """Check if two URLs are from the same source."""
        def extract_domain(url):
            url = url.lower()
            if "://" in url:
                url = url.split("://")[1]
            if "/" in url:
                url = url.split("/")[0]
            # Remove www.
            if url.startswith("www."):
                url = url[4:]
            return url
        
        return extract_domain(url1) == extract_domain(url2)


class DeduplicationEngine:
    """
    Handles deduplication of research findings using multiple strategies.
    """
    
    def __init__(self, research_log: Dict):
        """Initialize with existing research log."""
        self.research_log = research_log
        self.seen_hashes = set(research_log.get("seen_hashes", []))
    
    def is_exact_duplicate(self, finding: Dict) -> bool:
        """Check for exact content hash match."""
        content_hash = finding.get("raw_data", {}).get("content_hash", "")
        return content_hash in self.seen_hashes
    
    def is_url_duplicate(self, finding: Dict) -> bool:
        """Check if same URL and date already processed."""
        source_url = finding.get("raw_data", {}).get("source_url", "")
        pub_date = finding.get("raw_data", {}).get("publication_date", "")
        
        for prior in self.research_log.get("findings", []):
            prior_url = prior.get("raw_data", {}).get("source_url", "")
            prior_date = prior.get("raw_data", {}).get("publication_date", "")
            
            if prior_url == source_url and prior_date == pub_date:
                return True
        
        return False
    
    def get_cluster_id(self, finding: Dict) -> Optional[str]:
        """
        Get semantic cluster ID for a finding.
        
        Findings in the same cluster represent the same underlying fact
        from different sources or time periods.
        """
        project_id = finding.get("project_id", "")
        category = finding.get("category", "")
        
        # Generate cluster key
        pub_date = finding.get("raw_data", {}).get("publication_date", "")
        if pub_date:
            try:
                dt = datetime.strptime(pub_date[:10], "%Y-%m-%d")
                quarter = f"{dt.year}Q{(dt.month-1)//3+1}"
            except ValueError:
                quarter = "unknown"
        else:
            quarter = "unknown"
        
        return f"{project_id}_{category}_{quarter}"
    
    def add_to_cluster(self, finding: Dict, cluster_id: str):
        """Add finding to a semantic cluster."""
        clusters = self.research_log.setdefault("semantic_clusters", {})
        
        if cluster_id not in clusters:
            clusters[cluster_id] = []
        
        finding_id = finding.get("finding_id", "")
        if finding_id and finding_id not in clusters[cluster_id]:
            clusters[cluster_id].append(finding_id)
    
    def mark_as_seen(self, finding: Dict):
        """Mark a finding's content hash as seen."""
        content_hash = finding.get("raw_data", {}).get("content_hash", "")
        if content_hash:
            self.seen_hashes.add(content_hash)
            self.research_log.setdefault("seen_hashes", []).append(content_hash)


if __name__ == "__main__":
    # Test validation layer
    validator = ValidationLayer()
    
    test_finding = {
        "finding_id": "F-TEST-001",
        "project_id": "SE001",
        "project_name": "TSMC Arizona",
        "category": "financial",
        "raw_data": {
            "source_url": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=TSM",
            "source_type": "primary",
            "source_name": "SEC 10-K Filing",
            "publication_date": "2026-01-25",
            "content_hash": "abc123",
            "extracted_text": "TSMC announced that its Arizona fab Phase 1 has achieved "
                             "initial production yields of 85%, exceeding targets. The company "
                             "has invested $28 billion to date and expects full production "
                             "capacity by Q2 2025."
        }
    }
    
    result = validator.verify_credibility(test_finding)
    print(f"Credibility Score: {result['score']}")
    print(f"Flags: {result['flags']}")
    print(f"Recommendation: {result['recommendation']}")
