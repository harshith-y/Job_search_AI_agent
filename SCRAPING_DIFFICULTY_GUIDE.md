# 🕷️ Web Scraping Difficulty Guide

## What Makes a Site Easy/Medium/Hard to Scrape?

---

## ⚡ EASY Sites (Simple HTML)

### Characteristics:
✅ **Static HTML** - Content loads immediately in page source
✅ **Simple structure** - Consistent CSS classes/IDs
✅ **No JavaScript required** - All data in initial HTML
✅ **Stable markup** - Rarely changes structure
✅ **No anti-bot measures** - Allows scraping

### How to Identify:
```bash
# Right-click page → View Page Source
# Can you see the job listings in the HTML?
# If YES → Easy scrape
```

### Technical Approach:
- **Tools:** requests + BeautifulSoup
- **Effort:** 30-60 minutes per site
- **Reliability:** High (98%+ success rate)

### Examples:
- Academic job boards (jobs.ac.uk)
- University career pages
- Simple job aggregators
- Government job portals
- Static career pages

### Code Pattern:
```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
jobs = soup.find_all("div", class_="job-listing")
# Done! ✅
```

---

## 🔶 MEDIUM Sites (Moderate JavaScript)

### Characteristics:
⚠️ **Some JavaScript** - Partial dynamic loading
⚠️ **Multiple pages** - Pagination or infinite scroll
⚠️ **AJAX requests** - Data loaded after page load
⚠️ **Moderate protection** - Basic rate limiting
⚠️ **Irregular structure** - Varies between pages

### How to Identify:
```bash
# View Page Source - jobs NOT in HTML
# Open DevTools → Network → XHR
# Can you see API calls loading job data?
# If YES → Medium scrape
```

### Technical Approach:
- **Tools:** requests + BeautifulSoup + API inspection
- **Alternative:** Selenium (lightweight browser automation)
- **Effort:** 2-4 hours per site
- **Reliability:** Medium (80-90% success rate)

### Examples:
- Glassdoor (loads jobs via AJAX)
- Indeed (pagination + dynamic content)
- Reed.co.uk (some JS rendering)
- Monster (mixed static/dynamic)
- Some university portals

### Code Pattern (API Approach):
```python
# Find the API endpoint in DevTools Network tab
api_url = "https://site.com/api/jobs?page=1"
response = requests.get(api_url)
data = response.json()
# Parse JSON directly ✅
```

### Code Pattern (Selenium Approach):
```python
from selenium import webdriver

driver = webdriver.Chrome()
driver.get(url)
# Wait for JS to load
time.sleep(3)
html = driver.page_source
soup = BeautifulSoup(html, "html.parser")
```

---

## 🔴 HARD Sites (Heavy JavaScript / Protection)

### Characteristics:
❌ **Heavy JavaScript** - React/Angular/Vue apps
❌ **Dynamic rendering** - Content generated client-side
❌ **Authentication required** - Login to see jobs
❌ **Anti-bot protection** - Cloudflare, reCAPTCHA
❌ **Rate limiting** - IP bans for scraping
❌ **Frequent changes** - Structure changes weekly

### How to Identify:
```bash
# View Page Source - Almost empty (just <div id="root"></div>)
# All content loaded by JavaScript
# May require login to view
# DevTools Console shows React/Vue
# If YES → Hard scrape
```

### Technical Approach:
- **Tools:** Selenium/Playwright + undetected-chromedriver
- **Alternative:** Official API (if available)
- **Effort:** 8-20 hours per site + ongoing maintenance
- **Reliability:** Low (60-80% success rate, breaks often)

### Examples:
- **LinkedIn** (heavy React, requires login, anti-bot)
- **Indeed** (Cloudflare protection)
- **Greenhouse** (applicant tracking system)
- Many modern company career sites
- Sites with login walls

### Code Pattern (Playwright):
```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    # Login if needed
    page.goto("https://site.com/login")
    page.fill("#email", "your@email.com")
    page.fill("#password", "password")
    page.click("button[type=submit]")
    
    # Wait for navigation
    page.wait_for_selector(".job-listing")
    
    # Extract data
    jobs = page.query_selector_all(".job-listing")
```

### Major Challenges:
1. **Authentication** - Requires account, may violate ToS
2. **Bot detection** - Sites actively block scrapers
3. **Dynamic content** - Need to wait for JS execution
4. **Maintenance** - Breaks frequently, needs updates
5. **Legal/Ethical** - May violate terms of service

---

## 📊 Difficulty Comparison Table

| Factor | Easy | Medium | Hard |
|--------|------|--------|------|
| **HTML Structure** | Static | Mixed | Dynamic (JS) |
| **Authentication** | None | Optional | Required |
| **Anti-bot** | None | Basic | Advanced |
| **Dev Time** | 30-60 min | 2-4 hours | 8-20 hours |
| **Maintenance** | Rare | Monthly | Weekly |
| **Success Rate** | 98% | 80-90% | 60-80% |
| **Tools Needed** | requests + BS4 | + Selenium (light) | + Playwright/undetected |
| **Cost** | Free | Free | Free |
| **Legal Risk** | Low | Low-Medium | Medium-High |

---

## 🔍 How to Assess a New Site

### Step-by-Step Process:

**1. View Page Source (Ctrl+U)**
```
If jobs visible in HTML → Easy
If jobs NOT visible → Continue to step 2
```

**2. Open DevTools → Network Tab**
```
Refresh page
Look for XHR/Fetch requests
If API endpoints visible → Medium
If minimal API calls → Continue to step 3
```

**3. Check Page Structure**
```
Look for <div id="root"></div> or <div id="app"></div>
Check Console for React/Vue/Angular
If present → Hard
```

**4. Test with Basic Scraper**
```python
import requests
from bs4 import BeautifulSoup

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
print(soup.prettify())

# Can you see job titles/descriptions?
# Yes → Easy
# No → Medium/Hard
```

---

## 🎯 Quick Decision Guide

### Choose EASY if:
- You see jobs in "View Page Source"
- Academic/government sites
- Simple job boards
- No login required

### Choose MEDIUM if:
- Jobs load via AJAX/API
- Pagination exists
- Some JS but content accessible
- DevTools Network shows API calls

### Choose HARD if:
- Requires login/authentication
- Modern SPA (React/Vue/Angular)
- Cloudflare protection
- Content 100% JS-generated
- Anti-bot measures present

---

## 💡 Pro Tips

### 1. **Start with Easy Sites**
Build your scraper collection gradually. Easy sites give you data while you work on harder ones.

### 2. **Use APIs When Available**
Many sites have hidden APIs. Find them in DevTools Network tab - much easier than scraping HTML.

### 3. **Respect robots.txt**
```bash
# Check if scraping is allowed
curl https://example.com/robots.txt
```

### 4. **Add Delays**
```python
import time
time.sleep(2)  # Be nice to servers
```

### 5. **Rotate User Agents**
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
requests.get(url, headers=headers)
```

### 6. **Handle Failures Gracefully**
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except Exception as e:
    print(f"Failed: {e}")
    # Continue with other sites
```

---

## ⚠️ Legal & Ethical Considerations

### ✅ Generally OK:
- Public job listings
- Academic positions
- Government sites
- No authentication required
- Reasonable rate limits

### ⚠️ Gray Area:
- Sites with "No scraping" in ToS
- Requires account/login
- Aggressive scraping (1000s requests)
- Commercial use of data

### ❌ Don't Do:
- Scraping copyrighted content
- Violating CFAA (USA) / Computer Misuse Act (UK)
- Bypassing paywalls
- DDoS-ing sites with requests
- Scraping personal data (GDPR)

---

## 🛠️ Tools Comparison

| Tool | Best For | Difficulty | Speed | Cost |
|------|----------|------------|-------|------|
| **requests + BS4** | Easy sites | Low | Fast | Free |
| **Selenium** | Medium sites | Medium | Slow | Free |
| **Playwright** | Hard sites | High | Medium | Free |
| **Scrapy** | Large-scale | Medium | Fast | Free |
| **Official API** | Any | Low | Fast | Often free |

---

## 📚 Learning Resources

### For Beginners:
- BeautifulSoup docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- Requests docs: https://requests.readthedocs.io/

### For Medium Sites:
- Selenium: https://selenium-python.readthedocs.io/
- Finding hidden APIs: Use Chrome DevTools

### For Hard Sites:
- Playwright: https://playwright.dev/python/
- undetected-chromedriver: https://github.com/ultrafunkamsterdam/undetected-chromedriver

---

## 🎓 Next Steps

1. **Test sites you want to scrape** using the assessment steps above
2. **Start with Easy sites** to build momentum
3. **Learn Medium scraping** when ready (API inspection)
4. **Avoid Hard sites initially** unless critical

Remember: 80% of valuable job postings are on Easy/Medium sites!
