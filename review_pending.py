#!/usr/bin/env python3
"""
Review Pending Jobs
Opens the web GUI to review jobs found from remote searches
"""

from pending_review import load_pending_reviews, clear_pending_reviews, get_pending_count
from review_gui import start_review_server

def main():
    """Load pending reviews and launch GUI"""
    
    print(f"\n{'='*60}")
    print(f"📋 PENDING JOB REVIEW")
    print(f"{'='*60}\n")
    
    # Load pending jobs
    pending_jobs = load_pending_reviews()
    count = len(pending_jobs)
    
    if count == 0:
        print("✨ No jobs waiting for review!")
        print("\nEither:")
        print("  • No search has been run yet")
        print("  • All jobs have been reviewed")
        print("  • Run: python main.py (to search)")
        print("  • Or trigger remotely via API\n")
        return
    
    print(f"Found {count} jobs waiting for review:\n")
    
    # Show preview
    for i, job in enumerate(pending_jobs[:5], 1):
        job_type = "💼" if job.get('job_type') == 'Industry' else "🎓"
        print(f"{i}. {job_type} {job['title']} - {job['company']}")
    
    if count > 5:
        print(f"... and {count - 5} more")
    
    print(f"\n{'='*60}")
    print(f"🌐 Opening web interface for review...")
    print(f"{'='*60}\n")
    
    # Launch GUI
    try:
        start_review_server(pending_jobs, port=5000)
        
        # After review completes, clear pending
        print("\n✅ Review complete! Clearing pending reviews...")
        clear_pending_reviews()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Review interrupted")
        choice = input("Clear pending reviews anyway? [y/N]: ").strip().lower()
        if choice == 'y':
            clear_pending_reviews()
            print("✅ Cleared pending reviews")
    
    print("\n✅ Done!\n")


if __name__ == "__main__":
    main()
