#!/usr/bin/env python3
"""
Job Search Agent - Main Entry Point
Searches for BOTH industry jobs AND PhD positions
Includes interactive review system with like/dislike/maybe
Uses Claude Sonnet 4 for filtering
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Import components
from memory import load_memory, is_new_job, update_memory
from agent_claude import filter_industry_job, filter_phd_position
from scrapers import find_all_industry_jobs, find_all_phd_positions
from notifier import send_discord_notification
from tracker import JobTracker
from review_gui import start_review_server

load_dotenv()


def search_industry_jobs():
    """Search for industry ML/AI jobs"""
    print(f"\n{'='*60}")
    print(f"💼 INDUSTRY JOB SEARCH")
    print(f"{'='*60}\n")
    
    # Find jobs (scraping + search)
    all_jobs = find_all_industry_jobs()
    print(f"✅ Total jobs found: {len(all_jobs)}")
    
    if not all_jobs:
        print("⚠️  No jobs found")
        return []
    
    # Filter for new
    seen = load_memory()
    new_jobs = [job for job in all_jobs if is_new_job(job['url'])]
    print(f"🆕 New jobs: {len(new_jobs)}")
    
    if not new_jobs:
        print("✨ No new jobs - all caught up!")
        return []
    
    # AI filtering
    print(f"\n🤖 Filtering with Claude Sonnet 4...")
    relevant_jobs = []
    
    for i, job in enumerate(new_jobs, 1):
        print(f"  [{i}/{len(new_jobs)}] {job['title'][:50]}...", end=" ")
        
        try:
            is_relevant, info = filter_industry_job(job)
            
            if is_relevant:
                job["ai_summary"] = info["summary"]
                relevant_jobs.append(job)
                print("✅")
            else:
                print("⏭️")
        
        except Exception as e:
            print(f"❌")
            continue
    
    # Update memory
    update_memory([job['url'] for job in new_jobs])
    
    print(f"\n💾 Updated memory: {len(new_jobs)} jobs")
    print(f"✅ Relevant jobs: {len(relevant_jobs)}")
    
    return relevant_jobs


def search_phd_positions():
    """Search for PhD positions"""
    print(f"\n{'='*60}")
    print(f"🎓 PhD POSITION SEARCH")
    print(f"{'='*60}\n")
    
    # Find positions (Google search)
    all_positions = find_all_phd_positions()
    
    if not all_positions:
        print("⚠️  No positions found")
        return []
    
    # Load PhD memory
    phd_memory_file = "seen_phds.txt"
    if os.path.exists(phd_memory_file):
        with open(phd_memory_file, "r") as f:
            seen_phds = set(line.strip() for line in f if line.strip())
    else:
        seen_phds = set()
        open(phd_memory_file, "w").close()
    
    # Filter for new
    new_positions = [p for p in all_positions if p['url'] not in seen_phds]
    print(f"🆕 New positions: {len(new_positions)}")
    
    if not new_positions:
        print("✨ No new positions - all caught up!")
        return []
    
    # AI filtering
    print(f"\n🤖 Filtering with Claude Sonnet 4...")
    relevant_positions = []
    
    for i, phd in enumerate(new_positions, 1):
        print(f"  [{i}/{len(new_positions)}] {phd['title'][:50]}...", end=" ")
        
        try:
            is_relevant, info = filter_phd_position(phd)
            
            if is_relevant:
                phd["ai_info"] = info
                phd["ai_summary"] = info.get("summary", "")
                relevant_positions.append(phd)
                
                funding = info.get('funding_status', 'Unknown')
                if 'FUNDED' in funding.upper():
                    print("✅ 💰")
                elif 'UNCLEAR' in funding.upper():
                    print("⚠️ 💰?")
                else:
                    print("❌")
            else:
                print("⏭️")
        
        except Exception as e:
            print(f"❌")
            continue
    
    # Update memory
    with open(phd_memory_file, "a") as f:
        for phd in new_positions:
            f.write(phd['url'] + "\n")
    
    print(f"\n💾 Updated memory: {len(new_positions)} positions")
    print(f"✅ Relevant positions: {len(relevant_positions)}")
    
    return relevant_positions


def main():
    """Main workflow"""
    
    print(f"\n{'#'*60}")
    print(f"# JOB SEARCH AGENT")
    print(f"# {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'#'*60}")
    
    # Determine what to search
    if len(sys.argv) > 1:
        search_type = sys.argv[1].lower()
    else:
        search_type = "both"  # Default: search both
    
    industry_jobs = []
    phd_positions = []
    
    # Search based on argument
    if search_type in ["both", "industry"]:
        industry_jobs = search_industry_jobs()
    
    if search_type in ["both", "phd"]:
        phd_positions = search_phd_positions()
    
    # Combine results
    all_relevant = industry_jobs + phd_positions
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY")
    print(f"{'='*60}")
    print(f"💼 Industry jobs: {len(industry_jobs)}")
    print(f"🎓 PhD positions: {len(phd_positions)}")
    print(f"📌 Total relevant: {len(all_relevant)}")
    print(f"{'='*60}\n")
    
    if not all_relevant:
        print("✨ No new opportunities found today!\n")
        return
    
    # Send notifications
    if os.getenv("DISCORD_WEBHOOK_URL"):
        try:
            send_discord_notification(all_relevant)
            print("✅ Discord notification sent")
        except Exception as e:
            print(f"⚠️  Discord error: {e}")
    
    # Interactive review
    print(f"\n💡 Ready to review jobs?")
    choice = input("   Start web review interface? [Y/n]: ").strip().lower()
    
    if choice != 'n':
        print(f"\n🌐 Starting web interface...")
        start_review_server(all_relevant)
    else:
        print("\n✅ Jobs saved to memory. Run 'python tracker.py export' to see them.")
        # Still export to spreadsheet
        tracker = JobTracker()
        for job in all_relevant:
            tracker.add_job(job, status="new")
        tracker.export_to_excel()
    
    print("\n✅ Search complete!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)