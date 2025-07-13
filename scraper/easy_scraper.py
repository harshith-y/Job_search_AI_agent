import requests
import yaml
from bs4 import BeautifulSoup

# === Load config.yaml ===
def load_config(file_path='scraper/config.yaml'):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config['easy_sites'], config['medium_sites'], config['hard_sites']

import requests
from bs4 import BeautifulSoup

def scrape_ml_jobs_uk(max_pages=5):
    print("Scraping: Machine Learning Jobs UK")
    base_url = "https://machinelearningjobs.co.uk"
    jobs = []
    for page in range(1, max_pages + 1):
        print(f"  Page {page}")
        url = f"{base_url}/?page={page}"
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.find_all("article")
            if not job_cards:
                print("  No jobs found on this page. Stopping.")
                break

            for card in job_cards:
                try:
                    # Extract job title
                    title_tag = card.find("h2")
                    title = title_tag.text.strip() if title_tag else "Unknown Title"

                    # Extract company name
                    company_tag = card.find("span", class_="font-semibold")
                    company = company_tag.text.strip() if company_tag else "Unknown Company"

                    # Extract location, if present
                    spans = card.select("div.flex.gap-1.items-center.justify-start span")
                    location = spans[1].text.strip() if len(spans) > 1 else "Unknown Location"

                    # Extract job link
                    link_tag = card.find("a", class_="absolute inset-0")
                    if not link_tag or not link_tag.get("href"):
                        # Skip non-job cards - location buttons or articles
                        continue

                    link = link_tag["href"]
                    if "/view-job/" not in link:
                        # Skip non-job URLs
                        continue

                    # Construct full job URL
                    full_url = link if link.startswith("http") else base_url + link

                    # Request the job detail page
                    detail_response = requests.get(full_url)
                    detail_soup = BeautifulSoup(detail_response.text, "html.parser")
                    desc_div = detail_soup.find("div", class_="prose")
                    description = desc_div.get_text(separator="\n").strip() if desc_div else "No description found"
                                                            #separate with newlines and remove white spaces
                    # Store job data
                    jobs.append({
                        "title": title,
                        "company": company,
                        "location": location,
                        "url": full_url,
                        "description": description
                    })

                except Exception as e:
                    print(f"  Failed to parse job card: {e}")

        except Exception as e:
            print(f"  Request failed for page {page}: {e}")
            break

    print(f"\nTotal jobs scraped: {len(jobs)}\n")
    return jobs



def scrape_jobs_ac_uk(url, source):
    import requests
    from bs4 import BeautifulSoup

    jobs = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        job_divs = soup.select("div.j-search-result__result")

        for job_div in job_divs:
            try:
                # Extract job title and link
                title_tag = job_div.select_one(".j-search-result__text a")
                title = title_tag.text.strip() if title_tag else "Unknown Title"
                link = title_tag["href"] if title_tag and title_tag.has_attr("href") else None
                job_url = f"https://www.jobs.ac.uk{link}" if link and not link.startswith("http") else link
                if not job_url:
                    continue

                # Extract company name
                org_tag = job_div.select_one(".j-search-result__employer b")
                company = org_tag.text.strip() if org_tag else "Unknown Company"

                # Extract location
                location_tag = job_div.find(string=lambda text: text and "Location:" in text)
                location = location_tag.parent.text.replace("Location:", "").strip() if location_tag else "Unknown Location"

                # Extract salary
                salary = ""
                salary_tag = job_div.select_one(".j-search-result__info")
                if salary_tag and "Salary:" in salary_tag.text:
                    salary = salary_tag.text.replace("Salary:", "").strip()

                # Extract closing date
                close_tag = job_div.select_one(".j-search-result__date--blue")
                closing_date = close_tag.text.strip() if close_tag else "Not specified"

                # Fetch detail page for full job description
                detail_response = requests.get(job_url)
                detail_soup = BeautifulSoup(detail_response.text, "html.parser")
                desc_div = detail_soup.find("div", id="job-description")
                description = desc_div.get_text(separator="\n", strip=True) if desc_div else "No description found"

                # Append job data
                jobs.append({
                    "source": source,
                    "title": title,
                    "company": company,
                    "location": location,
                    "url": job_url,
                    "description": description,
                    "salary": salary,
                    "closing_date": closing_date
                })

            except Exception as e:
                print(f"  Skipping job due to error: {e}")

    except Exception as e:
        print(f"Failed to scrape {source}: {e}")

    return jobs



# === SCRAPER: King's College London ===
def scrape_kcl(url, source):
    jobs = []
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        job_links = soup.select(".vacancy .vacancy__link")

        for link_tag in job_links:
            title = link_tag.text.strip()
            link = link_tag["href"]
            full_url = link if link.startswith("http") else f"https://www.kcl.ac.uk{link}"

            jobs.append({
                "source": source,
                "title": title,
                "company": "King's College London",
                "location": "London, UK",
                "url": full_url,
                "description": title
            })
    except Exception as e:
        print(f"⚠️ Failed to scrape {source}: {e}")

    return jobs

# === Master Router for Easy Sites ===
def scrape_easy_sites(easy_sites):
    all_jobs = []

    for site in easy_sites:
        url = site['url']
        name = site['name']
        print(f"\n🟢 Scraping: {name} ({url})")

        if "machinelearningjobs.co.uk" in url:
            # jobs = scrape_ml_jobs_uk(max_pages=3)
            continue
        elif "jobs.ac.uk" in url:
            jobs = scrape_jobs_ac_uk(url, name)
        elif "kcl.ac.uk" in url:
            # jobs = scrape_kcl(url, name)
            continue
        else:
            print(f"⚠️ No scraper defined for: {name}")
            jobs = []

        print(f"✅ Found {len(jobs)} jobs from {name}")
        all_jobs.extend(jobs)

    return all_jobs

# === Run ===
if __name__ == "__main__":
    easy, medium, hard = load_config()
    all_easy_jobs = scrape_easy_sites(easy)
    print(f"\n✅ Total jobs scraped: {len(all_easy_jobs)}")
    for i, job in enumerate(all_easy_jobs, 1):
        print(f"\n🔹 Job {i}")
        print(f"Title      : {job['title']}")
        print(f"Company    : {job['company']}")
        print(f"Location   : {job['location']}")
        print(f"URL        : {job['url']}")
        print(f"Description:\n{job['description'][:500]}...")  # print first 500 characters


