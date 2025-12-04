"""
Integrated Job Scrapers
Uses BOTH direct site scraping AND Google Search for comprehensive coverage
"""

import os
from dotenv import load_dotenv
from universal_scraper import UniversalJobScraper, scrape_all_sites
import requests

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


def find_all_industry_jobs():
    """
    Find industry ML jobs using BOTH methods:
    1. Direct scraping of configured sites
    2. Google Search as supplement
    """
    
    print("\n" + "="*60)
    print("💼 INDUSTRY JOB SEARCH")
    print("="*60 + "\n")
    
    all_jobs = []
    
    # METHOD 1: Direct site scraping
    print("📍 METHOD 1: Direct Site Scraping")
    print("-" * 60)
    
    try:
        scraped_jobs = scrape_all_sites()
        all_jobs.extend(scraped_jobs)
        print(f"✅ Found {len(scraped_jobs)} jobs from direct scraping\n")
    except Exception as e:
        print(f"❌ Scraping error: {e}\n")
    
    # METHOD 2: Google Search (supplement)
    print("📍 METHOD 2: Google Search (Supplement)")
    print("-" * 60)
    
    try:
        google_jobs = search_google_industry_jobs()
        all_jobs.extend(google_jobs)
        print(f"✅ Found {len(google_jobs)} jobs from Google Search\n")
    except Exception as e:
        print(f"❌ Google Search error: {e}\n")
    
    # Deduplicate by URL
    seen_urls = set()
    unique_jobs = []
    
    for job in all_jobs:
        if job['url'] not in seen_urls:
            seen_urls.add(job['url'])
            unique_jobs.append(job)
    
    print("=" * 60)
    print(f"✅ Total unique industry jobs: {len(unique_jobs)}")
    print("=" * 60 + "\n")
    
    return unique_jobs


def find_all_phd_positions():
    """
    Find PhD positions using BOTH methods:
    1. Direct scraping of PhD sources
    2. Google Search as supplement
    """
    
    print("\n" + "="*60)
    print("🎓 PHD POSITION SEARCH")
    print("="*60 + "\n")
    
    all_positions = []
    
    # METHOD 1: Direct scraping of PhD sources
    print("📍 METHOD 1: Direct PhD Site Scraping")
    print("-" * 60)
    
    try:
        scraper = UniversalJobScraper()
        
        # Scrape PhD-specific sources
        if 'phd_sources' in scraper.config:
            for source in scraper.config['phd_sources']:
                positions = scraper.scrape_site(source['name'], source['url'])
                all_positions.extend(positions)
        
        print(f"✅ Found {len(all_positions)} positions from direct scraping\n")
    except Exception as e:
        print(f"❌ Scraping error: {e}\n")
    
    # METHOD 2: Google Search
    print("📍 METHOD 2: Google Search (Supplement)")
    print("-" * 60)
    
    try:
        google_positions = search_google_phd_positions()
        all_positions.extend(google_positions)
        print(f"✅ Found {len(google_positions)} positions from Google Search\n")
    except Exception as e:
        print(f"❌ Google Search error: {e}\n")
    
    # Deduplicate
    seen_urls = set()
    unique_positions = []
    
    for pos in all_positions:
        if pos['url'] not in seen_urls:
            seen_urls.add(pos['url'])
            unique_positions.append(pos)
    
    print("=" * 60)
    print(f"✅ Total unique PhD positions: {len(unique_positions)}")
    print("=" * 60 + "\n")
    
    return unique_positions


def search_google_industry_jobs():
    """Google Search for industry jobs (supplement to scraping)"""
    
    queries = [
        "machine learning engineer jobs UK site:linkedin.com",
        "ML engineer UK site:indeed.co.uk",
        "research scientist AI UK",
        "computer vision engineer London UK",
    ]
    
    all_jobs = []
    
    for query in queries:
        print(f"   🔍 {query[:50]}...")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": 10
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                
                for item in results.get("items", []):
                    job = {
                        "title": item.get("title", ""),
                        "company": extract_company_from_url(item.get("link", "")),
                        "location": "UK",
                        "city": "",
                        "description": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "source": "Google Search",
                        "salary": "Not specified",
                        "post_date": "Recent",
                        "deadline": "Not specified",
                        "requirements": [],
                        "expectations": [],
                        "cv_required": "Not specified",
                        "cover_letter_required": "Not specified",
                    }
                    all_jobs.append(job)
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return all_jobs


def search_google_phd_positions():
    """Google Search for PhD positions (supplement to scraping)"""
    
    queries = [
        "PhD machine learning UK funded 2025",
        "PhD computer vision UK studentship",
        "EPSRC PhD machine learning UK",
    ]
    
    all_positions = []
    
    for query in queries:
        print(f"   🔍 {query[:50]}...")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": GOOGLE_CSE_ID,
            "q": query,
            "num": 10
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                results = response.json()
                
                for item in results.get("items", []):
                    position = {
                        "title": item.get("title", ""),
                        "company": extract_company_from_url(item.get("link", "")),
                        "location": "UK",
                        "city": "",
                        "description": item.get("snippet", ""),
                        "url": item.get("link", ""),
                        "source": "Google Search",
                        "salary": "Check listing",
                        "post_date": "Recent",
                        "deadline": "Not specified",
                        "requirements": [],
                        "expectations": [],
                        "cv_required": "Not specified",
                        "cover_letter_required": "Not specified",
                    }
                    all_positions.append(position)
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    return all_positions


def extract_company_from_url(url):
    """Extract company name from URL"""
    
    company_map = {
        "linkedin.com": "LinkedIn Job",
        "indeed.co.uk": "Indeed Listing",
        "glassdoor.co.uk": "Glassdoor Listing",
        "deepmind.com": "Google DeepMind",
        "google.com": "Google",
        "microsoft.com": "Microsoft",
        "amazon": "Amazon",
        "meta.com": "Meta",
        "anthropic.com": "Anthropic",
        "openai.com": "OpenAI",
        "jobs.ac.uk": "Jobs.ac.uk",
        "cam.ac.uk": "University of Cambridge",
        "ox.ac.uk": "University of Oxford",
        "imperial.ac.uk": "Imperial College London",
        "ucl.ac.uk": "UCL",
        "kcl.ac.uk": "King's College London",
        "ed.ac.uk": "University of Edinburgh",
    }
    
    for key, name in company_map.items():
        if key in url.lower():
            return name
    
    try:
        domain = url.split("//")[1].split("/")[0]
        domain = domain.replace("www.", "")
        return domain.split(".")[0].title()
    except:
        return "Unknown"


if __name__ == "__main__":
    # Test integrated scraping
    print("Testing integrated job search...\n")
    
    jobs = find_all_industry_jobs()
    
    print(f"\n{'='*60}")
    print(f"Sample Results:")
    print(f"{'='*60}\n")
    
    for i, job in enumerate(jobs[:5], 1):
        print(f"{i}. {job['title']}")
        print(f"   Company: {job['company']}")
        print(f"   Location: {job.get('city', job['location'])}")
        print(f"   Source: {job.get('source', 'Unknown')}")
        print(f"   URL: {job['url'][:60]}...")
        print()