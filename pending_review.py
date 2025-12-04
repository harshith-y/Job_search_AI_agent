"""
Pending Review System
When searches are triggered remotely, results are saved for later GUI review
"""

import json
import os
from datetime import datetime

PENDING_FILE = "pending_review.json"


def save_for_review(jobs):
    """Save jobs that need to be reviewed"""
    
    # Load existing pending reviews
    if os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "r") as f:
            pending = json.load(f)
    else:
        pending = {"jobs": [], "last_updated": None}
    
    # Add new jobs
    for job in jobs:
        # Check if already pending
        if not any(existing['url'] == job['url'] for existing in pending['jobs']):
            pending['jobs'].append(job)
    
    # Update timestamp
    pending['last_updated'] = datetime.now().isoformat()
    
    # Save
    with open(PENDING_FILE, "w") as f:
        json.dump(pending, f, indent=2)
    
    return len(pending['jobs'])


def load_pending_reviews():
    """Load jobs waiting for review"""
    
    if not os.path.exists(PENDING_FILE):
        return []
    
    with open(PENDING_FILE, "r") as f:
        pending = json.load(f)
    
    return pending.get('jobs', [])


def clear_pending_reviews():
    """Clear all pending reviews (after they've been reviewed)"""
    
    if os.path.exists(PENDING_FILE):
        os.remove(PENDING_FILE)


def get_pending_count():
    """Get count of jobs waiting for review"""
    
    if not os.path.exists(PENDING_FILE):
        return 0
    
    with open(PENDING_FILE, "r") as f:
        pending = json.load(f)
    
    return len(pending.get('jobs', []))


# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "count":
        count = get_pending_count()
        print(f"Jobs waiting for review: {count}")
    elif len(sys.argv) > 1 and sys.argv[1] == "clear":
        clear_pending_reviews()
        print("Cleared all pending reviews")
    else:
        pending = load_pending_reviews()
        print(f"\nPending Reviews: {len(pending)}\n")
        
        for i, job in enumerate(pending[:5], 1):
            print(f"{i}. {job['title']} - {job['company']}")
        
        if len(pending) > 5:
            print(f"... and {len(pending) - 5} more")
        print()
