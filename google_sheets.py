"""
Google Sheets Integration - Sync jobs to your Google Drive spreadsheet

Setup:
1. Go to https://console.cloud.google.com/
2. Create a new project (or select existing)
3. Enable the Google Sheets API
4. Create credentials:
   - Option A (Service Account - recommended for automation):
     - Create a Service Account
     - Download JSON key file
     - Save as 'google_credentials.json' in project root
     - Share your Google Sheet with the service account email

   - Option B (OAuth - for personal use):
     - Create OAuth 2.0 Client ID (Desktop app)
     - Download JSON and save as 'google_credentials.json'
     - First run will open browser for authentication

5. Add to .env:
   GOOGLE_SHEET_ID=your_spreadsheet_id_from_url
   (The ID is the long string in your sheet URL between /d/ and /edit)
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False
    print("Note: gspread not installed. Run: pip install gspread google-auth")

from dotenv import load_dotenv

load_dotenv()


class GoogleSheetsSync:
    """Sync job tracker data to Google Sheets"""

    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]

    # Column headers matching tracker.py format
    HEADERS = [
        "Company Name",        # A
        "Application Status",  # B
        "Role",               # C
        "Salary",             # D
        "Date Submitted",     # E
        "Link to Job Req",    # F
        "Rejection Reason",   # G
        "Location",           # H
        "Deadline",           # I
        "Notes",              # J
        "AI Summary",         # K
    ]

    # Status colors for conditional formatting (RGB values)
    STATUS_COLORS = {
        "Submitted - Pending Response": {"red": 0.298, "green": 0.686, "blue": 0.314},  # Green
        "Have Not Applied": {"red": 0.392, "green": 0.710, "blue": 0.965},              # Blue
        "Interview Scheduled": {"red": 0.506, "green": 0.780, "blue": 0.518},           # Light green
        "Offer Received": {"red": 0.180, "green": 0.490, "blue": 0.196},                # Dark green
        "Rejected": {"red": 0.898, "green": 0.451, "blue": 0.451},                      # Red
        "N/A": {"red": 0.620, "green": 0.620, "blue": 0.620},                           # Grey
    }

    def __init__(self, credentials_path: str = "google_credentials.json"):
        """Initialize Google Sheets connection"""

        if not GSPREAD_AVAILABLE:
            raise ImportError("gspread not installed. Run: pip install gspread google-auth")

        self.credentials_path = credentials_path
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
        self.client = None
        self.spreadsheet = None
        self.worksheet = None

        if not self.sheet_id:
            print("Warning: GOOGLE_SHEET_ID not set in .env")

    def connect(self) -> bool:
        """Connect to Google Sheets API"""

        if not os.path.exists(self.credentials_path):
            print(f"Error: Credentials file not found: {self.credentials_path}")
            print("\nTo set up Google Sheets integration:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a project and enable Google Sheets API")
            print("3. Create a Service Account and download JSON key")
            print("4. Save as 'google_credentials.json' in project root")
            print("5. Share your Google Sheet with the service account email")
            return False

        try:
            credentials = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            self.client = gspread.authorize(credentials)
            print("Connected to Google Sheets API")
            return True

        except Exception as e:
            print(f"Error connecting to Google Sheets: {e}")
            return False

    def open_sheet(self, sheet_id: Optional[str] = None, sheet_name: str = "Job Applications") -> bool:
        """Open the Google Sheet"""

        sheet_id = sheet_id or self.sheet_id

        if not sheet_id:
            print("Error: No Google Sheet ID provided")
            print("Add GOOGLE_SHEET_ID to your .env file")
            return False

        if not self.client:
            if not self.connect():
                return False

        try:
            self.spreadsheet = self.client.open_by_key(sheet_id)

            # Try to get existing worksheet or create new one
            try:
                self.worksheet = self.spreadsheet.worksheet(sheet_name)
                print(f"Opened worksheet: {sheet_name}")
            except gspread.WorksheetNotFound:
                self.worksheet = self.spreadsheet.add_worksheet(
                    title=sheet_name,
                    rows=1000,
                    cols=len(self.HEADERS)
                )
                self._setup_headers()
                print(f"Created new worksheet: {sheet_name}")

            return True

        except gspread.SpreadsheetNotFound:
            print(f"Error: Spreadsheet not found with ID: {sheet_id}")
            print("Make sure you've shared the sheet with your service account email")
            return False
        except Exception as e:
            print(f"Error opening sheet: {e}")
            return False

    def _setup_headers(self):
        """Set up header row with formatting"""

        if not self.worksheet:
            return

        # Add headers
        self.worksheet.update('A1:K1', [self.HEADERS])

        # Format header row (bold, white text, dark green background)
        self.worksheet.format('A1:K1', {
            "backgroundColor": {"red": 0.180, "green": 0.369, "blue": 0.243},
            "textFormat": {"bold": True, "foregroundColor": {"red": 1, "green": 1, "blue": 1}},
            "horizontalAlignment": "CENTER"
        })

        # Freeze header row
        self.worksheet.freeze(rows=1)

        # Set column widths
        requests = []
        column_widths = [150, 200, 300, 120, 100, 250, 150, 150, 100, 200, 350]

        for i, width in enumerate(column_widths):
            requests.append({
                "updateDimensionProperties": {
                    "range": {
                        "sheetId": self.worksheet.id,
                        "dimension": "COLUMNS",
                        "startIndex": i,
                        "endIndex": i + 1
                    },
                    "properties": {"pixelSize": width},
                    "fields": "pixelSize"
                }
            })

        if requests:
            self.spreadsheet.batch_update({"requests": requests})

    def sync_jobs(self, tracker_data: Dict) -> Dict:
        """
        Sync jobs from tracker to Google Sheet.
        Returns summary of sync operation.
        """

        if not self.worksheet:
            if not self.open_sheet():
                return {"success": False, "error": "Could not open sheet"}

        # Get existing URLs from sheet to avoid duplicates
        try:
            existing_data = self.worksheet.get_all_values()
            existing_urls = set()

            if len(existing_data) > 1:  # Has data beyond header
                url_col_index = self.HEADERS.index("Link to Job Req")
                for row in existing_data[1:]:  # Skip header
                    if len(row) > url_col_index and row[url_col_index]:
                        existing_urls.add(row[url_col_index])
        except Exception as e:
            print(f"Error reading existing data: {e}")
            existing_urls = set()

        # Prepare new rows
        new_rows = []
        updated_count = 0

        for url, job in tracker_data.items():
            if url not in existing_urls:
                row = self._job_to_row(job, url)
                new_rows.append(row)

        # Batch append new rows
        if new_rows:
            try:
                # Find next empty row
                next_row = len(existing_data) + 1 if existing_data else 2

                # Append all new rows at once
                self.worksheet.update(
                    f'A{next_row}:K{next_row + len(new_rows) - 1}',
                    new_rows
                )

                # Apply alternating row colors and status colors
                self._apply_formatting(next_row, len(new_rows))

                print(f"Added {len(new_rows)} new jobs to Google Sheet")

            except Exception as e:
                print(f"Error appending rows: {e}")
                return {"success": False, "error": str(e)}
        else:
            print("No new jobs to add - sheet is up to date")

        return {
            "success": True,
            "new_jobs": len(new_rows),
            "existing_jobs": len(existing_urls),
            "total_jobs": len(existing_urls) + len(new_rows)
        }

    def _job_to_row(self, job: Dict, url: str) -> List:
        """Convert job dict to spreadsheet row"""

        # Map internal status to display status
        status_map = {
            "new": "Have Not Applied",
            "liked": "Have Not Applied",
            "maybe": "Have Not Applied",
            "disliked": "Have Not Applied",
            "applied": "Submitted - Pending Response",
            "interview": "Interview Scheduled",
            "offer": "Offer Received",
            "rejected": "Rejected"
        }

        status = status_map.get(job.get("status", "new"), "Have Not Applied")

        # Build location string
        city = job.get("city", "")
        country = job.get("location", "UK")
        location = f"{city}, {country}" if city else country

        # Date
        date_submitted = job.get("applied_date") or job.get("date_found", "")

        return [
            job.get("company", "Unknown"),      # A: Company Name
            status,                              # B: Application Status
            job.get("title", ""),               # C: Role
            job.get("salary", ""),              # D: Salary
            date_submitted,                      # E: Date Submitted
            url,                                 # F: Link to Job Req
            "N/A",                              # G: Rejection Reason
            location,                            # H: Location
            job.get("deadline", ""),            # I: Deadline
            job.get("notes", ""),               # J: Notes
            job.get("ai_summary", "")[:500] if job.get("ai_summary") else "",  # K: AI Summary (truncated)
        ]

    def _apply_formatting(self, start_row: int, num_rows: int):
        """Apply formatting to newly added rows"""

        if not self.worksheet or num_rows == 0:
            return

        requests = []

        for i in range(num_rows):
            row_num = start_row + i

            # Alternating row colors (light green / white)
            if row_num % 2 == 0:
                requests.append({
                    "repeatCell": {
                        "range": {
                            "sheetId": self.worksheet.id,
                            "startRowIndex": row_num - 1,
                            "endRowIndex": row_num,
                            "startColumnIndex": 0,
                            "endColumnIndex": len(self.HEADERS)
                        },
                        "cell": {
                            "userEnteredFormat": {
                                "backgroundColor": {"red": 0.910, "green": 0.961, "blue": 0.914}
                            }
                        },
                        "fields": "userEnteredFormat.backgroundColor"
                    }
                })

        # Apply status column dropdown
        requests.append({
            "setDataValidation": {
                "range": {
                    "sheetId": self.worksheet.id,
                    "startRowIndex": start_row - 1,
                    "endRowIndex": start_row + num_rows - 1,
                    "startColumnIndex": 1,  # Column B
                    "endColumnIndex": 2
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [
                            {"userEnteredValue": "Submitted - Pending Response"},
                            {"userEnteredValue": "Have Not Applied"},
                            {"userEnteredValue": "Interview Scheduled"},
                            {"userEnteredValue": "Offer Received"},
                            {"userEnteredValue": "Rejected"},
                            {"userEnteredValue": "N/A"}
                        ]
                    },
                    "showCustomUi": True,
                    "strict": True
                }
            }
        })

        # Apply rejection reason dropdown
        requests.append({
            "setDataValidation": {
                "range": {
                    "sheetId": self.worksheet.id,
                    "startRowIndex": start_row - 1,
                    "endRowIndex": start_row + num_rows - 1,
                    "startColumnIndex": 6,  # Column G
                    "endColumnIndex": 7
                },
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [
                            {"userEnteredValue": "N/A"},
                            {"userEnteredValue": "No Response"},
                            {"userEnteredValue": "Position Filled"},
                            {"userEnteredValue": "Not Qualified"},
                            {"userEnteredValue": "Failed Interview"},
                            {"userEnteredValue": "Salary Mismatch"},
                            {"userEnteredValue": "Location Issue"},
                            {"userEnteredValue": "Other"}
                        ]
                    },
                    "showCustomUi": True,
                    "strict": False
                }
            }
        })

        if requests:
            try:
                self.spreadsheet.batch_update({"requests": requests})
            except Exception as e:
                print(f"Warning: Could not apply formatting: {e}")

    def add_conditional_formatting(self):
        """Add conditional formatting rules for status colors"""

        if not self.worksheet:
            return

        requests = []

        # Add conditional formatting for each status
        for status, color in self.STATUS_COLORS.items():
            requests.append({
                "addConditionalFormatRule": {
                    "rule": {
                        "ranges": [{
                            "sheetId": self.worksheet.id,
                            "startRowIndex": 1,
                            "startColumnIndex": 1,  # Column B
                            "endColumnIndex": 2
                        }],
                        "booleanRule": {
                            "condition": {
                                "type": "TEXT_EQ",
                                "values": [{"userEnteredValue": status}]
                            },
                            "format": {
                                "backgroundColor": color,
                                "textFormat": {
                                    "foregroundColor": {"red": 1, "green": 1, "blue": 1},
                                    "bold": True
                                }
                            }
                        }
                    },
                    "index": 0
                }
            })

        if requests:
            try:
                self.spreadsheet.batch_update({"requests": requests})
                print("Applied conditional formatting for status colors")
            except Exception as e:
                print(f"Warning: Could not apply conditional formatting: {e}")

    def get_sheet_url(self) -> Optional[str]:
        """Get the URL to the Google Sheet"""

        if self.spreadsheet:
            return self.spreadsheet.url
        elif self.sheet_id:
            return f"https://docs.google.com/spreadsheets/d/{self.sheet_id}/edit"
        return None


def sync_to_google_sheets(tracker_data: Dict = None, sheet_id: str = None) -> Dict:
    """
    Convenience function to sync tracker data to Google Sheets.

    Args:
        tracker_data: Job data dict (loads from file if not provided)
        sheet_id: Google Sheet ID (uses env var if not provided)

    Returns:
        Dict with sync results
    """

    if not GSPREAD_AVAILABLE:
        return {
            "success": False,
            "error": "gspread not installed. Run: pip install gspread google-auth"
        }

    # Load tracker data if not provided
    if tracker_data is None:
        try:
            with open("job_tracker.json", "r") as f:
                tracker_data = json.load(f)
        except FileNotFoundError:
            return {"success": False, "error": "job_tracker.json not found"}

    # Create sync instance
    sync = GoogleSheetsSync()

    if sheet_id:
        sync.sheet_id = sheet_id

    # Connect and sync
    if sync.open_sheet():
        result = sync.sync_jobs(tracker_data)

        # Add conditional formatting on first sync
        if result.get("success") and result.get("new_jobs", 0) > 0:
            sync.add_conditional_formatting()

        result["sheet_url"] = sync.get_sheet_url()
        return result

    return {"success": False, "error": "Could not connect to Google Sheet"}


# CLI Interface
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        print("\n" + "=" * 60)
        print("GOOGLE SHEETS SETUP GUIDE")
        print("=" * 60)
        print("""
1. Go to https://console.cloud.google.com/

2. Create a new project (or select existing)
   - Click "Select Project" dropdown
   - Click "New Project"
   - Name it "Job Tracker" or similar

3. Enable the Google Sheets API
   - Go to "APIs & Services" > "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

4. Create Service Account credentials
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "Service Account"
   - Name it "job-tracker-service"
   - Click "Done"
   - Click on the service account you created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Select JSON and click "Create"
   - Save the downloaded file as 'google_credentials.json' in your project folder

5. Share your Google Sheet with the service account
   - Open the JSON file you downloaded
   - Copy the "client_email" value
   - Open your Google Sheet in browser
   - Click "Share"
   - Paste the service account email
   - Give it "Editor" access
   - Click "Done"

6. Add your Sheet ID to .env
   - Open your Google Sheet in browser
   - Copy the ID from the URL:
     https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   - Add to .env file:
     GOOGLE_SHEET_ID=YOUR_SHEET_ID_HERE

7. Install required packages
   pip install gspread google-auth

8. Run sync
   python google_sheets.py sync
""")
        print("=" * 60)

    elif len(sys.argv) > 1 and sys.argv[1] == "sync":
        print("\nSyncing jobs to Google Sheets...")
        result = sync_to_google_sheets()

        if result.get("success"):
            print(f"\nSync completed successfully!")
            print(f"  New jobs added: {result.get('new_jobs', 0)}")
            print(f"  Total jobs in sheet: {result.get('total_jobs', 0)}")
            if result.get("sheet_url"):
                print(f"\nView your sheet: {result['sheet_url']}")
        else:
            print(f"\nSync failed: {result.get('error')}")
            print("\nRun 'python google_sheets.py setup' for setup instructions")

    else:
        print("\nGoogle Sheets Sync for Job Tracker")
        print("-" * 40)
        print("Usage:")
        print("  python google_sheets.py setup  - Show setup instructions")
        print("  python google_sheets.py sync   - Sync jobs to Google Sheet")
        print()
