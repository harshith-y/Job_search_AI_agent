"""
Consolidated Scrapers
All scraping and searching functionality in one place
"""

import requests
from bs4 import BeautifulSoup
import yaml
import time
import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


# ============================================================================
# CONFIG LOADING
# ============================================================================

def load_config():
    """Load job sites from config.yaml"""
    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        easy_sites = config.get("easy_sites", [])
        medium_sites = config.get("medium_sites", [])
        hard_sites = config.get("hard_sites", [])
        
        return easy_sites, medium_sites, hard_sites
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return [], [], []


# ============================================================================
# INDUSTRY JOB SCRAPING
# ============================================================================

def scrape_jobs_ac_uk(keywords="machine learning", max_results=20):
    """Scrape jobs.ac.uk for ML/AI jobs"""
    print(f"🔍 Scraping jobs.ac.uk...")
    
    base_url = "https://www.jobs.ac.uk"
    search_url = f"{base_url}/search/"
    
    params = {
        'keywords': keywords,
        'location': 'UK',
        'sort': 'date'
    }
    
    jobs = []
    
    try:
        response = requests.get(search_url, params=params, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        job_cards = soup.find_all("li", class_="job-result")
        if not job_cards:
            job_cards = soup.find_all("article", class_="job")
        
        for card in job_cards[:max_results]:
            try:
                title_tag = card.find("h3") or card.find("h2")
                link_tag = card.find("a")
                
                if not title_tag or not link_tag:
                    continue
                
                title = title_tag.text.strip()
                url = link_tag.get("href")
                
                if url and not url.startswith("http"):
                    url = base_url + url
                
                company_tag = card.find("span", class_="company") or card.find("p", class_="employer")
                company = company_tag.text.strip() if company_tag else "Unknown"
                
                location_tag = card.find("span", class_="location")
                location = location_tag.text.strip() if location_tag else "UK"
                
                desc_tag = card.find("p", class_="description") or card.find("div", class_="snippet")
                description = desc_tag.text.strip() if desc_tag else "See job posting for details"
                
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": url,
                    "description": description,
                    "job_type": "Industry",
                    "source": "jobs.ac.uk"
                })
                
            except Exception as e:
                continue
        
        print(f"✅ Found {len(jobs)} jobs on jobs.ac.uk")
        return jobs
        
    except Exception as e:
        print(f"❌ Error scraping jobs.ac.uk: {e}")
        return []


def scrape_industry_jobs():
    """Scrape all configured industry job sites"""
    easy_sites, _, _ = load_config()
    
    all_jobs = []
    
    for site in easy_sites:
        site_name = site.get("name", "Unknown")
        
        if "jobs.ac.uk" in site_name.lower():
            jobs = scrape_jobs_ac_uk()
            all_jobs.extend(jobs)
        else:
            print(f"⚠️  Scraper not implemented for: {site_name}")
    
    return all_jobs


# ============================================================================
# GOOGLE SEARCH (INDUSTRY)
# ============================================================================

def search_google_industry_jobs():
    """Search Google for industry ML/AI jobs"""
    
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("⚠️  Google API not configured - skipping search")
        return []
    
    queries = [
        "machine learning engineer UK jobs",
        "AI researcher position UK"
    ]
    
    all_jobs = []
    
    for query in queries:
        results = search_google(query, num_results=10)
        for result in results:
            result["job_type"] = "Industry"
            result["source"] = f"Google: {query}"
        all_jobs.extend(results)
    
    return all_jobs


# ============================================================================
# PHD POSITION SEARCHING (GOOGLE ONLY - FindAPhD blocked)
# ============================================================================

def search_google_phd_positions():
    """Search Google for PhD positions"""
    
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("⚠️  Google API not configured - skipping search")
        return []
    
    print(f"🌐 Searching Google for PhD positions...")
    
    queries = [
        "machine learning PhD UK 2025 funded",
        "artificial intelligence PhD studentship UK",
        "computer vision PhD EPSRC funded",
        "NLP PhD Cambridge Oxford Imperial",
        "deep learning PhD position UK"
    ]
    
    all_positions = []
    
    for i, query in enumerate(queries, 1):
        print(f"  🔍 [{i}/{len(queries)}] '{query}'")
        results = search_google(query, num_results=10, days_ago=30)
        for result in results:
            result["job_type"] = "PhD"
            result["source"] = f"Google: {query}"
            result["funding"] = "Check website"
            result["deadline"] = "Check website"
        all_positions.extend(results)
        time.sleep(1)
    
    print(f"✅ Found {len(all_positions)} PhD positions via Google")
    
    # Deduplicate
    seen_urls = set()
    unique = []
    for pos in all_positions:
        if pos['url'] not in seen_urls:
            seen_urls.add(pos['url'])
            unique.append(pos)
    
    print(f"✅ {len(unique)} unique positions after deduplication")
    
    return unique


# ============================================================================
# GOOGLE SEARCH (GENERIC)
# ============================================================================

def search_google(query, num_results=10, days_ago=7):
    """Generic Google search function"""
    
    base_url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': GOOGLE_API_KEY,
        'cx': GOOGLE_CSE_ID,
        'q': query,
        'num': num_results,
        'dateRestrict': f'd{days_ago}'
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        if 'items' in data:
            for item in data['items']:
                results.append({
                    'title': item.get('title', ''),
                    'url': item.get('link', ''),
                    'company': item.get('displayLink', ''),
                    'location': 'UK',
                    'description': item.get('snippet', ''),
                })
        
        return results
    
    except Exception as e:
        print(f"  ⚠️  Search error: {e}")
        return []


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def find_all_industry_jobs():
    """Find industry jobs using both scraping and search"""
    jobs = scrape_industry_jobs()
    
    if GOOGLE_API_KEY:
        searched = search_google_industry_jobs()
        jobs.extend(searched)
    
    return jobs


def find_all_phd_positions():
    """Find PhD positions using Google search"""
    return search_google_phd_positions()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("="*60)
    print("SCRAPER TEST")
    print("="*60)
    print()
    
    # Test industry scraping
    print("Testing industry job scraping...")
    industry = find_all_industry_jobs()
    print(f"\n✅ Found {len(industry)} industry jobs\n")
    
    # Test PhD search
    print("Testing PhD position search...")
    phds = find_all_phd_positions()
    print(f"\n✅ Found {len(phds)} PhD positions\n")