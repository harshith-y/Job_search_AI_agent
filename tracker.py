"""
Enhanced Job Tracker with Fancy Excel Formatting
- Color-coded dropdowns for Status
- Additional detailed columns
- Progress tracking dropdown
- Professional formatting
"""

import json
import os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation


class EnhancedJobTracker:
    """Enhanced job tracker with detailed information and fancy Excel export"""
    
    def __init__(self, filename="job_tracker_enhanced.json"):
        self.filename = filename
        self.jobs = self.load()
    
    def load(self):
        """Load jobs from JSON"""
        if os.path.exists(self.filename):
            with open(self.filename, "r") as f:
                return json.load(f)
        return {}
    
    def save(self):
        """Save jobs to JSON"""
        with open(self.filename, "w") as f:
            json.dump(self.jobs, f, indent=2)
    
    def add_job(self, job, status="new"):
        """Add a job with all details"""
        
        url = job["url"]
        
        if url in self.jobs:
            # Update existing
            self.jobs[url].update({
                "status": status,
                "last_updated": datetime.now().isoformat()
            })
        else:
            # Add new
            self.jobs[url] = {
                "title": job["title"],
                "company": job["company"],
                "location": job.get("location", "UK"),
                "city": job.get("city", job.get("location", "UK")),  # NEW
                "type": job.get("job_type", job.get("type", "Industry")),
                "url": url,
                "description": job.get("description", ""),
                "ai_summary": job.get("ai_summary", ""),
                "status": status,
                "date_found": datetime.now().strftime("%Y-%m-%d"),
                "applied_date": None,
                "response": "Not Applied",
                "notes": "",
                # NEW FIELDS:
                "requirements": job.get("requirements", []),
                "expectations": job.get("expectations", []),
                "salary": job.get("salary", "Not specified"),
                "post_date": job.get("post_date", "Recent"),
                "deadline": job.get("deadline", "Not specified"),
                "cv_required": job.get("cv_required", "Not specified"),
                "cover_letter_required": job.get("cover_letter_required", "Not specified"),
            }
        
        self.save()
    
    def update_status(self, url, status):
        """Update job status"""
        if url in self.jobs:
            self.jobs[url]["status"] = status
            self.jobs[url]["last_updated"] = datetime.now().isoformat()
            self.save()
    
    def get_jobs_by_status(self, status):
        """Get all jobs with specific status"""
        return [job for job in self.jobs.values() if job["status"] == status]
    
    def export_to_excel_fancy(self, filename="job_applications_enhanced.xlsx"):
        """
        Export to Excel with FANCY formatting:
        - Color-coded dropdown for Status
        - Progress dropdown for Response
        - Professional styling
        - All detailed columns
        """
        
        # Check if file exists
        if os.path.exists(filename):
            print(f"📊 Updating existing spreadsheet: {filename}")
            wb = load_workbook(filename)
            ws = wb.active
            
            # Get existing URLs to avoid duplicates
            existing_urls = set()
            for row in range(2, ws.max_row + 1):
                url = ws.cell(row=row, column=15).value  # URL column
                if url:
                    existing_urls.add(url)
            
            # Add only new jobs
            row_num = ws.max_row + 1
            new_count = 0
            
            for url, job in self.jobs.items():
                if url not in existing_urls:
                    self._add_job_row_fancy(ws, row_num, job)
                    row_num += 1
                    new_count += 1
                else:
                    # Update status if changed
                    for row in range(2, ws.max_row + 1):
                        if ws.cell(row=row, column=15).value == url:
                            self._update_status_cell(ws, row, job["status"])
                            break
            
            print(f"   ✅ Added {new_count} new jobs")
            print(f"   ✅ Updated statuses for existing jobs")
        
        else:
            print(f"📊 Creating new spreadsheet: {filename}")
            wb = Workbook()
            ws = wb.active
            ws.title = "Job Applications"
            
            # Create header row
            self._create_fancy_header(ws)
            
            # Add all jobs
            row_num = 2
            for url, job in self.jobs.items():
                self._add_job_row_fancy(ws, row_num, job)
                row_num += 1
            
            print(f"   ✅ Added {len(self.jobs)} jobs")
        
        # Add dropdowns and formatting
        self._add_fancy_dropdowns(ws)
        self._auto_fit_columns(ws)
        
        # Save
        wb.save(filename)
        print(f"✅ Spreadsheet saved: {filename}\n")
        
        return filename
    
    def _create_fancy_header(self, ws):
        """Create professional header row with styling"""
        
        headers = [
            "Date Found", "Status", "Title", "Company", "City", "Country", 
            "Type", "Salary", "Post Date", "Deadline", 
            "Applied Date", "Response", "Progress", "Notes", "URL",
            "Requirements", "Expectations", "CV Required", "Cover Letter"
        ]
        
        # Header styling
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF", size=11)
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
        
        # Set row height
        ws.row_dimensions[1].height = 25
    
    def _add_job_row_fancy(self, ws, row_num, job):
        """Add a job row with all details"""
        
        # Get status emoji
        status_emoji = {
            "new": "🆕",
            "liked": "👍",
            "maybe": "🤔",
            "disliked": "👎",
            "applied": "📤",
            "interview": "🎤",
            "offer": "🎉",
            "rejected": "❌"
        }.get(job["status"], "")
        
        # Format requirements and expectations
        requirements = ", ".join(job.get("requirements", [])[:5]) if job.get("requirements") else "See listing"
        expectations = " | ".join(job.get("expectations", [])[:3]) if job.get("expectations") else "See listing"
        
        # Data
        row_data = [
            job["date_found"],
            f"{status_emoji} {job['status'].title()}",
            job["title"],
            job["company"],
            job.get("city", job.get("location", "UK")),
            job.get("location", "UK"),
            job["type"],
            job.get("salary", "Not specified"),
            job.get("post_date", "Recent"),
            job.get("deadline", "Not specified"),
            job.get("applied_date", ""),
            job.get("response", "Not Applied"),
            "",  # Progress (will be dropdown)
            job.get("notes", ""),
            job["url"],
            requirements,
            expectations,
            job.get("cv_required", "Not specified"),
            job.get("cover_letter_required", "Not specified"),
        ]
        
        # Add data to row
        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        
        # Color-code status cell
        self._color_status_cell(ws, row_num, job["status"])
    
    def _color_status_cell(self, ws, row_num, status):
        """Apply color to status cell based on status"""
        
        status_colors = {
            "liked": "C6EFCE",      # Light green
            "disliked": "FFC7CE",   # Light red
            "maybe": "FFEB9C",      # Light yellow/beige
            "applied": "BDD7EE",    # Light blue
            "interview": "B4C7E7",  # Blue
            "offer": "00B050",      # Dark green
            "rejected": "FF0000",   # Red
            "new": "F2F2F2",        # Light gray
        }
        
        color = status_colors.get(status, "FFFFFF")
        cell = ws.cell(row=row_num, column=2)  # Status column
        cell.fill = PatternFill(start_color=color, end_color=color, fill_type="solid")
        
        # Bold font for status
        cell.font = Font(bold=True)
    
    def _update_status_cell(self, ws, row_num, status):
        """Update status cell with new status and color"""
        
        status_emoji = {
            "new": "🆕",
            "liked": "👍",
            "maybe": "🤔",
            "disliked": "👎",
            "applied": "📤",
            "interview": "🎤",
            "offer": "🎉",
            "rejected": "❌"
        }.get(status, "")
        
        cell = ws.cell(row=row_num, column=2)
        cell.value = f"{status_emoji} {status.title()}"
        
        # Update color
        self._color_status_cell(ws, row_num, status)
    
    def _add_fancy_dropdowns(self, ws):
        """Add color-coded dropdowns for Status and Progress"""
        
        # Status dropdown (column B)
        status_options = '"🆕 New,👍 Liked,🤔 Maybe,👎 Disliked,📤 Applied,🎤 Interview,🎉 Offer,❌ Rejected"'
        status_dv = DataValidation(type="list", formula1=status_options, allow_blank=False)
        status_dv.error = "Invalid status"
        status_dv.errorTitle = "Invalid Entry"
        ws.add_data_validation(status_dv)
        status_dv.add(f"B2:B{ws.max_row}")
        
        # Progress dropdown (column M)
        progress_options = '"Not Started,Researching,Preparing Application,Ready to Apply,Applied - Waiting,Interview Scheduled,Awaiting Decision,Offer Received,Accepted,Declined,Rejected"'
        progress_dv = DataValidation(type="list", formula1=progress_options, allow_blank=True)
        progress_dv.error = "Invalid progress"
        progress_dv.errorTitle = "Invalid Entry"
        ws.add_data_validation(progress_dv)
        progress_dv.add(f"M2:M{ws.max_row}")
    
    def _auto_fit_columns(self, ws):
        """Auto-fit column widths"""
        
        column_widths = {
            "A": 12,   # Date Found
            "B": 15,   # Status
            "C": 40,   # Title
            "D": 25,   # Company
            "E": 15,   # City
            "F": 12,   # Country
            "G": 10,   # Type
            "H": 15,   # Salary
            "I": 12,   # Post Date
            "J": 15,   # Deadline
            "K": 12,   # Applied Date
            "L": 20,   # Response
            "M": 20,   # Progress
            "N": 30,   # Notes
            "O": 50,   # URL
            "P": 40,   # Requirements
            "Q": 50,   # Expectations
            "R": 12,   # CV Required
            "S": 15,   # Cover Letter
        }
        
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width


# CLI Interface
if __name__ == "__main__":
    import sys
    
    tracker = EnhancedJobTracker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "export":
            tracker.export_to_excel_fancy()
        
        elif command == "stats":
            print("\n📊 Job Tracker Stats:\n")
            print(f"   Total jobs: {len(tracker.jobs)}")
            print(f"   👍 Liked: {len(tracker.get_jobs_by_status('liked'))}")
            print(f"   🤔 Maybe: {len(tracker.get_jobs_by_status('maybe'))}")
            print(f"   👎 Disliked: {len(tracker.get_jobs_by_status('disliked'))}")
            print(f"   📤 Applied: {len(tracker.get_jobs_by_status('applied'))}")
            print(f"   🎤 Interview: {len(tracker.get_jobs_by_status('interview'))}")
            print(f"   🎉 Offer: {len(tracker.get_jobs_by_status('offer'))}")
            print()
        
        elif command == "add":
            # Manual entry
            print("\n➕ Add Manual Job Entry\n")
            
            title = input("Job Title: ")
            company = input("Company: ")
            city = input("City: ")
            location = input("Country [UK]: ") or "UK"
            url = input("URL: ")
            job_type = input("Type (Industry/PhD) [Industry]: ") or "Industry"
            salary = input("Salary [Not specified]: ") or "Not specified"
            deadline = input("Deadline [Not specified]: ") or "Not specified"
            notes = input("Notes: ")
            
            job = {
                "title": title,
                "company": company,
                "location": location,
                "city": city,
                "url": url,
                "type": job_type,
                "job_type": job_type,
                "salary": salary,
                "deadline": deadline,
                "notes": notes,
                "requirements": [],
                "expectations": [],
                "post_date": "Today",
                "cv_required": "Not specified",
                "cover_letter_required": "Not specified",
            }
            
            tracker.add_job(job, status="new")
            tracker.export_to_excel_fancy()
            
            print("\n✅ Job added and spreadsheet updated!\n")
    
    else:
        print("\nUsage:")
        print("  python tracker_enhanced.py export  - Export to Excel")
        print("  python tracker_enhanced.py stats   - View statistics")
        print("  python tracker_enhanced.py add     - Add manual entry")
        print()