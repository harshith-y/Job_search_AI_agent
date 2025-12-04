"""
Job Memory System
Tracks which jobs have been seen to avoid duplicates
"""

import os

# Separate memory files for industry and PhD
INDUSTRY_MEMORY_FILE = "seen_jobs.txt"
PHD_MEMORY_FILE = "seen_phds.txt"


def load_memory(memory_file):
    """Load seen job URLs from file"""
    if not os.path.exists(memory_file):
        return set()
    
    with open(memory_file, "r") as f:
        return set(line.strip() for line in f if line.strip())


def save_memory(seen_urls, memory_file):
    """Save seen job URLs to file"""
    with open(memory_file, "w") as f:
        for url in sorted(seen_urls):
            f.write(url + "\n")


def is_new_job(url, job_type="industry"):
    """Check if a job URL has been seen before"""
    
    # Choose memory file based on job type
    memory_file = PHD_MEMORY_FILE if job_type == "phd" else INDUSTRY_MEMORY_FILE
    
    seen_urls = load_memory(memory_file)
    return url not in seen_urls


def mark_as_seen(url, job_type="industry"):
    """Mark a job URL as seen"""
    
    # Choose memory file based on job type
    memory_file = PHD_MEMORY_FILE if job_type == "phd" else INDUSTRY_MEMORY_FILE
    
    seen_urls = load_memory(memory_file)
    seen_urls.add(url)
    save_memory(seen_urls, memory_file)


def get_seen_count(job_type="industry"):
    """Get count of seen jobs"""
    
    memory_file = PHD_MEMORY_FILE if job_type == "phd" else INDUSTRY_MEMORY_FILE
    seen_urls = load_memory(memory_file)
    return len(seen_urls)


def clear_memory(job_type="industry"):
    """Clear all seen jobs (for testing)"""
    
    memory_file = PHD_MEMORY_FILE if job_type == "phd" else INDUSTRY_MEMORY_FILE
    
    if os.path.exists(memory_file):
        os.remove(memory_file)
        print(f"✅ Cleared {job_type} job memory")


# CLI interface
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "stats":
            industry_count = get_seen_count("industry")
            phd_count = get_seen_count("phd")
            print(f"\n📊 Memory Stats:")
            print(f"   Industry jobs seen: {industry_count}")
            print(f"   PhD positions seen: {phd_count}")
            print(f"   Total: {industry_count + phd_count}\n")
        
        elif command == "clear":
            job_type = sys.argv[2] if len(sys.argv) > 2 else "all"
            
            if job_type == "all":
                clear_memory("industry")
                clear_memory("phd")
            else:
                clear_memory(job_type)
        
        else:
            print("\nUsage:")
            print("  python memory.py stats          - Show memory statistics")
            print("  python memory.py clear [type]   - Clear memory")
            print("     type: industry, phd, or all")
            print()
    
    else:
        print("\nUsage:")
        print("  python memory.py stats          - Show memory statistics")
        print("  python memory.py clear [type]   - Clear memory")
        print()