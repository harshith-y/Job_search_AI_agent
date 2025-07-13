import os

MEMORY_FILE = "seen_jobs.txt"

def load_memory():
    with open(MEMORY_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())

def is_new_job(job_url):
    return job_url not in load_memory()

def update_memory(new_job_urls):
    with open(MEMORY_FILE, "a") as f:
        for url in new_job_urls:
            f.write(url + "\n")
