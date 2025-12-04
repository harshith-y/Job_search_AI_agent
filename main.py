#!/usr/bin/env python3
"""
Main Job Search Script
Uses Universal Scraper + Google Search + Claude Filtering + GUI Review
"""

import sys
from scrapers import find_all_industry_jobs, find_all_phd_positions
from agent_claude import filter_industry_job, filter_phd_position
from memory import is_new_job, mark_as_seen
from notifier import send_discord_notification
from tracker import EnhancedJobTracker
from review_gui import start_review_server


def main(search_type="both"):
    """
    Main job search function
    
    Args:
        search_type: "industry", "phd", or "both"
    """
    
    print("\n" + "="*70)
    print("🎯 JOB SEARCH AGENT - UNIVERSAL SCRAPER EDITION")
    print("="*70 + "\n")
    
    all_relevant_jobs = []
    tracker = EnhancedJobTracker()
    
    # ========================================================================
    # INDUSTRY JOBS
    # ========================================================================
    
    if search_type in ["both", "industry"]:
        print("💼 SEARCHING FOR INDUSTRY ML/AI JOBS...")
        print("-" * 70 + "\n")
        
        # Find jobs using universal scraper + Google Search
        industry_jobs = find_all_industry_jobs()
        
        if not industry_jobs:
            print("⚠️  No industry jobs found")
        else:
            # Filter with Claude
            print(f"\n🤖 Filtering {len(industry_jobs)} jobs with Claude AI...")
            print("   (Using your preferences from user_preferences.py)")
            print()
            
            relevant_count = 0
            
            for i, job in enumerate(industry_jobs, 1):
                # Check if new
                if not is_new_job(job['url']):
                    continue
                
                # Filter with Claude
                print(f"   [{i}/{len(industry_jobs)}] {job['title'][:50]}... ", end="")
                
                try:
                    is_relevant, info = filter_industry_job(job)
                    
                    if is_relevant:
                        print("✅ MATCH")
                        
                        # Add AI analysis
                        job['ai_summary'] = info.get('summary', '')
                        job['ai_analysis'] = info.get('full_analysis', '')
                        job['job_type'] = 'Industry'
                        
                        # Add to tracker and results
                        tracker.add_job(job, status='new')
                        all_relevant_jobs.append(job)
                        
                        # Mark as seen
                        mark_as_seen(job['url'])
                        
                        relevant_count += 1
                    else:
                        print("⏭  Skip")
                
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            print(f"\n   ✅ Found {relevant_count} relevant industry jobs\n")
    
    # ========================================================================
    # PHD POSITIONS
    # ========================================================================
    
    if search_type in ["both", "phd"]:
        print("🎓 SEARCHING FOR PHD POSITIONS...")
        print("-" * 70 + "\n")
        
        # Find PhD positions using universal scraper + Google Search
        phd_positions = find_all_phd_positions()
        
        if not phd_positions:
            print("⚠️  No PhD positions found")
        else:
            # Filter with Claude
            print(f"\n🤖 Filtering {len(phd_positions)} positions with Claude AI...")
            print("   (Using your preferences from user_preferences.py)")
            print()
            
            relevant_count = 0
            
            for i, position in enumerate(phd_positions, 1):
                # Check if new
                if not is_new_job(position['url']):
                    continue
                
                # Filter with Claude
                print(f"   [{i}/{len(phd_positions)}] {position['title'][:50]}... ", end="")
                
                try:
                    is_relevant, info = filter_phd_position(position)
                    
                    if is_relevant:
                        print("✅ MATCH")
                        
                        # Add AI analysis
                        position['ai_summary'] = info.get('summary', '')
                        position['ai_analysis'] = str(info)
                        position['job_type'] = 'PhD'
                        position['funding_status'] = info.get('funding_status', 'Unknown')
                        
                        # Add to tracker and results
                        tracker.add_job(position, status='new')
                        all_relevant_jobs.append(position)
                        
                        # Mark as seen
                        mark_as_seen(position['url'])
                        
                        relevant_count += 1
                    else:
                        print("⏭  Skip")
                
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            print(f"\n   ✅ Found {relevant_count} relevant PhD positions\n")
    
    # ========================================================================
    # RESULTS
    # ========================================================================
    
    print("="*70)
    print("📊 SEARCH COMPLETE")
    print("="*70 + "\n")
    
    if not all_relevant_jobs:
        print("❌ No relevant jobs found this time")
        print("\nSuggestions:")
        print("  • Check user_preferences.py (maybe too strict?)")
        print("  • Try different search queries in config.yaml")
        print("  • Add more job sources to config.yaml")
        print()
        return
    
    print(f"✅ Found {len(all_relevant_jobs)} relevant opportunities:")
    
    industry_count = len([j for j in all_relevant_jobs if j.get('job_type') == 'Industry'])
    phd_count = len([j for j in all_relevant_jobs if j.get('job_type') == 'PhD'])
    
    print(f"   💼 Industry: {industry_count}")
    print(f"   🎓 PhD: {phd_count}")
    print()
    
    # Send Discord notification
    try:
        print("📱 Sending Discord notification...")
        send_discord_notification(all_relevant_jobs)
        print("   ✅ Notification sent\n")
    except Exception as e:
        print(f"   ⚠️  Could not send notification: {e}\n")
    
    # Export to spreadsheet
    print("📊 Updating spreadsheet...")
    tracker.export_to_excel_fancy()
    print()
    
    # Launch GUI for review
    print("="*70)
    print("🎨 LAUNCHING REVIEW GUI")
    print("="*70 + "\n")
    
    print("Opening web interface in your browser...")
    print("Review each job with Like/Maybe/Pass buttons!")
    print("\nPress Ctrl+C to skip GUI and exit\n")
    
    try:
        start_review_server(all_relevant_jobs, port=5000)
    except KeyboardInterrupt:
        print("\n\n⚠️  GUI skipped")
    
    print("\n" + "="*70)
    print("✅ JOB SEARCH COMPLETE")
    print("="*70)
    
    print(f"\n📊 Results saved to:")
    print(f"   • job_applications_enhanced.xlsx (spreadsheet)")
    print(f"   • job_tracker_enhanced.json (database)")
    print()
    
    print("Next steps:")
    print("  1. Review spreadsheet for detailed info")
    print("  2. Update 'Status' column with dropdowns")
    print("  3. Add notes for jobs you like")
    print("  4. Mark when you apply!")
    print()


if __name__ == "__main__":
    # Parse command line arguments
    if len(sys.argv) > 1:
        search_type = sys.argv[1].lower()
        if search_type not in ["industry", "phd", "both"]:
            print("Usage: python main.py [industry|phd|both]")
            print("Example: python main.py industry")
            sys.exit(1)
    else:
        search_type = "both"
    
    try:
        main(search_type)
    except KeyboardInterrupt:
        print("\n\n⚠️  Search interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("  • Check that all required files exist")
        print("  • Check .env file has API keys")
        print("  • Check internet connection")
        print("  • Try: pip install -r requirements.txt")