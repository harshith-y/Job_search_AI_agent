"""
Integrated Job Scrapers - Google Search Edition
Uses Google Custom Search API for job discovery with:
- Targeted search queries for actual job postings
- URL validation to filter out aggregator/search pages
- Detail fetching from job URLs for richer data
- Quality scoring for better results
- Configurable search preferences
"""

import os
import re
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()


# ============================================================================
# JOB DETAIL FETCHER - Scrape full details from job URLs
# ============================================================================

def fetch_job_details(url, timeout=10):
    """
    Fetch full job details from a URL by scraping the page.

    Extracts:
    - Title, Company, Location
    - Salary information
    - Deadline/closing date
    - Requirements and qualifications
    - Full description

    Returns a dict with extracted fields (empty strings for missing data).
    """
    details = {
        'title': '',
        'company': '',
        'location': '',
        'city': '',
        'salary': 'Not specified',
        'deadline': 'Not specified',
        'requirements': [],
        'expectations': [],
        'description': '',
        'cv_required': 'Not specified',
        'cover_letter_required': 'Not specified',
    }

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
        }

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = soup.get_text(separator=' ', strip=True).lower()

        # === TITLE ===
        # Try common title selectors
        title_selectors = [
            'h1.job-title', 'h1.posting-title', 'h1[class*="title"]',
            '.job-title h1', '.posting-headline h1', 'h1'
        ]
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem and len(elem.get_text(strip=True)) > 5:
                details['title'] = elem.get_text(strip=True)[:200]
                break

        # === COMPANY ===
        company_selectors = [
            '.company-name', '.employer-name', '[class*="company"]',
            '[class*="employer"]', '.organization'
        ]
        for selector in company_selectors:
            elem = soup.select_one(selector)
            if elem and len(elem.get_text(strip=True)) > 1:
                details['company'] = elem.get_text(strip=True)[:100]
                break

        # === LOCATION ===
        location_selectors = [
            '.location', '[class*="location"]', '.job-location',
            '[class*="city"]', '.address'
        ]
        for selector in location_selectors:
            elem = soup.select_one(selector)
            if elem and len(elem.get_text(strip=True)) > 1:
                location_text = elem.get_text(strip=True)[:100]
                details['location'] = location_text
                # Try to extract city
                if ',' in location_text:
                    details['city'] = location_text.split(',')[0].strip()
                break

        # === SALARY ===
        salary_patterns = [
            r'£[\d,]+\s*[-–to]+\s*£[\d,]+',  # £50,000 - £70,000
            r'£[\d,]+\s*(?:pa|per annum|per year|annually)?',  # £50,000 pa
            r'\$[\d,]+\s*[-–to]+\s*\$[\d,]+',  # $50,000 - $70,000
            r'salary[:\s]+£?[\d,]+',  # Salary: £50,000
            r'(?:stipend|funding)[:\s]+£?[\d,]+',  # For PhDs
        ]
        for pattern in salary_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                details['salary'] = match.group(0).strip()
                break

        # === DEADLINE ===
        # More comprehensive deadline patterns
        deadline_patterns = [
            # "Deadline: 15 January 2025" or "Closing date: 15/01/2025"
            r'(?:deadline|closing date|closes?|apply by|applications?\s*close)[:\s]+(\d{1,2}[\s/-]\w+[\s/-]\d{2,4})',
            r'(?:deadline|closing date|closes?|apply by)[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
            # Standalone dates: "15 January 2025"
            r'(\d{1,2}\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})',
            # "January 15, 2025"
            r'((?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2},?\s+\d{4})',
            # ISO format: "2025-01-15"
            r'(?:deadline|closing)[:\s]*(\d{4}-\d{2}-\d{2})',
            # UK format: "15/01/2025" near deadline keywords
            r'(?:deadline|closing|apply by)[:\s]*(\d{1,2}/\d{1,2}/\d{4})',
            # "Applications close on 15th January"
            r'applications?\s+close\s+(?:on\s+)?(\d{1,2}(?:st|nd|rd|th)?\s+\w+(?:\s+\d{4})?)',
        ]
        for pattern in deadline_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                deadline_str = match.group(1).strip() if match.lastindex else match.group(0).strip()
                # Clean up ordinal suffixes
                deadline_str = re.sub(r'(\d+)(?:st|nd|rd|th)', r'\1', deadline_str)
                details['deadline'] = deadline_str
                break

        # === POST DATE (to detect old jobs) ===
        post_date_patterns = [
            r'(?:posted|published|listed)[:\s]+(\d{1,2}[\s/-]\w+[\s/-]\d{2,4})',
            r'(?:posted|published)[:\s]+(\w+\s+\d{1,2},?\s+\d{4})',
            r'(\d+)\s*(?:days?|weeks?|months?)\s+ago',
        ]
        for pattern in post_date_patterns:
            match = re.search(pattern, text_content, re.IGNORECASE)
            if match:
                details['post_date'] = match.group(0).strip()
                break

        # === REQUIREMENTS ===
        # Look for requirement sections
        requirements = []
        req_headers = soup.find_all(['h2', 'h3', 'h4', 'strong', 'b'],
                                     string=re.compile(r'requirement|qualification|experience|skills|criteria', re.I))
        for header in req_headers[:2]:  # Limit to first 2 sections
            # Get the next sibling list or paragraphs
            next_elem = header.find_next(['ul', 'ol'])
            if next_elem:
                items = next_elem.find_all('li')[:8]  # Limit items
                for item in items:
                    text = item.get_text(strip=True)
                    if 5 < len(text) < 200:
                        requirements.append(text)

        if requirements:
            details['requirements'] = requirements[:6]  # Max 6 requirements

        # === DESCRIPTION ===
        # Get main content area
        content_selectors = [
            '.job-description', '.posting-description', '[class*="description"]',
            '.content', 'article', 'main'
        ]
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                desc = elem.get_text(separator=' ', strip=True)
                if len(desc) > 100:
                    details['description'] = desc[:2000]
                    break

        # === CV/COVER LETTER ===
        if any(phrase in text_content for phrase in ['cv required', 'resume required', 'upload cv', 'attach cv']):
            details['cv_required'] = 'Yes'
        if any(phrase in text_content for phrase in ['cover letter required', 'covering letter', 'letter of motivation']):
            details['cover_letter_required'] = 'Yes'

    except requests.RequestException as e:
        # Silently fail - we'll use what we have from Google
        pass
    except Exception as e:
        # Silently fail for parsing errors
        pass

    return details

# Cache file for intermediate results (allows resuming after crashes)
CACHE_FILE = "job_search_cache.json"


def save_cache(jobs, search_type="industry"):
    """Save intermediate results to cache file for crash recovery."""
    try:
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "search_type": search_type,
            "job_count": len(jobs),
            "jobs": jobs
        }
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)
        print(f"   💾 Cached {len(jobs)} jobs for crash recovery")
    except Exception as e:
        print(f"   ⚠️  Could not save cache: {e}")


def load_cache(search_type="industry", max_age_hours=2):
    """Load cached results if available and recent enough."""
    try:
        if not os.path.exists(CACHE_FILE):
            return None

        with open(CACHE_FILE, 'r') as f:
            cache_data = json.load(f)

        # Check if cache is for the right search type
        if cache_data.get("search_type") != search_type:
            return None

        # Check if cache is recent enough
        cache_time = datetime.fromisoformat(cache_data.get("timestamp", "2000-01-01"))
        age_hours = (datetime.now() - cache_time).total_seconds() / 3600

        if age_hours > max_age_hours:
            print(f"   ⏰ Cache is {age_hours:.1f} hours old (max: {max_age_hours}h) - refreshing")
            return None

        jobs = cache_data.get("jobs", [])
        print(f"   ✅ Loaded {len(jobs)} jobs from cache ({age_hours:.1f}h old)")
        return jobs
    except Exception as e:
        print(f"   ⚠️  Could not load cache: {e}")
        return None


def clear_cache():
    """Clear the cache file."""
    try:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
    except Exception:
        pass


# ============================================================================
# DEADLINE VALIDATION - Filter out expired opportunities
# ============================================================================

def parse_deadline(deadline_text):
    """
    Parse a deadline string into a datetime object.
    Returns None if parsing fails.
    """
    if not deadline_text or deadline_text in ['Not specified', 'Not Specified', '', 'N/A']:
        return None

    original_text = deadline_text.strip()
    deadline_lower = deadline_text.lower().strip()

    # Month name mappings for manual parsing
    month_map = {
        'january': 1, 'jan': 1,
        'february': 2, 'feb': 2,
        'march': 3, 'mar': 3,
        'april': 4, 'apr': 4,
        'may': 5,
        'june': 6, 'jun': 6,
        'july': 7, 'jul': 7,
        'august': 8, 'aug': 8,
        'september': 9, 'sep': 9, 'sept': 9,
        'october': 10, 'oct': 10,
        'november': 11, 'nov': 11,
        'december': 12, 'dec': 12,
    }

    # Pattern 1: "31 December 2024" or "31 Dec 2024"
    match = re.search(r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{4})', deadline_lower)
    if match:
        day = int(match.group(1))
        month = month_map.get(match.group(2), 1)
        year = int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass

    # Pattern 2: "December 31, 2024"
    match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\s+(\d{1,2}),?\s+(\d{4})', deadline_lower)
    if match:
        month = month_map.get(match.group(1), 1)
        day = int(match.group(2))
        year = int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass

    # Pattern 3: "31/12/2024" or "31-12-2024" (UK format: DD/MM/YYYY)
    match = re.search(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})', original_text)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        # Validate it's a reasonable date (day <= 31, month <= 12)
        if day <= 31 and month <= 12:
            try:
                return datetime(year, month, day)
            except ValueError:
                pass

    # Pattern 4: "2024-12-31" (ISO format: YYYY-MM-DD)
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', original_text)
    if match:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
        try:
            return datetime(year, month, day)
        except ValueError:
            pass

    # Pattern 5: Just month and day "31 December" - assume next occurrence
    match = re.search(r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december|jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)', deadline_lower)
    if match:
        day = int(match.group(1))
        month = month_map.get(match.group(2), 1)
        year = datetime.now().year
        try:
            parsed = datetime(year, month, day)
            # If date is in the past, assume next year
            if parsed < datetime.now():
                parsed = datetime(year + 1, month, day)
            return parsed
        except ValueError:
            pass

    return None


def is_deadline_expired(deadline_text, grace_days=0):
    """
    Check if a deadline has already passed.

    Args:
        deadline_text: The deadline string to check
        grace_days: Number of days grace period (negative = already passed is OK)

    Returns:
        (is_expired: bool, parsed_deadline: datetime or None)
    """
    if not deadline_text or deadline_text in ['Not specified', 'Not Specified', '', 'N/A']:
        # No deadline specified - don't filter out
        return False, None

    parsed = parse_deadline(deadline_text)

    if parsed is None:
        # Couldn't parse - don't filter out (might still be valid)
        return False, None

    cutoff = datetime.now() - timedelta(days=grace_days)

    if parsed < cutoff:
        return True, parsed
    else:
        return False, parsed


def is_deadline_too_old(deadline_text, max_days_past=7):
    """
    Check if a deadline is more than max_days_past in the past.
    This filters out clearly expired opportunities while allowing some grace.
    """
    expired, parsed = is_deadline_expired(deadline_text, grace_days=max_days_past)
    return expired, parsed

GOOGLE_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")


# ============================================================================
# URL VALIDATION - Detect real job postings vs aggregator/search pages
# ============================================================================

def is_valid_job_url(url, title=""):
    """
    Validate if a URL is likely a real job posting, not an aggregator page.
    Returns (is_valid, reason)
    """
    # Handle None or empty URL
    if not url:
        return False, "No URL provided"

    url_lower = url.lower()
    title_lower = title.lower() if title else ""

    # REJECT: Known aggregator/search URL patterns
    aggregator_patterns = [
        r'/jobs/search',
        r'/jobs\?',
        r'/search\?',
        r'/jobs-list',
        r'/job-search',
        r'/careers/search',
        r'/vacancies\?',
        r'linkedin\.com/jobs/[a-z-]+-jobs$',  # LinkedIn category pages
        r'linkedin\.com/jobs/[a-z-]+-jobs-[a-z]+$',  # LinkedIn location pages
        r'indeed\.com/jobs\?',
        r'indeed\.com/q-',
        r'glassdoor\..*/Job/',  # Glassdoor search pages
        r'totaljobs\.com/jobs/',
        r'reed\.co\.uk/jobs/',
    ]

    for pattern in aggregator_patterns:
        if re.search(pattern, url_lower):
            return False, "Aggregator search page"

    # REJECT: Title patterns that indicate aggregator pages
    aggregator_title_patterns = [
        r'\d{1,3},?\d{3}\+?\s+.*jobs',  # "6,000+ ML jobs"
        r'\d+\s+.*jobs\s+in',            # "500 jobs in London"
        r'jobs\s+in\s+(united kingdom|london|uk|england)',
        r'job openings',
        r'job listings',
        r'search results',
        r'browse.*jobs',
        r'find.*jobs',
    ]

    for pattern in aggregator_title_patterns:
        if re.search(pattern, title_lower):
            return False, "Aggregator title pattern"

    # ACCEPT: Strong indicators of actual job postings
    job_posting_patterns = [
        r'/job/\d+',           # /job/12345
        r'/jobs/\d+',          # /jobs/12345
        r'/position/\d+',
        r'/vacancy/\d+',
        r'/posting/\d+',
        r'/careers/.*apply',
        r'/apply/\d+',
        r'greenhouse\.io/.*job',
        r'lever\.co/',
        r'workable\.com/',
        r'smartrecruiters\.com/',
        r'jobs\.lever\.co/',
        r'boards\.greenhouse\.io/',
        r'apply\.workable\.com/',
        r'jobs\.ac\.uk/job/',
        r'linkedin\.com/jobs/view/',  # LinkedIn specific job view
    ]

    for pattern in job_posting_patterns:
        if re.search(pattern, url_lower):
            return True, "Job posting URL pattern"

    # NEUTRAL: Check for company career pages (generally OK)
    company_career_patterns = [
        r'/careers/',
        r'/jobs/',
        r'/opportunities/',
        r'/vacancies/',
    ]

    # If it's a company career page with a specific path (not just /careers/)
    for pattern in company_career_patterns:
        if re.search(pattern, url_lower):
            # Check if there's more path after the careers section
            match = re.search(pattern + r'.+', url_lower)
            if match:
                return True, "Company career page with specific job"

    # Default: Accept but with lower confidence
    return True, "Default accept"


def is_job_from_past_year(job):
    """
    Check if a job appears to be from a past year (2024 or earlier).
    Returns (is_old, reason) tuple.
    """
    current_year = datetime.now().year
    past_years = [str(y) for y in range(2020, current_year)]  # 2020-2024

    title = (job.get('title') or '').lower()
    description = (job.get('description') or '').lower()
    deadline = (job.get('deadline') or '').lower()
    post_date = (job.get('post_date') or '').lower()

    # Check for past year mentions in key fields
    for year in past_years:
        # Title mentions like "2024 Graduate Scheme"
        if year in title:
            return True, f"Title contains {year}"

        # Deadline in past year
        if year in deadline:
            return True, f"Deadline in {year}"

        # Posted in past year (if explicitly stated)
        if year in post_date and 'posted' not in post_date:
            return True, f"Post date in {year}"

    # Check for specific patterns like "September 2024" in description (first 500 chars)
    desc_start = description[:500]
    for year in past_years:
        # Pattern: month + year in description header area
        month_year_pattern = rf'(january|february|march|april|may|june|july|august|september|october|november|december)\s+{year}'
        if re.search(month_year_pattern, desc_start):
            return True, f"Description mentions {year}"

    return False, None


def is_senior_role(job):
    """
    Check if a job is a senior-level role (not suitable for recent graduates).
    Returns (is_senior, reason) tuple.
    """
    title = (job.get('title') or '').lower()
    description = (job.get('description') or '').lower()
    requirements = job.get('requirements', [])
    req_text = ' '.join([str(r).lower() for r in requirements])

    # STRONG indicators in title - immediate disqualification
    senior_title_keywords = [
        'senior', 'sr.', 'sr ', 'lead', 'principal', 'staff', 'head of',
        'director', 'vp ', 'vice president', 'chief', 'manager', 'team lead'
    ]

    for keyword in senior_title_keywords:
        if keyword in title:
            return True, f"Title contains '{keyword}'"

    # Experience requirements - check for high years
    experience_patterns = [
        r'(\d+)\+?\s*years?\s*(of\s+)?(experience|exp)',
        r'(\d+)\+?\s*years?\s*(in\s+)?(industry|professional)',
        r'minimum\s+(\d+)\s*years?',
        r'at\s+least\s+(\d+)\s*years?',
    ]

    combined_text = f"{description} {req_text}"

    for pattern in experience_patterns:
        matches = re.findall(pattern, combined_text)
        for match in matches:
            years = int(match[0]) if match[0].isdigit() else 0
            if years >= 5:
                return True, f"Requires {years}+ years experience"

    # Check requirements list for senior indicators
    senior_req_phrases = [
        'proven track record', 'extensive experience', 'deep expertise',
        'significant experience', '5+ years', '7+ years', '10+ years',
        'leadership experience', 'management experience', 'phd required'
    ]

    for phrase in senior_req_phrases:
        if phrase in req_text or phrase in description[:1000]:
            return True, f"Requirements mention '{phrase}'"

    return False, None


def calculate_quality_score(job):
    """
    Calculate a quality score for a job posting (0-100).
    Higher score = more likely to be a relevant, real job posting.

    Now includes:
    - Senior role detection (penalized)
    - Past year detection (penalized)
    - Graduate-friendly indicators (boosted)
    """
    score = 50  # Base score

    # Use 'or' to handle both missing keys AND None values
    title = (job.get('title') or '').lower()
    url = (job.get('url') or '').lower()
    description = (job.get('description') or '').lower()
    company = (job.get('company') or '').lower()

    # =====================================================
    # CRITICAL NEGATIVE SIGNALS (check first)
    # =====================================================

    # Check if job is from a past year (2024 or earlier)
    is_old, old_reason = is_job_from_past_year(job)
    if is_old:
        score -= 50  # Heavy penalty for old jobs
        job['_filter_reason'] = old_reason  # Track why for debugging

    # Check if job is senior level
    is_senior, senior_reason = is_senior_role(job)
    if is_senior:
        score -= 40  # Heavy penalty for senior roles
        job['_filter_reason'] = senior_reason

    # =====================================================
    # POSITIVE signals
    # =====================================================

    # Specific job title (not generic)
    if any(word in title for word in ['engineer', 'scientist', 'analyst', 'developer', 'researcher']):
        score += 10

    # Has a real company name (not "LinkedIn Job" or "Indeed Listing")
    if company and company not in ['linkedin job', 'indeed listing', 'glassdoor listing', 'unknown', 'see listing']:
        score += 15

    # URL contains job ID or specific posting indicator
    if re.search(r'/job/\d+|/jobs/\d+|/position/\d+|/view/\d+', url):
        score += 15

    # From known quality job platforms
    quality_domains = ['greenhouse.io', 'lever.co', 'workable.com', 'jobs.ac.uk', 'smartrecruiters']
    if any(domain in url for domain in quality_domains):
        score += 10

    # Has meaningful description
    if len(description) > 100:
        score += 5

    # GRADUATE-FRIENDLY indicators (HIGH priority!)
    graduate_keywords = [
        'graduate scheme', 'graduate programme', 'graduate program',
        'early careers', 'entry level', 'entry-level', 'junior',
        'new graduate', 'recent graduate', 'graduate role',
        'graduate position', 'trainee', 'apprentice', '0-2 years',
        '1-2 years', 'no experience required'
    ]

    if any(phrase in title for phrase in graduate_keywords):
        score += 25  # Big boost for graduate roles in title
    elif any(phrase in description[:500] for phrase in graduate_keywords):
        score += 15  # Smaller boost if in description

    # Healthcare/biomedical indicators (user's interest)
    if any(word in title or word in description[:500]
           for word in ['healthcare', 'medical', 'biomedical', 'clinical', 'health', 'nhs']):
        score += 10

    # Current year indicator (2025) - good sign
    current_year = str(datetime.now().year)
    if current_year in title or current_year in description[:300]:
        score += 10

    # =====================================================
    # OTHER NEGATIVE signals
    # =====================================================

    # Aggregator indicators in title
    if re.search(r'\d{2,},?\d*\+?\s+jobs', title):
        score -= 40

    # Generic company names
    if company in ['linkedin job', 'indeed listing', 'glassdoor listing']:
        score -= 10

    # Very short title (likely not a real job posting)
    if len(title) < 10:
        score -= 15

    # URL is a search page
    if any(pattern in url for pattern in ['/search?', '/jobs?q=', 'job-search']):
        score -= 30

    return max(0, min(100, score))  # Clamp to 0-100


def find_all_industry_jobs():
    """
    Find industry ML jobs using Google Custom Search API.

    Features:
    - URL validation to filter aggregator pages
    - Deadline validation to filter expired jobs
    - Quality scoring to prioritize best matches
    """

    print("\n" + "="*60)
    print("💼 INDUSTRY JOB SEARCH (ENHANCED)")
    print("="*60 + "\n")

    all_jobs = []

    # Google Search for jobs
    print("📍 Google Search (Enhanced)")
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

    # SAVE CACHE before post-processing (crash recovery)
    save_cache(unique_jobs, search_type="industry")

    # POST-PROCESSING: Validate and filter all jobs
    print("📍 POST-PROCESSING: Validation & Filtering")
    print("-" * 60)

    validated_jobs = []
    expired_count = 0
    invalid_count = 0
    old_year_count = 0
    senior_count = 0
    low_quality_count = 0

    for job in unique_jobs:
        # Check URL validity
        is_valid, reason = is_valid_job_url(job.get('url', ''), job.get('title', ''))
        if not is_valid:
            invalid_count += 1
            continue

        # Check deadline
        deadline = job.get('deadline', '')
        if deadline and deadline not in ['Not specified', 'Not Specified', '', 'N/A']:
            is_expired, parsed_date = is_deadline_too_old(deadline, max_days_past=7)
            if is_expired:
                expired_count += 1
                print(f"   ⏭️  Expired: {job.get('title', 'Unknown')[:40]}... (deadline: {deadline})")
                continue

        # Check if job is from a past year (2024 or earlier)
        is_old, old_reason = is_job_from_past_year(job)
        if is_old:
            old_year_count += 1
            print(f"   ⏭️  Old job: {job.get('title', 'Unknown')[:40]}... ({old_reason})")
            continue

        # Check if job is senior level
        is_senior, senior_reason = is_senior_role(job)
        if is_senior:
            senior_count += 1
            print(f"   ⏭️  Senior: {job.get('title', 'Unknown')[:40]}... ({senior_reason})")
            continue

        # Add quality score if not already present
        if 'quality_score' not in job:
            job['quality_score'] = calculate_quality_score(job)

        # Filter out very low quality jobs
        if job['quality_score'] < 25:
            low_quality_count += 1
            print(f"   ⏭️  Low quality ({job['quality_score']}): {job.get('title', 'Unknown')[:40]}...")
            continue

        validated_jobs.append(job)

    # Sort by quality score
    validated_jobs.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    print(f"\n   Filtered out:")
    print(f"      • {invalid_count} invalid URLs")
    print(f"      • {expired_count} expired deadlines")
    print(f"      • {old_year_count} old/2024 jobs")
    print(f"      • {senior_count} senior roles")
    print(f"      • {low_quality_count} low quality")

    print("\n" + "=" * 60)
    print(f"✅ Total validated industry jobs: {len(validated_jobs)}")
    print("=" * 60 + "\n")

    # Clear cache after successful completion
    clear_cache()

    return validated_jobs


def find_all_phd_positions():
    """
    Find PhD positions using Google Custom Search API.

    Features:
    - URL validation to filter aggregator pages
    - Deadline validation to filter EXPIRED positions
    - Quality scoring to prioritize funded, relevant positions
    """

    print("\n" + "="*60)
    print("🎓 PHD POSITION SEARCH (ENHANCED)")
    print("="*60 + "\n")

    all_positions = []

    # Google Search for PhD positions
    print("📍 Google Search (Enhanced)")
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

    # SAVE CACHE before post-processing (crash recovery)
    save_cache(unique_positions, search_type="phd")

    # POST-PROCESSING: Validate and filter all positions
    print("📍 POST-PROCESSING: Validation & Deadline Filtering")
    print("-" * 60)

    validated_positions = []
    expired_count = 0
    invalid_count = 0
    old_year_count = 0
    low_quality_count = 0

    for pos in unique_positions:
        # Check URL validity
        is_valid, _ = is_valid_job_url(pos.get('url', ''), pos.get('title', ''))
        if not is_valid:
            invalid_count += 1
            continue

        # CHECK DEADLINE - This is crucial for PhDs!
        deadline = pos.get('deadline', '')
        if deadline and deadline not in ['Not specified', 'Not Specified', '', 'N/A']:
            is_expired, parsed_date = is_deadline_too_old(deadline, max_days_past=7)
            if is_expired:
                expired_count += 1
                date_str = parsed_date.strftime('%d %b %Y') if parsed_date else deadline
                print(f"   ⏭️  EXPIRED: {pos.get('title', 'Unknown')[:40]}... (deadline: {date_str})")
                continue

        # Check if position is from a past year (2024 or earlier)
        is_old, old_reason = is_job_from_past_year(pos)
        if is_old:
            old_year_count += 1
            print(f"   ⏭️  Old position: {pos.get('title', 'Unknown')[:40]}... ({old_reason})")
            continue

        # Add quality score if not already present
        if 'quality_score' not in pos:
            pos['quality_score'] = calculate_quality_score(pos)

            # PhD-specific bonus points
            title_lower = (pos.get('title') or '').lower()
            desc_lower = (pos.get('description') or '').lower()

            if any(word in title_lower or word in desc_lower for word in ['funded', 'stipend', 'scholarship']):
                pos['quality_score'] += 15
            if any(word in title_lower or word in desc_lower for word in ['cdt', 'centre for doctoral']):
                pos['quality_score'] += 10

        # Filter out very low quality positions
        if pos['quality_score'] < 25:
            low_quality_count += 1
            print(f"   ⏭️  Low quality ({pos['quality_score']}): {pos.get('title', 'Unknown')[:40]}...")
            continue

        validated_positions.append(pos)

    # Sort by quality score
    validated_positions.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    print(f"\n   Filtered out:")
    print(f"      • {invalid_count} invalid URLs")
    print(f"      • {expired_count} EXPIRED deadlines")
    print(f"      • {old_year_count} old/2024 positions")
    print(f"      • {low_quality_count} low quality")

    print("\n" + "=" * 60)
    print(f"✅ Total validated PhD positions: {len(validated_positions)}")
    print("=" * 60 + "\n")

    # Clear cache after successful completion
    clear_cache()

    return validated_positions


def search_google_industry_jobs():
    """
    Enhanced Google Search for industry jobs.

    Key improvements:
    1. Target actual job posting platforms (Greenhouse, Lever, etc.)
    2. Use more specific queries to find real postings
    3. Filter out aggregator pages
    4. Fetch full details for valid results
    5. Quality scoring to prioritize best matches
    """

    # IMPROVED QUERIES - Target actual job postings, not search pages
    queries = [
        # ===========================================
        # ATS PLATFORMS (Actual job postings!)
        # ===========================================
        # Greenhouse - many tech/biotech companies use this
        'site:greenhouse.io "machine learning" UK',
        'site:greenhouse.io "data scientist" UK',
        'site:greenhouse.io "graduate" UK',
        'site:greenhouse.io "healthcare" UK',

        # Lever - popular with startups
        'site:lever.co "machine learning" London',
        'site:lever.co "data" UK',
        'site:lever.co "engineer" UK biotech',

        # Workable - many companies use this
        'site:workable.com "machine learning" UK',
        'site:workable.com "graduate" UK',

        # ===========================================
        # SPECIFIC JOB POSTINGS (not search pages)
        # ===========================================
        # LinkedIn specific job views (not search results)
        '"linkedin.com/jobs/view" "machine learning engineer" UK',
        '"linkedin.com/jobs/view" "graduate scheme" UK',
        '"linkedin.com/jobs/view" "data scientist" UK healthcare',

        # ===========================================
        # GRADUATE SCHEMES (High priority!)
        # ===========================================
        '"graduate scheme" "2025" UK technology',
        '"graduate programme" engineering UK "apply"',
        '"early careers" UK biotech "apply now"',
        '"graduate rotation" UK 2025',

        # ===========================================
        # HEALTHCARE / BIOMEDICAL (User's interest)
        # ===========================================
        '"machine learning" healthcare UK "apply"',
        '"data scientist" NHS UK job',
        '"biomedical engineer" UK graduate',
        '"medical device" engineer UK job',
        'site:jobs.ac.uk "machine learning" -postdoc',
        'site:jobs.ac.uk "data scientist" -postdoc -senior',

        # ===========================================
        # COMPANY CAREER PAGES (Direct postings)
        # ===========================================
        'site:careers.google.com "machine learning" UK',
        'site:amazon.jobs "machine learning" UK',
        '"careers" "machine learning engineer" UK "apply"',
        '"careers" "graduate" biotech UK "apply"',

        # ===========================================
        # SPECIFIC COMPANIES (Hidden gems)
        # ===========================================
        'site:benevolent.ai careers',
        'site:oxfordnanopore.com careers graduate',
        'site:healx.io careers',
        '"Cambridge Consultants" graduate careers',
        'site:lifearc.org careers',
    ]

    all_jobs = []
    seen_urls = set()

    for query in queries:
        print(f"   🔍 {query[:55]}...")

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
                    item_url = item.get("link", "")
                    item_title = item.get("title", "")

                    # Skip if already seen
                    if item_url in seen_urls:
                        continue
                    seen_urls.add(item_url)

                    # VALIDATE: Check if this is a real job posting
                    is_valid, reason = is_valid_job_url(item_url, item_title)
                    if not is_valid:
                        print(f"      ⏭️  Skipped: {reason} - {item_title[:40]}...")
                        continue

                    # Build initial job object
                    job = {
                        "title": item_title,
                        "company": extract_company_from_url(item_url),
                        "location": "UK",
                        "city": "",
                        "description": item.get("snippet", ""),
                        "url": item_url,
                        "source": "Google Search",
                        "salary": "Not specified",
                        "post_date": "Recent",
                        "deadline": "Not specified",
                        "requirements": [],
                        "expectations": [],
                        "cv_required": "Not specified",
                        "cover_letter_required": "Not specified",
                    }

                    # Calculate quality score
                    job['quality_score'] = calculate_quality_score(job)

                    # Only process jobs with decent quality score
                    if job['quality_score'] < 30:
                        print(f"      ⏭️  Low quality ({job['quality_score']}): {item_title[:40]}...")
                        continue

                    # ENHANCE: Fetch full details for high-quality results
                    if job['quality_score'] >= 50:
                        try:
                            print(f"      📄 Fetching details for: {item_title[:40]}...")
                            full_details = fetch_job_details(item_url)

                            # Merge full details with job
                            if full_details.get('title') and len(full_details['title']) > 5:
                                job['title'] = full_details['title']
                            if full_details.get('company') and full_details['company'] != 'Unknown':
                                job['company'] = full_details['company']
                            if full_details.get('city'):
                                job['city'] = full_details['city']
                            if full_details.get('salary') and full_details['salary'] != 'Not specified':
                                job['salary'] = full_details['salary']
                            if full_details.get('deadline') and full_details['deadline'] != 'Not specified':
                                job['deadline'] = full_details['deadline']
                            if full_details.get('requirements'):
                                job['requirements'] = full_details['requirements']
                            if full_details.get('expectations'):
                                job['expectations'] = full_details['expectations']
                            if full_details.get('cv_required') and full_details['cv_required'] != 'Not specified':
                                job['cv_required'] = full_details['cv_required']
                            if full_details.get('cover_letter_required') and full_details['cover_letter_required'] != 'Not specified':
                                job['cover_letter_required'] = full_details['cover_letter_required']
                            if full_details.get('description'):
                                job['description'] = full_details['description']

                            print(f"      ✅ Got details: {job['company']}")
                        except Exception as e:
                            print(f"      ⚠️  Couldn't fetch details: {e}")

                    all_jobs.append(job)
                    print(f"      ✅ Added (score: {job['quality_score']}): {job['title'][:50]}...")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Sort by quality score (highest first)
    all_jobs.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    print(f"\n   📊 Google Search: {len(all_jobs)} valid jobs (filtered from {len(seen_urls)} results)")

    return all_jobs


def search_google_phd_positions():
    """
    Enhanced Google Search for PhD positions.

    Key improvements:
    1. Target actual PhD listing platforms (FindAPhD, jobs.ac.uk, etc.)
    2. Filter out expired deadlines
    3. Focus on funded positions
    4. Better queries for 2025 start dates
    """

    # Get current year for queries
    current_year = datetime.now().year
    next_year = current_year + 1

    # IMPROVED QUERIES - Target actual PhD postings
    queries = [
        # ===========================================
        # PHD LISTING PLATFORMS (Best sources!)
        # ===========================================
        f'site:findaphd.com "machine learning" UK funded {next_year}',
        f'site:findaphd.com "data science" UK funded',
        f'site:findaphd.com "healthcare" UK funded',
        f'site:findaphd.com "biomedical" UK funded',
        f'site:findaphd.com "computer vision" UK',

        f'site:jobs.ac.uk PhD "machine learning" UK -expired',
        f'site:jobs.ac.uk PhD "data science" UK',
        f'site:jobs.ac.uk PhD "healthcare" UK funded',
        f'site:jobs.ac.uk studentship "machine learning"',

        # ===========================================
        # UNIVERSITY DIRECT POSTINGS
        # ===========================================
        f'site:cam.ac.uk PhD "machine learning" funded {next_year}',
        f'site:ox.ac.uk DPhil "machine learning" funded',
        f'site:imperial.ac.uk PhD "data science" funded',
        f'site:ucl.ac.uk PhD "machine learning" funded',
        f'site:ed.ac.uk PhD "machine learning" funded',
        f'site:kcl.ac.uk PhD "healthcare" "machine learning"',

        # ===========================================
        # CDT PROGRAMMES (Often best funded!)
        # ===========================================
        f'"CDT" "machine learning" UK {next_year}',
        f'"Centre for Doctoral Training" AI UK apply',
        f'"EPSRC CDT" machine learning UK',
        f'"Health Data Science" CDT UK',

        # ===========================================
        # FUNDING BODIES
        # ===========================================
        f'site:ukri.org PhD "machine learning" studentship',
        f'"EPSRC" PhD "machine learning" UK funded {next_year}',
        f'"Wellcome Trust" PhD studentship UK',
        f'"MRC" PhD "machine learning" healthcare UK',

        # ===========================================
        # RESEARCH INSTITUTES
        # ===========================================
        'site:turing.ac.uk PhD studentship',
        'site:crick.ac.uk PhD studentship',
        '"Alan Turing Institute" PhD machine learning',

        # ===========================================
        # SPECIFIC SEARCHES (Current openings)
        # ===========================================
        f'PhD "machine learning" UK funded "deadline" {next_year}',
        f'PhD "computer vision" UK "apply by" {next_year}',
        f'PhD "healthcare AI" UK funded stipend',
        f'"fully funded PhD" "machine learning" UK {next_year}',
    ]

    all_positions = []
    seen_urls = set()

    for query in queries:
        print(f"   🔍 {query[:55]}...")

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
                    item_url = item.get("link", "")
                    item_title = item.get("title", "")

                    # Skip if already seen
                    if item_url in seen_urls:
                        continue
                    seen_urls.add(item_url)

                    # VALIDATE: Check if this is a real PhD posting
                    is_valid, reason = is_valid_job_url(item_url, item_title)
                    if not is_valid:
                        print(f"      ⏭️  Skipped: {reason} - {item_title[:40]}...")
                        continue

                    # Build initial position object
                    position = {
                        "title": item_title,
                        "company": extract_company_from_url(item_url),
                        "location": "UK",
                        "city": "",
                        "description": item.get("snippet", ""),
                        "url": item_url,
                        "source": "Google Search",
                        "salary": "Check listing",
                        "post_date": "Recent",
                        "deadline": "Not specified",
                        "requirements": [],
                        "expectations": [],
                        "cv_required": "Not specified",
                        "cover_letter_required": "Not specified",
                        "type": "PhD",
                    }

                    # Calculate quality score
                    position['quality_score'] = calculate_quality_score(position)

                    # PhD-specific bonus points
                    title_lower = (item_title or '').lower()
                    desc_lower = (item.get("snippet") or '').lower()
                    url_lower = (item_url or '').lower()

                    if any(word in title_lower or word in desc_lower for word in ['funded', 'stipend', 'scholarship']):
                        position['quality_score'] += 15
                    if any(word in title_lower or word in desc_lower for word in ['cdt', 'centre for doctoral']):
                        position['quality_score'] += 10
                    if any(uni in url_lower for uni in ['cam.ac.uk', 'ox.ac.uk', 'imperial', 'ucl', 'ed.ac.uk']):
                        position['quality_score'] += 10

                    # Skip low quality
                    if position['quality_score'] < 30:
                        print(f"      ⏭️  Low quality ({position['quality_score']}): {item_title[:40]}...")
                        continue

                    # ENHANCE: Fetch full details for PhD positions (especially deadlines!)
                    if position['quality_score'] >= 45:
                        try:
                            print(f"      📄 Fetching details for: {item_title[:40]}...")
                            full_details = fetch_job_details(item_url)

                            # Merge full details
                            if full_details.get('title') and len(full_details['title']) > 5:
                                position['title'] = full_details['title']
                            if full_details.get('company') and full_details['company'] != 'Unknown':
                                position['company'] = full_details['company']
                            if full_details.get('city'):
                                position['city'] = full_details['city']
                            if full_details.get('salary') and full_details['salary'] != 'Not specified':
                                position['salary'] = full_details['salary']
                            if full_details.get('deadline') and full_details['deadline'] != 'Not specified':
                                position['deadline'] = full_details['deadline']
                            if full_details.get('requirements'):
                                position['requirements'] = full_details['requirements']
                            if full_details.get('description'):
                                position['description'] = full_details['description']

                            print(f"      ✅ Got details: {position['company']}")

                            # CHECK DEADLINE - Filter out expired positions!
                            if position['deadline'] and position['deadline'] != 'Not specified':
                                is_expired, parsed_date = is_deadline_too_old(position['deadline'], max_days_past=7)
                                if is_expired:
                                    print(f"      ⏭️  EXPIRED ({position['deadline']}): {item_title[:40]}...")
                                    continue
                                elif parsed_date:
                                    print(f"      📅 Deadline OK: {parsed_date.strftime('%d %B %Y')}")

                        except Exception as e:
                            print(f"      ⚠️  Couldn't fetch details: {e}")

                    all_positions.append(position)
                    print(f"      ✅ Added (score: {position['quality_score']}): {position['title'][:50]}...")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Sort by quality score
    all_positions.sort(key=lambda x: x.get('quality_score', 0), reverse=True)

    print(f"\n   📊 PhD Search: {len(all_positions)} valid positions (filtered from {len(seen_urls)} results)")

    return all_positions


def extract_company_from_url(url):
    """Extract company name from URL"""

    # Handle None or empty URL
    if not url:
        return "Unknown"

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