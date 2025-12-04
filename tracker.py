"""
Job Tracker - Review, Like/Dislike, and Track Applications
Generates Excel spreadsheet with all your job applications
"""

import os
import json
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

TRACKER_FILE = "job_tracker.json"
SPREADSHEET_FILE = "job_applications.xlsx"


class JobTracker:
    """Track job applications with like/dislike/maybe status"""
    
    def __init__(self):
        self.jobs = self.load_tracker()
    
    def load_tracker(self):
        """Load existing tracked jobs"""
        if os.path.exists(TRACKER_FILE):
            with open(TRACKER_FILE, "r") as f:
                return json.load(f)
        return {}
    
    def save_tracker(self):
        """Save tracked jobs to file"""
        with open(TRACKER_FILE, "w") as f:
            json.dump(self.jobs, f, indent=2)
    
    def add_job(self, job, status="new"):
        """Add or update a job"""
        job_id = job['url']
        
        self.jobs[job_id] = {
            "date_found": datetime.now().strftime("%Y-%m-%d"),
            "status": status,  # new, liked, maybe, disliked, applied, interview, offer, rejected
            "title": job['title'],
            "company": job['company'],
            "location": job['location'],
            "url": job['url'],
            "type": job.get('job_type', 'Industry'),
            "description": job.get('description', '')[:500],  # First 500 chars
            "ai_summary": job.get('ai_summary', '')[:300],
            "notes": "",
            "applied_date": None,
            "response_date": None,
            "response_status": None
        }
        
        self.save_tracker()
    
    def update_status(self, job_url, status, notes=""):
        """Update job status"""
        if job_url in self.jobs:
            self.jobs[job_url]["status"] = status
            if notes:
                self.jobs[job_url]["notes"] = notes
            if status == "applied":
                self.jobs[job_url]["applied_date"] = datetime.now().strftime("%Y-%m-%d")
            self.save_tracker()
    
    def get_jobs_by_status(self, status):
        """Get all jobs with specific status"""
        return [job for job in self.jobs.values() if job["status"] == status]
    
    def export_to_excel(self):
        """Update existing Excel spreadsheet (or create if doesn't exist)"""
        
        # Load or create workbook
        if os.path.exists(SPREADSHEET_FILE):
            wb = load_workbook(SPREADSHEET_FILE)
            ws = wb.active
            print(f"📊 Updating existing spreadsheet: {SPREADSHEET_FILE}")
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Job Applications"
            
            # Create headers
            headers = [
                "Date Found", "Status", "Title", "Company", "Location", 
                "Type", "Applied Date", "Response", "Notes", "URL"
            ]
            ws.append(headers)
            
            # Style headers
            for cell in ws[1]:
                cell.font = Font(bold=True, size=12)
                cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
                cell.font = Font(bold=True, color="FFFFFF")
                cell.alignment = Alignment(horizontal="center")
            
            print(f"📊 Created new spreadsheet: {SPREADSHEET_FILE}")
        
        # Get existing URLs to avoid duplicates
        existing_urls = set()
        for row in range(2, ws.max_row + 1):
            url_cell = ws.cell(row=row, column=10).value
            if url_cell:
                existing_urls.add(url_cell)
        
        # Add NEW jobs only
        new_jobs_added = 0
        for job in self.jobs.values():
            if job['url'] not in existing_urls:
                status_emoji = {
                    "new": "🆕",
                    "liked": "👍",
                    "maybe": "🤔",
                    "disliked": "👎",
                    "applied": "📤",
                    "interview": "🎤",
                    "offer": "🎉",
                    "rejected": "❌"
                }.get(job["status"], "❓")
                
                row = [
                    job["date_found"],
                    f"{status_emoji} {job['status'].title()}",
                    job["title"],
                    job["company"],
                    job["location"],
                    job["type"],
                    job.get("applied_date", ""),
                    job.get("response_status", ""),
                    job.get("notes", ""),
                    job["url"]
                ]
                ws.append(row)
                new_jobs_added += 1
        
        # Update EXISTING jobs if status changed
        for row_idx in range(2, ws.max_row + 1):
            url = ws.cell(row=row_idx, column=10).value
            if url and url in self.jobs:
                job = self.jobs[url]
                status_emoji = {
                    "new": "🆕",
                    "liked": "👍",
                    "maybe": "🤔",
                    "disliked": "👎",
                    "applied": "📤",
                    "interview": "🎤",
                    "offer": "🎉",
                    "rejected": "❌"
                }.get(job["status"], "❓")
                
                # Update status column
                ws.cell(row=row_idx, column=2).value = f"{status_emoji} {job['status'].title()}"
                
                # Update applied date if exists
                if job.get("applied_date"):
                    ws.cell(row=row_idx, column=7).value = job["applied_date"]
                
                # Update response if exists
                if job.get("response_status"):
                    ws.cell(row=row_idx, column=8).value = job["response_status"]
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Save
        wb.save(SPREADSHEET_FILE)
        
        if new_jobs_added > 0:
            print(f"✅ Added {new_jobs_added} new jobs to spreadsheet")
        else:
            print(f"✅ Spreadsheet updated (no new jobs to add)")
        
        return SPREADSHEET_FILE
    
    def add_manual_entry(self, title, company, location, url, job_type="Industry", notes=""):
        """Manually add a job (e.g., from LinkedIn) that wasn't scraped"""
        
        # Create manual job entry
        manual_job = {
            'title': title,
            'company': company,
            'location': location,
            'url': url,
            'job_type': job_type,
            'description': 'Manually added',
            'ai_summary': notes
        }
        
        # Add to tracker
        self.add_job(manual_job, status="new")
        print(f"✅ Manually added: {title} at {company}")
        
        # Export to update spreadsheet
        self.export_to_excel()
        
        return manual_job


def review_jobs_interactive(jobs):
    """Interactive terminal review of new jobs"""
    
    tracker = JobTracker()
    
    print(f"\n{'='*70}")
    print(f"📋 JOB REVIEW - {len(jobs)} new jobs to review")
    print(f"{'='*70}\n")
    
    for i, job in enumerate(jobs, 1):
        print(f"\n{'─'*70}")
        print(f"Job {i} of {len(jobs)}")
        print(f"{'─'*70}\n")
        
        print(f"📌 {job['title']}")
        print(f"🏢 {job['company']}")
        print(f"📍 {job['location']}")
        print(f"🔗 {job['url']}\n")
        
        if 'ai_summary' in job:
            summary = job['ai_summary'][:200] + "..." if len(job['ai_summary']) > 200 else job['ai_summary']
            print(f"💡 {summary}\n")
        
        while True:
            choice = input("👍 [L]ike  🤔 [M]aybe  👎 [D]islike  ⏭️ [S]kip  ❌ [Q]uit? ").strip().lower()
            
            if choice == 'l':
                tracker.add_job(job, status="liked")
                print("✅ Marked as LIKED")
                break
            elif choice == 'm':
                tracker.add_job(job, status="maybe")
                print("✅ Marked as MAYBE")
                break
            elif choice == 'd':
                tracker.add_job(job, status="disliked")
                print("✅ Marked as DISLIKED")
                break
            elif choice == 's':
                tracker.add_job(job, status="new")
                print("⏭️ Skipped (marked as NEW)")
                break
            elif choice == 'q':
                print("\n👋 Exiting review...")
                tracker.export_to_excel()
                return
            else:
                print("❌ Invalid choice. Try again.")
    
    print(f"\n{'='*70}")
    print(f"✅ Review complete!")
    print(f"{'='*70}\n")
    
    # Export to Excel
    tracker.export_to_excel()
    
    # Show summary
    liked = tracker.get_jobs_by_status("liked")
    maybe = tracker.get_jobs_by_status("maybe")
    
    print(f"\n📊 Summary:")
    print(f"   👍 Liked: {len(liked)}")
    print(f"   🤔 Maybe: {len(maybe)}")
    print(f"\n💡 Next steps:")
    print(f"   1. Open {SPREADSHEET_FILE} to see all jobs")
    print(f"   2. Add notes and track applications")
    print(f"   3. Update status as you apply/hear back\n")


# Quick command-line interface
if __name__ == "__main__":
    import sys
    
    tracker = JobTracker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "export":
            tracker.export_to_excel()
            print(f"✅ Exported to {SPREADSHEET_FILE}")
        
        elif command == "stats":
            print(f"\n📊 Job Tracker Stats:")
            print(f"   Total jobs tracked: {len(tracker.jobs)}")
            print(f"   👍 Liked: {len(tracker.get_jobs_by_status('liked'))}")
            print(f"   🤔 Maybe: {len(tracker.get_jobs_by_status('maybe'))}")
            print(f"   👎 Disliked: {len(tracker.get_jobs_by_status('disliked'))}")
            print(f"   📤 Applied: {len(tracker.get_jobs_by_status('applied'))}")
            print(f"   🎤 Interview: {len(tracker.get_jobs_by_status('interview'))}")
            print(f"   🎉 Offer: {len(tracker.get_jobs_by_status('offer'))}")
            print()
        
        elif command == "liked":
            liked = tracker.get_jobs_by_status("liked")
            print(f"\n👍 Liked Jobs ({len(liked)}):\n")
            for i, job in enumerate(liked, 1):
                print(f"{i}. {job['title']} - {job['company']}")
                print(f"   {job['url']}\n")
        
        elif command == "add":
            # Manual entry
            print("\n➕ Add Manual Job Entry")
            print("(For jobs from LinkedIn, etc. that weren't scraped)\n")
            
            title = input("Job Title: ").strip()
            company = input("Company: ").strip()
            location = input("Location: ").strip()
            url = input("URL: ").strip()
            job_type = input("Type [Industry/PhD] (default: Industry): ").strip() or "Industry"
            notes = input("Notes (optional): ").strip()
            
            if title and company and url:
                tracker.add_manual_entry(title, company, location, url, job_type, notes)
            else:
                print("❌ Title, company, and URL are required")
        
        else:
            print("Usage: python tracker.py [export|stats|liked|add]")
            print("  export - Export to Excel")
            print("  stats  - Show statistics")
            print("  liked  - Show liked jobs")
            print("  add    - Manually add a job (e.g., from LinkedIn)")
    else:
        print(f"\n📋 Job Tracker")
        print(f"   Total jobs: {len(tracker.jobs)}")
        print(f"\nCommands:")
        print(f"   python tracker.py export  # Export to Excel")
        print(f"   python tracker.py stats   # Show statistics")
        print(f"   python tracker.py liked   # Show liked jobs")
        print(f"   python tracker.py add     # Manually add a job")
        print()