#!/usr/bin/env python3
"""
Custom news scraper for NXT Research Agent.
Scrapes multiple news sources without relying on paid APIs.
"""

import re
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from urllib.parse import urljoin, quote_plus
import requests
from bs4 import BeautifulSoup


class NewsScraper:
    """
    Custom scraper for construction and infrastructure news.
    Targets specific high-quality sources without paid API dependencies.
    """
    
    def __init__(self):
        """Initialize the news scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        
        # Source configurations
        self.sources = {
            "reuters.com": {
                "search_url": "https://www.reuters.com/site-search/?query={query}",
                "article_selector": "li.search-results__item",
                "title_selector": "h3.search-results__title",
                "link_selector": "a",
                "date_selector": "time",
                "content_selector": "article p",
            },
            "wsj.com": {
                "search_url": "https://www.wsj.com/search?query={query}&mod=searchresults_viewallresults",
                "article_selector": "article",
                "title_selector": "h3",
                "link_selector": "a",
                "date_selector": "time",
                "content_selector": "article p",
            },
            "electrek.co": {
                "search_url": "https://electrek.co/?s={query}",
                "article_selector": "article.post",
                "title_selector": "h2.entry-title",
                "link_selector": "a",
                "date_selector": "time.entry-date",
                "content_selector": "div.entry-content p",
            },
            "semianalysis.com": {
                "search_url": "https://www.semianalysis.com/search?q={query}",
                "article_selector": "div.post-preview",
                "title_selector": "h2.post-title",
                "link_selector": "a",
                "date_selector": "time",
                "content_selector": "div.post-content p",
            },
            "datacenterdynamics.com": {
                "search_url": "https://www.datacenterdynamics.com/en/search/?q={query}",
                "article_selector": "div.search-result",
                "title_selector": "h3",
                "link_selector": "a",
                "date_selector": "time",
                "content_selector": "article p",
            },
            "utilitydive.com": {
                "search_url": "https://www.utilitydive.com/search/?q={query}",
                "article_selector": "li.feed__item",
                "title_selector": "h3.feed__title",
                "link_selector": "a",
                "date_selector": "time",
                "content_selector": "article p",
            },
        }
        
        # Local news sources by state
        self.local_sources = {
            "arizona": ["azcentral.com"],
            "ohio": ["dispatch.com", "cleveland.com"],
            "texas": ["statesman.com", "dallasnews.com", "reporternews.com"],
            "georgia": ["ajc.com", "savannahnow.com"],
            "tennessee": ["tennessean.com", "commercialappeal.com"],
            "north_carolina": ["newsobserver.com"],
            "kentucky": ["courier-journal.com"],
            "indiana": ["indystar.com"],
            "michigan": ["freep.com", "mlive.com"],
            "new_york": ["syracuse.com", "timesunion.com"],
            "louisiana": ["theadvocate.com"],
            "west_virginia": ["wvgazettemail.com"],
            "kansas": ["kansascity.com"],
        }
    
    def search(self, query: str, sources: List[str] = None, 
               days_back: int = 7) -> List[Dict]:
        """
        Search for news articles across specified sources.
        
        Args:
            query: Search query string
            sources: List of source domains to search (default: all)
            days_back: How many days back to search
            
        Returns:
            List of article dictionaries
        """
        results = []
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Determine which sources to search
        if sources:
            search_sources = [s for s in sources if s in self.sources]
        else:
            search_sources = list(self.sources.keys())
        
        for source_domain in search_sources:
            try:
                source_results = self._search_source(
                    source_domain, 
                    query, 
                    cutoff_date
                )
                results.extend(source_results)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"    Warning: Failed to search {source_domain}: {e}")
                continue
        
        # Deduplicate by URL
        seen_urls = set()
        unique_results = []
        for result in results:
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                unique_results.append(result)
        
        return unique_results
    
    def _search_source(self, source_domain: str, query: str, 
                       cutoff_date: datetime) -> List[Dict]:
        """Search a single news source."""
        config = self.sources.get(source_domain)
        if not config:
            return []
        
        results = []
        
        # Build search URL
        search_url = config["search_url"].format(query=quote_plus(query))
        
        try:
            response = self.session.get(search_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Find articles
            articles = soup.select(config["article_selector"])[:10]  # Limit to 10
            
            for article in articles:
                try:
                    # Extract title
                    title_elem = article.select_one(config["title_selector"])
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    
                    # Extract link
                    link_elem = article.select_one(config["link_selector"])
                    if not link_elem or not link_elem.get("href"):
                        continue
                    url = link_elem["href"]
                    if not url.startswith("http"):
                        url = urljoin(f"https://{source_domain}", url)
                    
                    # Extract date
                    date_elem = article.select_one(config["date_selector"])
                    if date_elem:
                        date_str = date_elem.get("datetime") or date_elem.get_text(strip=True)
                        published_date = self._parse_date(date_str)
                    else:
                        published_date = datetime.utcnow().strftime("%Y-%m-%d")
                    
                    # Fetch article content
                    content = self._fetch_article_content(url, config)
                    
                    results.append({
                        "source": source_domain,
                        "title": title,
                        "url": url,
                        "published_date": published_date,
                        "content": content,
                    })
                    
                except Exception as e:
                    continue
                    
        except requests.RequestException as e:
            print(f"    Request failed for {source_domain}: {e}")
        
        return results
    
    def _fetch_article_content(self, url: str, config: Dict) -> str:
        """Fetch and extract article content."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Try to find article content
            content_elems = soup.select(config["content_selector"])
            if content_elems:
                content = " ".join([p.get_text(strip=True) for p in content_elems])
            else:
                # Fallback: get all paragraph text
                paragraphs = soup.find_all("p")
                content = " ".join([p.get_text(strip=True) for p in paragraphs[:10]])
            
            # Clean up content
            content = re.sub(r'\s+', ' ', content).strip()
            return content[:3000]  # Truncate to 3000 chars
            
        except Exception as e:
            return ""
    
    def _parse_date(self, date_str: str) -> str:
        """Parse various date formats to YYYY-MM-DD."""
        if not date_str:
            return datetime.utcnow().strftime("%Y-%m-%d")
        
        # Try ISO format first
        try:
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%d",
            "%B %d, %Y",
            "%b %d, %Y",
            "%d %B %Y",
            "%d %b %Y",
            "%m/%d/%Y",
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # Fallback to today
        return datetime.utcnow().strftime("%Y-%m-%d")
    
    def search_google_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """
        Search Google News as a fallback/supplement.
        Note: This is for research purposes and should respect robots.txt.
        """
        results = []
        
        # Google News RSS feed
        rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        
        try:
            response = self.session.get(rss_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "xml")
            
            items = soup.find_all("item")[:15]
            cutoff = datetime.utcnow() - timedelta(days=days_back)
            
            for item in items:
                try:
                    title = item.find("title").get_text(strip=True)
                    link = item.find("link").get_text(strip=True)
                    pub_date_str = item.find("pubDate").get_text(strip=True)
                    
                    # Parse date
                    pub_date = datetime.strptime(
                        pub_date_str, 
                        "%a, %d %b %Y %H:%M:%S %Z"
                    )
                    
                    if pub_date < cutoff:
                        continue
                    
                    # Extract source from title (Google News format: "Title - Source")
                    source = "google_news"
                    if " - " in title:
                        parts = title.rsplit(" - ", 1)
                        if len(parts) == 2:
                            title, source = parts
                    
                    results.append({
                        "source": source,
                        "title": title,
                        "url": link,
                        "published_date": pub_date.strftime("%Y-%m-%d"),
                        "content": "",  # Would need to fetch
                    })
                    
                except Exception:
                    continue
                    
        except Exception as e:
            print(f"    Google News search failed: {e}")
        
        return results


class SECScraper:
    """Scraper for SEC EDGAR filings."""
    
    def __init__(self):
        """Initialize SEC scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "NXT Research Agent research@velocityxp.com",
            "Accept": "application/json",
        })
        self.base_url = "https://efts.sec.gov/LATEST/search-index"
        self.filing_base = "https://www.sec.gov/cgi-bin/browse-edgar"
    
    def search(self, ticker: str, days_back: int = 7, 
               filing_types: List[str] = None) -> List[Dict]:
        """
        Search for recent SEC filings.
        
        Args:
            ticker: Company stock ticker
            days_back: Days to look back
            filing_types: List of filing types (default: 10-K, 10-Q, 8-K)
            
        Returns:
            List of filing dictionaries
        """
        if filing_types is None:
            filing_types = ["10-K", "10-Q", "8-K"]
        
        results = []
        start_date = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        
        for filing_type in filing_types:
            try:
                # Use SEC EDGAR full-text search
                search_url = (
                    f"https://efts.sec.gov/LATEST/search-index?"
                    f"q={ticker}&dateRange=custom&startdt={start_date}"
                    f"&forms={filing_type}"
                )
                
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    hits = data.get("hits", {}).get("hits", [])
                    
                    for hit in hits[:5]:  # Limit to 5 per type
                        source = hit.get("_source", {})
                        results.append({
                            "filing_type": filing_type,
                            "company": source.get("display_names", [ticker])[0],
                            "filing_date": source.get("file_date", ""),
                            "url": f"https://www.sec.gov/Archives/edgar/data/{source.get('ciks', [''])[0]}",
                            "excerpt": source.get("text", "")[:1000],
                        })
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"    SEC search failed for {ticker} {filing_type}: {e}")
                continue
        
        return results


class CHIPSScraper:
    """Scraper for CHIPS Act award status."""
    
    def __init__(self):
        """Initialize CHIPS scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        # Commerce Department CHIPS page
        self.chips_url = "https://www.nist.gov/chips"
    
    def check_status(self, project_id: str) -> List[Dict]:
        """
        Check CHIPS Act status for a project.
        
        Note: This is a placeholder. The actual implementation would need
        to be customized based on how Commerce publishes updates.
        """
        results = []
        
        try:
            # Check main CHIPS page for updates
            response = self.session.get(self.chips_url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Look for news/updates section
            news_items = soup.select("div.news-item, article.update")
            
            for item in news_items[:5]:
                title = item.get_text(strip=True)[:200]
                results.append({
                    "url": self.chips_url,
                    "update_date": datetime.utcnow().strftime("%Y-%m-%d"),
                    "status_text": title,
                })
                
        except Exception as e:
            print(f"    CHIPS status check failed: {e}")
        
        return results


class GridQueueScraper:
    """Scraper for grid interconnection queue data."""
    
    def __init__(self):
        """Initialize grid queue scraper."""
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })
        
        # Grid operator queue URLs
        self.queue_urls = {
            "PJM": "https://www.pjm.com/planning/services-requests/interconnection-queues",
            "ERCOT": "https://www.ercot.com/gridinfo/resource",
            "CAISO": "https://www.caiso.com/planning/Pages/GeneratorInterconnection/Default.aspx",
            "MISO": "https://www.misoenergy.org/planning/generator-interconnection/GI_Queue/",
            "NYISO": "https://www.nyiso.com/interconnections",
            "SPP": "https://www.spp.org/engineering/generator-interconnection/",
            "TVA": "https://www.tva.com/energy/transmission-system/transmission-system-planning",
        }
    
    def check_position(self, operator: str, interconnection_id: str) -> List[Dict]:
        """
        Check interconnection queue position.
        
        Note: Actual implementation would parse operator-specific data formats.
        Many operators provide downloadable Excel/CSV files.
        """
        results = []
        
        if operator not in self.queue_urls:
            return results
        
        try:
            url = self.queue_urls[operator]
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            # This is a placeholder - actual implementation would
            # download and parse the queue data file
            results.append({
                "url": url,
                "data_date": datetime.utcnow().strftime("%Y-%m-%d"),
                "status_text": f"Queue data retrieved from {operator}",
            })
            
        except Exception as e:
            print(f"    Grid queue check failed for {operator}: {e}")
        
        return results


if __name__ == "__main__":
    # Test the scrapers
    news = NewsScraper()
    results = news.search("TSMC Arizona", days_back=7)
    print(f"Found {len(results)} news articles")
    for r in results[:3]:
        print(f"  - {r['title'][:60]}... ({r['source']})")
