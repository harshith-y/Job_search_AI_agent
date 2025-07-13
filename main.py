from memory import load_memory, is_new_job, update_memory
from agent import summarize_job

seen = load_memory()

all_jobs = scrape_easy_sites(easy)  # Your scraper call

new_jobs = [job for job in all_jobs if is_new_job(job['url'])]
print(f"\n🆕 Found {len(new_jobs)} new jobs")

relevant_jobs = []

for job in new_jobs:
    is_relevant, summary = summarize_job(job)
    if is_relevant:
        job["summary"] = summary
        relevant_jobs.append(job)

# Update memory
update_memory([job['url'] for job in new_jobs])
