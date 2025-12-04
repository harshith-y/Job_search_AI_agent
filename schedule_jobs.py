"""
Scheduled Job Runner
Runs job searches automatically at specified times
Perfect for cloud deployment
"""

import schedule
import time
import subprocess
from datetime import datetime

def run_daily_search():
    """Run the daily job search"""
    
    print(f"\n{'='*60}")
    print(f"🕐 Scheduled Search Starting - {datetime.now()}")
    print(f"{'='*60}\n")
    
    try:
        # Run main.py
        result = subprocess.run(
            ["python", "main.py"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )
        
        if result.returncode == 0:
            print("✅ Search completed successfully")
            print(result.stdout[-500:])  # Last 500 chars
        else:
            print("❌ Search failed")
            print(result.stderr)
    
    except Exception as e:
        print(f"❌ Error running search: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ Scheduled Search Complete - {datetime.now()}")
    print(f"{'='*60}\n")


def main():
    """Set up and run scheduler"""
    
    print("\n🕐 Job Search Scheduler Starting...\n")
    
    # Schedule searches at 9:00 AM and 4:00 PM GMT
    schedule.every().day.at("09:00").do(run_daily_search)
    schedule.every().day.at("16:00").do(run_daily_search)  # 4 PM
    
    print("📅 Schedule configured:")
    print("   • Daily search at 9:00 AM GMT")
    print("   • Daily search at 4:00 PM GMT")
    print("\n⏳ Waiting for scheduled time...\n")
    
    # Run forever
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Scheduler stopped")