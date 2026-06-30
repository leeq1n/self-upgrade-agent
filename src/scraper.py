"""arXiv/Web scraper using Selenium — primary tool for dynamic sites, API fallback.

[STABLE v1.3.0] — Selenium-based scraping for Papers With Code, GitHub Trending,
and arXiv HTML search. Falls back gracefully when browser is unavailable.

Capabilities:
  - search_arxiv_scrape()       — arXiv HTML search (API fallback)
  - scrape_pwc_trending()       — Papers With Code trending papers
  - scrape_github_trending()    — GitHub weekly trending repos
  - check_selenium_available()  — Health check for browser availability
"""
import os, re, time, logging, urllib.parse
from typing import List, Dict, Optional

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


def scrape_pwc_trending(max_results: int = 10) -> List[Dict]:
    """Scrape Papers With Code trending page using Selenium.

    Uses browser automation to extract paper cards with titles and arXiv IDs,
    which is more robust than regex-based HTML parsing for JavaScript-rendered pages.

    Args:
        max_results: Maximum number of papers to return.

    Returns:
        List of dicts with keys: title, arxiv_id, url, abstract.
        Returns empty list on any error (graceful degradation).
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    driver = None
    try:
        driver = _get_driver()
        driver.get("https://paperswithcode.com/")
        time.sleep(3)  # Wait for JS rendering

        # Find paper cards
        cards = driver.find_elements(By.CSS_SELECTOR, ".paper-card, [class*='paper-card'], article")
        papers = []

        for card in cards[:max_results * 2]:  # Fetch extra to filter
            try:
                # Title
                try:
                    title_el = card.find_element(By.CSS_SELECTOR, "h1 a, h2 a")
                    title = title_el.text.strip()
                except Exception:
                    continue  # Skip cards without recognizable title

                if not title:
                    continue

                # arXiv ID: search all links in the card
                arxiv_id = None
                links = card.find_elements(By.TAG_NAME, "a")
                for link in links:
                    try:
                        href = link.get_attribute("href") or ""
                        match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})', href)
                        if match:
                            arxiv_id = match.group(1)
                            break
                    except Exception:
                        continue

                # Abstract snippet
                abstract = ""
                try:
                    abstract_el = card.find_element(By.CSS_SELECTOR, ".paper-abstract, p")
                    abstract = abstract_el.text.strip()[:200]
                except Exception:
                    pass

                url = ""
                try:
                    url_el = card.find_element(By.CSS_SELECTOR, "a[href*='/paper/']")
                    url = url_el.get_attribute("href") or ""
                except Exception:
                    pass

                papers.append({
                    "title": title,
                    "arxiv_id": arxiv_id,
                    "url": url,
                    "abstract": abstract,
                })

                if len(papers) >= max_results:
                    break

            except Exception:
                continue

        logger.info(f"Selenium PwC: {len(papers)} papers scraped")
        return papers

    except Exception as e:
        logger.debug(f"Selenium PwC failed: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def scrape_github_trending(language: str = "python") -> List[Dict]:
    """Scrape GitHub trending page using Selenium.

    Args:
        language: Programming language to filter (default: python).

    Returns:
        List of dicts with keys: name, description, language, url, stars_today.
        Returns empty list on any error.
    """
    from selenium.webdriver.common.by import By

    driver = None
    try:
        driver = _get_driver()
        driver.get(f"https://github.com/trending/{language}?since=weekly")
        time.sleep(3)  # Wait for JS rendering

        # Each repo is an article.Box-row
        articles = driver.find_elements(By.CSS_SELECTOR, "article.Box-row")
        repos = []

        for article in articles[:30]:
            try:
                # Name: h2 > a
                name_el = article.find_element(By.CSS_SELECTOR, "h2 a")
                href = name_el.get_attribute("href") or ""
                name = href.strip("/").replace("https://github.com/", "") if href else ""

                # Description: first p
                desc = ""
                try:
                    desc_el = article.find_element(By.CSS_SELECTOR, "p")
                    desc = desc_el.text.strip()[:200]
                except Exception:
                    pass

                # Language
                lang = ""
                try:
                    lang_el = article.find_element(By.CSS_SELECTOR, '[itemprop="programmingLanguage"]')
                    lang = lang_el.text.strip()
                except Exception:
                    pass

                # Stars today
                stars = ""
                try:
                    stars_el = article.find_element(By.CSS_SELECTOR, ".d-inline-block.float-sm-right")
                    stars = stars_el.text.strip()
                except Exception:
                    pass

                if name:
                    repos.append({
                        "name": name,
                        "description": desc,
                        "language": lang,
                        "url": f"https://github.com/{name}" if not href else href,
                        "stars_today": stars,
                    })

            except Exception:
                continue

        logger.info(f"Selenium GitHub trending: {len(repos)} repos")
        return repos

    except Exception as e:
        logger.debug(f"Selenium GitHub failed: {e}")
        return []
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass


def check_selenium_available() -> bool:
    """Quick health check: can we start and stop a headless browser?

    Returns True if Selenium + Chrome/Edge is available, False otherwise.
    Use this before scheduling Selenium-dependent tasks.
    """
    try:
        driver = _get_driver()
        driver.quit()
        return True
    except Exception as e:
        logger.debug(f"Selenium not available: {e}")
        return False
