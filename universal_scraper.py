"""
Universal Job Scraper - ENHANCED
Works with config.yaml to scrape multiple job sites
Fetches FULL job details from each individual posting
"""

import requests
from bs4 import BeautifulSoup
import yaml
import re
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import time


class UniversalJobScraper:
    """
    Smart scraper that:
    1. Finds job listings from search pages
    2. FETCHES each individual job page (KEY ENHANCEMENT!)
    3. EXTRACTS full details (salary, deadline, requirements, etc.)
    """
    
    def __init__(self, config_file="config.yaml"):
        with open(config_file, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Site-specific patterns (for better accuracy)
        self.site_patterns = {
            "jobs.ac.uk": {
                "job_container": "div.j-search-result",
                "title": "h3.j-search-result__heading a",
                "company": "div.j-search-result__employer",
                "location": "li.j-search-result__location",
                "salary": "li.j-search-result__salary",
                "link": "h3.j-search-result__heading a",
                "date": "li.j-search-result__date",
            },
            "machinelearningjobs.co.uk": {
                "job_container": "div.job-listing",
                "title": "h2.job-title a, h3.job-title a",
                "company": "span.company, div.company",
                "location": "span.location, div.location",
                "salary": "span.salary, div.salary",
                "link": "h2.job-title a, h3.job-title a",
            },
            "qmul.ac.uk": {
                "job_container": "div.job, tr.job-listing, li.job-item",
                "title": "h3 a, td.title a",
                "company": "span.department",
                "link": "h3 a, td.title a",
            },
            "ox.ac.uk": {
                "job_container": "div.job, article.job, li.job-listing",
                "title": "h2 a, h3 a",
                "link": "h2 a, h3 a",
            },
            "kcl.ac.uk": {
                "job_container": "div.job-item, tr.job-row",
                "title": "a.job-title, td.job-title a",
                "company": "span.department",
                "location": "span.location",
                "link": "a.job-title",
            },
            "imperial.ac.uk": {
                "job_container": "div.vacancy, tr.vacancy-row",
                "title": "a.vacancy-title",
                "company": "span.department",
                "location": "span.location",
                "link": "a.vacancy-title",
            },
            "ucl.ac.uk": {
                "job_container": "div.job, tr.job-listing",
                "title": "h3.job-title a, td.title a",
                "company": "span.department",
                "link": "h3.job-title a, td.title a",
            },
            "glassdoor.co.uk": {
                "job_container": "li.react-job-listing, div.job-listing",
                "title": "a.job-title",
                "company": "div.employer-name",
                "location": "div.location",
                "salary": "div.salary-estimate",
                "link": "a.job-title",
            },
            "indeed.co.uk": {
                "job_container": "div.job_seen_beacon, div.jobsearch-SerpJobCard",
                "title": "h2.jobTitle a, a.jobtitle",
                "company": "span.companyName",
                "location": "div.companyLocation",
                "salary": "div.salary-snippet",
                "link": "h2.jobTitle a, a.jobtitle",
            },
            "linkedin.com": {
                "job_container": "div.base-card, li.jobs-search-results__list-item",
                "title": "h3.base-search-card__title",
                "company": "h4.base-search-card__subtitle",
                "location": "span.job-search-card__location",
                "link": "a.base-card__full-link",
            },
        }
        
        # Generic patterns (fallback)
        self.generic_patterns = {
            "job_container": [
                "div[class*='job']", "li[class*='job']", "tr[class*='job']",
                "div[class*='vacancy']", "div[class*='position']",
                "article[class*='job']", "div[class*='listing']"
            ],
            "title": [
                "h2 a", "h3 a", "a[class*='title']", "a[class*='job']",
                "h2[class*='title']", "h3[class*='title']", "div.title a"
            ],
            "company": [
                "span[class*='company']", "div[class*='company']",
                "span[class*='employer']", "div[class*='employer']",
                "span[class*='organization']"
            ],
            "location": [
                "span[class*='location']", "div[class*='location']",
                "span[class*='city']", "div[class*='city']"
            ],
            "salary": [
                "span[class*='salary']", "div[class*='salary']",
                "span[class*='pay']", "div[class*='compensation']"
            ],
        }
    
    def scrape_site(self, site_name, site_url):
        """Scrape a single site and fetch FULL details for each job"""
        
        print(f"🔍 Scraping {site_name}...")
        
        try:
            # STEP 1: Fetch search results page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(site_url, headers=headers, timeout=15)
            
            if response.status_code != 200:
                print(f"   ❌ Failed: HTTP {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            domain = urlparse(site_url).netloc
            
            # STEP 2: Extract basic job info and URLs from search results
            jobs_basic = self._extract_with_patterns(soup, domain, site_url)
            
            if not jobs_basic:
                print(f"   📋 Using generic scraper...")
                jobs_basic = self._generic_extract(soup, site_url)
            
            if not jobs_basic:
                print(f"   ⚠️  No jobs found on search page")
                return []
            
            print(f"   📋 Found {len(jobs_basic)} job listings")
            
            # STEP 3: Fetch FULL details for each job (THIS IS THE KEY ENHANCEMENT!)
            jobs_complete = []
            max_jobs = min(len(jobs_basic), 20)  # Limit to 20 per site
            
            for i, job_basic in enumerate(jobs_basic[:max_jobs], 1):
                url = job_basic.get('url')
                
                if not url or len(url) < 10:
                    continue
                
                print(f"      [{i}/{max_jobs}] Fetching full details...", end=" ")
                
                # Fetch the FULL job page and extract all details
                full_details = self.scrape_with_details(url)
                
                # Merge basic info with full details
                job_complete = {**job_basic, **full_details}
                job_complete['source'] = site_name
                
                # Extract better title from full page if needed
                if full_details.get('title') and len(full_details['title']) > 5:
                    job_complete['title'] = full_details['title']
                
                # Only add if we got a real title
                if job_complete.get('title') and len(job_complete['title']) > 5:
                    jobs_complete.append(job_complete)
                    print("✅")
                else:
                    print("⏭️")
                
                time.sleep(0.5)  # Be polite to servers
            
            print(f"   ✅ Extracted {len(jobs_complete)} complete job postings\n")
            return jobs_complete
        
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def _extract_with_patterns(self, soup, domain, base_url):
        """Extract jobs using site-specific patterns"""
        
        # Find matching pattern
        pattern = None
        for site_key, site_pattern in self.site_patterns.items():
            if site_key in domain:
                pattern = site_pattern
                print(f"   🎯 Using pattern for: {site_key}")
                break
        
        if not pattern:
            return []
        
        jobs = []
        
        # Find job containers
        containers = soup.select(pattern["job_container"])
        
        for container in containers:
            try:
                job = self._extract_job_from_container(
                    container, pattern, base_url
                )
                if job and job.get('title') and job.get('url'):
                    jobs.append(job)
            except Exception as e:
                continue
        
        return jobs
    
    def _extract_job_from_container(self, container, pattern, base_url):
        """Extract job details from a container using patterns"""
        
        job = {
            'title': '',
            'company': '',
            'location': 'UK',
            'city': '',
            'salary': 'Not specified',
            'post_date': 'Recent',
            'url': '',
            'description': '',
            'requirements': [],
            'expectations': [],
            'deadline': 'Not specified',
            'cv_required': 'Not specified',
            'cover_letter_required': 'Not specified',
        }
        
        # Extract title
        if 'title' in pattern:
            title_elem = container.select_one(pattern['title'])
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
        
        # Extract company
        if 'company' in pattern:
            company_elem = container.select_one(pattern['company'])
            if company_elem:
                job['company'] = company_elem.get_text(strip=True)
        
        # Extract location
        if 'location' in pattern:
            location_elem = container.select_one(pattern['location'])
            if location_elem:
                location_text = location_elem.get_text(strip=True)
                job['location'] = location_text
                job['city'] = self._extract_city_from_text(location_text)
        
        # Extract salary
        if 'salary' in pattern:
            salary_elem = container.select_one(pattern['salary'])
            if salary_elem:
                job['salary'] = salary_elem.get_text(strip=True)
        
        # Extract link
        if 'link' in pattern:
            link_elem = container.select_one(pattern['link'])
            if link_elem and link_elem.get('href'):
                href = link_elem.get('href')
                job['url'] = urljoin(base_url, href)
        
        # Extract date
        if 'date' in pattern:
            date_elem = container.select_one(pattern['date'])
            if date_elem:
                job['post_date'] = self._parse_date(date_elem.get_text(strip=True))
        
        # Get description snippet from container
        text = container.get_text(' ', strip=True)
        job['description'] = text[:300] + '...' if len(text) > 300 else text
        
        return job
    
    def _generic_extract(self, soup, base_url):
        """Generic extraction when no specific pattern matches"""
        
        jobs = []
        
        # Try different container patterns
        containers = []
        for pattern in self.generic_patterns['job_container']:
            containers.extend(soup.select(pattern)[:50])  # Limit to 50
        
        # Deduplicate containers
        seen = set()
        unique_containers = []
        for c in containers:
            c_str = str(c)[:200]  # First 200 chars as signature
            if c_str not in seen:
                seen.add(c_str)
                unique_containers.append(c)
        
        for container in unique_containers[:30]:  # Max 30 jobs
            try:
                job = self._generic_extract_job(container, base_url)
                if job and job.get('title') and job.get('url'):
                    jobs.append(job)
            except:
                continue
        
        return jobs
    
    def _generic_extract_job(self, container, base_url):
        """Extract job using generic patterns"""
        
        job = {
            'title': '',
            'company': 'See listing',
            'location': 'UK',
            'city': '',
            'salary': 'Not specified',
            'post_date': 'Recent',
            'url': '',
            'description': '',
            'requirements': [],
            'expectations': [],
            'deadline': 'Not specified',
            'cv_required': 'Not specified',
            'cover_letter_required': 'Not specified',
        }
        
        # Extract title (try all patterns)
        for pattern in self.generic_patterns['title']:
            elem = container.select_one(pattern)
            if elem:
                job['title'] = elem.get_text(strip=True)
                # Try to get link from same element
                if elem.get('href'):
                    job['url'] = urljoin(base_url, elem.get('href'))
                elif elem.find_parent('a'):
                    href = elem.find_parent('a').get('href')
                    if href:
                        job['url'] = urljoin(base_url, href)
                break
        
        # Extract company
        for pattern in self.generic_patterns['company']:
            elem = container.select_one(pattern)
            if elem:
                job['company'] = elem.get_text(strip=True)
                break
        
        # Extract location
        for pattern in self.generic_patterns['location']:
            elem = container.select_one(pattern)
            if elem:
                location_text = elem.get_text(strip=True)
                job['location'] = location_text
                job['city'] = self._extract_city_from_text(location_text)
                break
        
        # Extract salary
        for pattern in self.generic_patterns['salary']:
            elem = container.select_one(pattern)
            if elem:
                job['salary'] = elem.get_text(strip=True)
                break
        
        # If no URL found yet, try any link in container
        if not job['url']:
            link = container.find('a', href=True)
            if link:
                job['url'] = urljoin(base_url, link.get('href'))
        
        # Description
        text = container.get_text(' ', strip=True)
        job['description'] = text[:300] + '...' if len(text) > 500 else text
        
        return job
    
    def _extract_city_from_text(self, text):
        """Extract UK city from location text"""
        
        uk_cities = [
            "London", "Cambridge", "Oxford", "Edinburgh", "Manchester",
            "Bristol", "Birmingham", "Leeds", "Glasgow", "Liverpool",
            "Newcastle", "Sheffield", "Nottingham", "Southampton",
            "Warwick", "Bath", "Durham", "St Andrews", "Leicester",
            "Cardiff", "Belfast", "Reading", "Brighton", "York"
        ]
        
        text_lower = text.lower()
        
        for city in uk_cities:
            if city.lower() in text_lower:
                return city
        
        if "remote" in text_lower:
            return "Remote"
        
        return text.split(',')[0] if ',' in text else text
    
    def _parse_date(self, date_text):
        """Parse date from text"""
        
        date_text = date_text.lower().strip()
        today = datetime.now()
        
        # Check for relative dates
        if 'today' in date_text or 'just posted' in date_text:
            return today.strftime("%Y-%m-%d")
        elif 'yesterday' in date_text:
            return (today - timedelta(days=1)).strftime("%Y-%m-%d")
        elif 'days ago' in date_text:
            match = re.search(r'(\d+)\s*days?\s*ago', date_text)
            if match:
                days = int(match.group(1))
                return (today - timedelta(days=days)).strftime("%Y-%m-%d")
        elif 'week' in date_text:
            return (today - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Try to extract date
        date_patterns = [
            r'(\d{1,2})\s*(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',
            r'(\d{1,2})/(\d{1,2})/(\d{4})',
            r'(\d{4})-(\d{2})-(\d{2})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Recent"
    
    def scrape_all(self):
        """Scrape all sites from config"""
        
        all_jobs = []
        
        # Get all sites from config
        sites = []
        
        if 'easy_sites' in self.config:
            sites.extend([(s['name'], s['url']) for s in self.config['easy_sites']])
        
        if 'medium_sites' in self.config:
            sites.extend([(s['name'], s['url']) for s in self.config['medium_sites']])
        
        if 'hard_sites' in self.config:
            sites.extend([(s['name'], s['url']) for s in self.config['hard_sites']])
        
        print(f"\n{'='*70}")
        print(f"🔍 SCRAPING {len(sites)} SITES WITH FULL DETAIL EXTRACTION")
        print(f"{'='*70}\n")
        
        for name, url in sites:
            jobs = self.scrape_site(name, url)
            all_jobs.extend(jobs)
            time.sleep(2)  # Be polite
        
        print(f"\n{'='*70}")
        print(f"✅ Total jobs with full details: {len(all_jobs)}")
        print(f"{'='*70}\n")
        
        return all_jobs
    
    def scrape_with_details(self, url):
        """
        Fetch full job page and extract detailed info
        THIS IS THE KEY METHOD - it visits each job URL and extracts everything!
        """
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all text for searching
            text = soup.get_text().lower()
            
            # Extract EVERYTHING from the full page
            details = {
                'title': self._extract_title_from_page(soup),
                'company': self._extract_company_from_page(soup, url),
                'city': self._extract_city_from_page(soup, text),
                'salary': self._extract_salary_from_page(soup, text),
                'deadline': self._extract_deadline_from_page(text),
                'requirements': self._extract_requirements(soup, text),
                'expectations': self._extract_expectations(soup, text),
                'cv_required': self._check_cv_required(text),
                'cover_letter_required': self._check_cover_letter(text),
                'description': self._extract_description_from_page(soup),
            }
            
            return details
        
        except:
            return {
                'requirements': [],
                'expectations': [],
                'deadline': 'Not specified',
                'cv_required': 'Not specified',
                'cover_letter_required': 'Not specified',
            }
    
    def _extract_title_from_page(self, soup):
        """Extract job title from full page"""
        
        # Try common title patterns
        patterns = [
            "h1", "h2.job-title", "h1.job-title", "h1.title",
            "h1[class*='title']", "h2[class*='title']"
        ]
        
        for pattern in patterns:
            elem = soup.select_one(pattern)
            if elem:
                title = elem.get_text(strip=True)
                if 5 < len(title) < 200:
                    return title
        
        return None
    
    def _extract_company_from_page(self, soup, url):
        """Extract company from full page"""
        
        # Try to find company in page
        patterns = [
            "span[class*='company']", "div[class*='company']",
            "span[class*='employer']", "div[class*='organisation']"
        ]
        
        for pattern in patterns:
            elem = soup.select_one(pattern)
            if elem:
                return elem.get_text(strip=True)
        
        # Extract from URL
        domain_map = {
            "qmul.ac.uk": "Queen Mary University of London",
            "ox.ac.uk": "University of Oxford",
            "cam.ac.uk": "University of Cambridge",
            "imperial.ac.uk": "Imperial College London",
            "ucl.ac.uk": "UCL",
            "kcl.ac.uk": "King's College London",
            "ed.ac.uk": "University of Edinburgh",
        }
        
        for key, name in domain_map.items():
            if key in url:
                return name
        
        return None
    
    def _extract_city_from_page(self, soup, text):
        """Extract city from full page"""
        
        uk_cities = [
            "London", "Cambridge", "Oxford", "Edinburgh", "Manchester",
            "Bristol", "Birmingham", "Leeds", "Glasgow", "Liverpool",
            "Newcastle", "Sheffield", "Nottingham", "Southampton"
        ]
        
        # Check in text
        for city in uk_cities:
            if city.lower() in text:
                return city
        
        if "remote" in text:
            return "Remote"
        
        return ""
    
    def _extract_salary_from_page(self, soup, text):
        """Extract salary from full page - KEY ENHANCEMENT!"""
        
        # Look for salary section
        salary_keywords = ['salary', 'pay', 'compensation', 'stipend']
        
        for keyword in salary_keywords:
            if keyword in text:
                idx = text.find(keyword)
                snippet = text[idx:idx+300]
                
                # UK salary patterns
                patterns = [
                    r'£\s*(\d{2,3},?\d{3})\s*-\s*£?\s*(\d{2,3},?\d{3})',  # £44,288 - £51,755
                    r'£\s*(\d{2,3},?\d{3})',  # £45,000
                    r'(\d{2,3},?\d{3})\s*-\s*(\d{2,3},?\d{3})\s*per annum',
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, snippet)
                    if match:
                        return match.group(0)
        
        # Try finding it in HTML structure
        salary_selectors = [
            "span[class*='salary']", "div[class*='salary']",
            "dd.salary", "td.salary"
        ]
        
        for selector in salary_selectors:
            elem = soup.select_one(selector)
            if elem:
                salary = elem.get_text(strip=True)
                if '£' in salary or 'stipend' in salary.lower():
                    return salary
        
        return "Not specified"
    
    def _extract_description_from_page(self, soup):
        """Extract job description from full page"""
        
        # Get main content
        content_selectors = [
            "div.job-description", "div.description", "div[class*='content']",
            "article", "main"
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(' ', strip=True)
                return text[:500] + '...' if len(text) > 500 else text
        
        # Fallback to body
        body = soup.find('body')
        if body:
            text = body.get_text(' ', strip=True)
            return text[:500] + '...' if len(text) > 500 else text
        
        return ""
    
    def _extract_requirements(self, soup, text):
        """Extract requirements from full page - KEY ENHANCEMENT!"""
        
        requirements = []
        
        # Look for requirements section
        headers = soup.find_all(['h2', 'h3', 'h4', 'strong'])
        
        for header in headers:
            header_text = header.get_text().lower()
            if any(word in header_text for word in ['requirement', 'qualification', 'essential', 'must have', 'about you']):
                # Get following content
                next_elem = header.find_next_sibling()
                if next_elem:
                    if next_elem.name == 'ul':
                        items = next_elem.find_all('li')
                        requirements = [item.get_text(strip=True) for item in items[:8]]
                    else:
                        text_content = next_elem.get_text(strip=True)
                        if len(text_content) > 30:
                            # Split by periods or newlines
                            sentences = [s.strip() for s in re.split(r'[.\n]', text_content) if len(s.strip()) > 20]
                            requirements = sentences[:5]
                
                if requirements:
                    break
        
        # Fallback: look for common keywords
        if not requirements:
            keywords = ['phd', 'master', 'bachelor', 'python', 'pytorch', 'tensorflow', 'machine learning', 'experience']
            for keyword in keywords:
                if keyword in text:
                    requirements.append(keyword.title())
                    if len(requirements) >= 5:
                        break
        
        return requirements[:8]
    
    def _extract_expectations(self, soup, text):
        """Extract role expectations from full page - KEY ENHANCEMENT!"""
        
        expectations = []
        
        headers = soup.find_all(['h2', 'h3', 'h4', 'strong'])
        
        for header in headers:
            header_text = header.get_text().lower()
            if any(word in header_text for word in ['responsibilities', 'duties', 'you will', 'role', 'about the role']):
                next_elem = header.find_next_sibling()
                if next_elem:
                    if next_elem.name == 'ul':
                        items = next_elem.find_all('li')
                        expectations = [item.get_text(strip=True)[:200] for item in items[:6]]
                    else:
                        text_content = next_elem.get_text(strip=True)
                        if len(text_content) > 30:
                            sentences = [s.strip() for s in re.split(r'[.\n]', text_content) if len(s.strip()) > 20]
                            expectations = sentences[:5]
                
                if expectations:
                    break
        
        return expectations
    
    def _extract_deadline_from_page(self, text):
        """Extract deadline from full page - KEY ENHANCEMENT!"""
        
        deadline_keywords = ['deadline', 'closing date', 'apply by', 'close date', 'closing']
        
        for keyword in deadline_keywords:
            if keyword in text:
                idx = text.find(keyword)
                snippet = text[idx:idx+200]
                
                # Look for dates
                date_match = re.search(r'(\d{1,2})\s+(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})', snippet, re.IGNORECASE)
                if date_match:
                    return date_match.group(0)
                
                date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', snippet)
                if date_match:
                    return date_match.group(0)
        
        return 'Not specified'
    
    def _check_cv_required(self, text):
        """Check if CV is required"""
        
        if 'cv required' in text or 'resume required' in text or 'must submit cv' in text:
            return 'Yes'
        elif 'cv' in text or 'resume' in text:
            return 'Likely'
        return 'Not specified'
    
    def _check_cover_letter(self, text):
        """Check if cover letter is required"""
        
        if 'cover letter required' in text or 'covering letter required' in text:
            return 'Yes'
        elif 'cover letter' in text or 'covering letter' in text:
            return 'Likely'
        return 'Not specified'


# Main function
def scrape_all_sites():
    """Scrape all configured sites with FULL detail extraction"""
    
    scraper = UniversalJobScraper()
    jobs = scraper.scrape_all()
    
    # Deduplicate by URL
    seen_urls = set()
    unique_jobs = []
    
    for job in jobs:
        if job['url'] not in seen_urls:
            seen_urls.add(job['url'])
            unique_jobs.append(job)
    
    print(f"📊 Unique jobs after deduplication: {len(unique_jobs)}\n")
    
    return unique_jobs


if __name__ == "__main__":
    # Test
    jobs = scrape_all_sites()
    
    if jobs:
        print("\n" + "="*70)
        print("Sample job with FULL details:")
        print("="*70 + "\n")
        
        job = jobs[0]
        print(f"Title: {job['title']}")
        print(f"Company: {job['company']}")
        print(f"City: {job['city']}")
        print(f"Salary: {job['salary']}")
        print(f"Deadline: {job['deadline']}")
        print(f"CV Required: {job['cv_required']}")
        print(f"Cover Letter: {job['cover_letter_required']}")
        print(f"\nRequirements:")
        for req in job['requirements'][:3]:
            print(f"  • {req[:100]}")
        print(f"\nExpectations:")
        for exp in job['expectations'][:3]:
            print(f"  • {exp[:100]}")
        print(f"\nURL: {job['url'][:60]}...")