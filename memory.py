"""
Simple memory system for tracking seen jobs
Uses a text file to store URLs of jobs we've already seen
"""

import os

MEMORY_FILE = "seen_jobs.txt"


def load_memory():
    """Load list of previously seen job URLs"""
    if not os.path.exists(MEMORY_FILE):
        return set()
    
    with open(MEMORY_FILE, "r") as f:
        return set(line.strip() for line in f if line.strip())


def is_new_job(url):
    """Check if we've seen this job before"""
    seen = load_memory()
    return url not in seen


def update_memory(urls):
    """Add new job URLs to memory"""
    with open(MEMORY_FILE, "a") as f:
        for url in urls:
            f.write(url + "\n")


def clear_memory():
    """Clear all memory (use with caution!)"""
    if os.path.exists(MEMORY_FILE):
        os.remove(MEMORY_FILE)
    print("✅ Memory cleared")


# Example usage
if __name__ == "__main__":
    print("Memory system test:")
    print(f"Previously seen jobs: {len(load_memory())}")