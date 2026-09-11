"""
FAIDA: Financial Adversarial Indian Data Agents
Module: backend.scrapers.web_search_client
Description:
    Deep Web Search & Real-Time Financial News Context Ingestion Client.
    
    Provides targeted, query-aware intelligence by querying live news and web feeds
    specifically aligned with the user's investment hypothesis and topical keywords
    (e.g., crude volatility, commercial vehicle expansion, dividend yield safety,
    promoter selling, regulatory notices).
    
    Data Feeds:
        1. Google News RSS (India Region): Live, free, zero-key, query-targeted news.
        2. Yahoo Finance News: Company-level institutional news stream.
        3. Finnhub API: International coverage and ADR developments (when key is present).
"""

import re
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import httpx
import logging

from backend.scrapers.yfinance_client import YFinanceClient
from backend.scrapers.finnhub_client import FinnhubClient

logger = logging.getLogger("faida.scrapers.web_search")

STOP_WORDS = {
    "THE", "AND", "FOR", "THAT", "THIS", "WITH", "FROM", "HAVE", "ARE", "WAS", "WERE",
    "BUY", "SELL", "HOLD", "WANT", "THINKING", "LOOKING", "SHOULD", "STOCK", "SHARE",
    "PRICE", "TARGET", "RUPEES", "TODAY", "BECAUSE", "SINCE", "ABOUT", "SOME", "MANY",
    "VERY", "WOULD", "COULD", "WILL", "PLANNING", "EXPECTING", "LEVEL", "LEVELS", "INR", "RS"
}


class WebSearchClient:
    """
    Executes query-aware web and news intelligence gathering for Indian equities.
    Connects investor thesis arguments to real-time market facts.
    """

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "application/rss+xml, application/xml, text/xml, */*",
    }

    @classmethod
    def extract_query_keywords(cls, query_text: Optional[str], symbol: str = "") -> List[str]:
        """Extracts significant topical keywords from the user's input."""
        if not query_text:
            return []
        
        # Remove currency symbols and numbers
        cleaned = re.sub(r"[₹$€£\d,.]+", " ", query_text)
        words = re.findall(r"\b[A-Za-z]{3,}\b", cleaned)
        
        symbol_upper = symbol.strip().upper()
        keywords = [
            w.lower() for w in words
            if w.upper() not in STOP_WORDS and w.upper() != symbol_upper
        ]
        return keywords[:5]

    @classmethod
    def search_query_context(
        cls,
        symbol: str,
        company_name: Optional[str] = None,
        user_query: Optional[str] = None,
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Gathers live news and web intelligence matching the user's specific hypothesis.
        """
        clean_symbol = symbol.strip().upper().replace(".NS", "").replace(".BO", "")
        keywords = cls.extract_query_keywords(user_query, symbol=clean_symbol)
        
        articles: List[Dict[str, Any]] = []

        # 1. Google News RSS Query (Query-Specific & Company-Specific)
        search_terms = [clean_symbol]
        if company_name and len(company_name) > 2 and company_name.upper() != clean_symbol:
            # Use concise company name
            short_name = company_name.split()[0]
            search_terms.append(short_name)
        if keywords:
            search_terms.extend(keywords[:3])

        query_str = " ".join(search_terms)
        rss_articles = cls._fetch_google_news_rss(query_str, limit=limit + 2)
        articles.extend(rss_articles)

        # 2. Fallback to General Company News if query was too narrow or returned 0
        if len(articles) < 2:
            general_query = f"{company_name or clean_symbol} share news"
            articles.extend(cls._fetch_google_news_rss(general_query, limit=3))

        # 3. Yahoo Finance News Feed Integration
        yf_news = cls._fetch_yfinance_news(clean_symbol, limit=3)
        articles.extend(yf_news)

        # 4. Finnhub News (if API key available)
        finnhub_news = FinnhubClient.get_company_news(clean_symbol)
        for fn in finnhub_news[:2]:
            articles.append({
                "title": fn.get("headline", ""),
                "source": f"Finnhub ({fn.get('source', 'Global')})",
                "snippet": fn.get("summary", "")[:240],
                "link": fn.get("url", ""),
                "published": fn.get("datetime", ""),
                "is_query_matched": False
            })

        # 5. Deduplicate and Score by Query Keyword Match
        return cls._rank_and_deduplicate(articles, keywords, limit=limit)

    @classmethod
    def _fetch_google_news_rss(cls, query: str, limit: int = 4) -> List[Dict[str, Any]]:
        encoded_query = urllib.parse.quote(query.strip())
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        results = []

        try:
            with httpx.Client(headers=cls.HEADERS, timeout=4.5, follow_redirects=True) as client:
                resp = client.get(url)
                if resp.status_code == 200 and resp.text:
                    root = ET.fromstring(resp.text)
                    items = root.findall(".//item")
                    for it in items[:limit]:
                        title_elem = it.find("title")
                        source_elem = it.find("source")
                        desc_elem = it.find("description")
                        link_elem = it.find("link")
                        pub_elem = it.find("pubDate")

                        title = title_elem.text.strip() if title_elem is not None and title_elem.text else ""
                        source = source_elem.text.strip() if source_elem is not None and source_elem.text else "Google News"
                        desc = desc_elem.text.strip() if desc_elem is not None and desc_elem.text else ""
                        link = link_elem.text.strip() if link_elem is not None and link_elem.text else ""
                        pub = pub_elem.text.strip() if pub_elem is not None and pub_elem.text else ""

                        # Clean HTML from description
                        clean_desc = re.sub(r"<[^>]+>", " ", desc).strip()
                        clean_desc = re.sub(r"\s+", " ", clean_desc)

                        if title:
                            results.append({
                                "title": title,
                                "source": source,
                                "snippet": clean_desc[:260],
                                "link": link,
                                "published": pub,
                                "is_query_matched": False
                            })
        except Exception as e:
            logger.debug(f"Google News RSS fetch error for '{query}': {e}")

        return results

    @classmethod
    def _fetch_yfinance_news(cls, symbol: str, limit: int = 3) -> List[Dict[str, Any]]:
        results = []
        try:
            import yfinance as yf
            ticker_str = f"{symbol}.NS"
            t = yf.Ticker(ticker_str)
            raw_news = getattr(t, "news", None) or []
            for item in raw_news[:limit]:
                # Handle both yfinance format variations
                content = item.get("content") if isinstance(item, dict) else None
                if content and isinstance(content, dict):
                    title = content.get("title", "")
                    provider = content.get("provider", {})
                    source = provider.get("displayName", "Yahoo Finance") if isinstance(provider, dict) else "Yahoo Finance"
                    snippet = content.get("summary", "") or content.get("description", "")
                    link = (content.get("clickThroughUrl") or {}).get("url", "")
                    pub = content.get("pubDate", "")
                elif isinstance(item, dict):
                    title = item.get("title", "")
                    source = item.get("publisher", "Yahoo Finance")
                    snippet = item.get("summary", "")
                    link = item.get("link", "")
                    pub = item.get("providerPublishTime", "")
                else:
                    continue

                if title:
                    results.append({
                        "title": title,
                        "source": source,
                        "snippet": snippet[:260],
                        "link": link,
                        "published": str(pub),
                        "is_query_matched": False
                    })
        except Exception as e:
            logger.debug(f"YFinance news fetch error for {symbol}: {e}")

        return results

    @classmethod
    def _rank_and_deduplicate(
        cls,
        articles: List[Dict[str, Any]],
        keywords: List[str],
        limit: int = 4
    ) -> List[Dict[str, Any]]:
        seen_titles = set()
        ranked: List[Dict[str, Any]] = []

        for a in articles:
            title = a.get("title", "").strip()
            if not title:
                continue
            
            # Simple deduplication key
            norm_key = re.sub(r"[^\w\s]", "", title.lower())[:60]
            if norm_key in seen_titles:
                continue
            seen_titles.add(norm_key)

            # Score keyword match
            text_to_check = f"{title} {a.get('snippet', '')}".lower()
            matches = sum(1 for kw in keywords if kw in text_to_check)
            a["is_query_matched"] = matches > 0
            a["match_score"] = matches
            ranked.append(a)

        # Sort: query keyword matches first, then order of arrival
        ranked.sort(key=lambda x: x.get("match_score", 0), reverse=True)
        return ranked[:limit]
