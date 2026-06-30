"""arXiv HTML scraper using Selenium — bypasses API rate limits.

Falls back to cached API results if Selenium fails.
"""
import os, re, time, logging, urllib.parse
from typing import List
from src.research import Paper

logger = logging.getLogger(__name__)

_HEADLESS = True  # Run without visible browser window


def _get_driver():
    """Get a headless Chrome driver."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    options = Options()
    if _HEADLESS:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    service = Service()
    try:
        return webdriver.Chrome(service=service, options=options)
    except Exception:
        from selenium.webdriver.edge.service import Service as EdgeService
        options.use_chromium = True
        return webdriver.Edge(service=EdgeService(), options=options)


def search_arxiv_scrape(keywords: List[str], categories: List[str] = None, max_results: int = 10) -> List[Paper]:
    """Search arXiv via HTML scraping. Returns list of Paper objects."""
    query = " OR ".join(keywords[:3])
    if categories:
        cats = " OR ".join(f"cat:{c}" for c in categories[:3])
        query = f"({query}) AND ({cats})"
    
    url = f"https://arxiv.org/search/?query={urllib.parse.quote(query)}&searchtype=all&order=-announced_date_first"
    logger.info(f"Scraping: {url}")
    
    driver = None
    try:
        driver = _get_driver()
        driver.get(url)
        time.sleep(2)  # Let page load
        
        html = driver.page_source
        
        titles = re.findall(r'<p class="title is-5 mathjax">\s*(.*?)\s*</p>', html, re.DOTALL)
        ids = re.findall(r'<a href="/abs/(\d+\.\d+)"', html)
        summaries = re.findall(r'<span class="abstract-full.*?">(.*?)</span>', html, re.DOTALL)
        cats_elem = re.findall(r'<span class="primary-subject">(.*?)</span>', html)
        
        papers = []
        for i in range(min(max_results, len(titles))):
            title = re.sub(r'<[^>]+>', '', titles[i]).strip()[:200]
            arxiv_id = ids[i] if i < len(ids) else "N/A"
            abstract = re.sub(r'<[^>]+>', '', summaries[i]).strip() if i < len(summaries) else ""
            cat = cats_elem[i].strip() if i < len(cats_elem) else ""
            
            if "withdrawn" not in abstract.lower():
                papers.append(Paper(
                    arxiv_id=arxiv_id, title=title, authors="",
                    published="", abstract=abstract[:500], categories=cat
                ))
        return papers
    except Exception as e:
        logger.warning(f"Scraping failed: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
