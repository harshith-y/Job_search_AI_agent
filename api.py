"""
FastAPI Remote Access API
Allows triggering searches, viewing stats, and checking results remotely
Perfect for cloud deployment or remote triggering
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import subprocess
from datetime import datetime
from typing import Optional

from tracker import JobTracker
from memory import load_memory

app = FastAPI(
    title="Job Search Agent API",
    description="Remote access to your job search automation",
    version="1.0.0"
)

# CORS for remote access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track running searches
search_status = {
    "running": False,
    "last_run": None,
    "last_result": None
}


# ============================================================================
# MODELS
# ============================================================================

class SearchRequest(BaseModel):
    """Request to trigger a search"""
    search_type: str = "both"  # both, industry, phd


class SearchResult(BaseModel):
    """Result of a search"""
    status: str
    jobs_found: int
    relevant_jobs: int
    search_type: str
    timestamp: str


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Landing page with links to all endpoints"""
    
    tracker = JobTracker()
    stats = {
        "total": len(tracker.jobs),
        "liked": len(tracker.get_jobs_by_status("liked")),
        "maybe": len(tracker.get_jobs_by_status("maybe")),
        "applied": len(tracker.get_jobs_by_status("applied")),
    }
    
    # Get pending review count
    from pending_review import get_pending_count
    pending_count = get_pending_count()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Job Search Agent</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }}
            .card {{
                background: white;
                color: #333;
                padding: 30px;
                border-radius: 20px;
                margin: 20px 0;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            }}
            h1 {{
                margin: 0 0 10px 0;
                font-size: 36px;
            }}
            .subtitle {{
                color: #666;
                margin: 0 0 30px 0;
            }}
            .pending-banner {{
                background: #fef5e7;
                border: 2px solid #f39c12;
                color: #f39c12;
                padding: 20px;
                border-radius: 12px;
                margin: 20px 0;
                text-align: center;
                font-weight: 600;
                font-size: 18px;
            }}
            .stats {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 15px;
                margin: 20px 0;
            }}
            .stat {{
                text-align: center;
                padding: 15px;
                background: #f7fafc;
                border-radius: 12px;
            }}
            .stat-number {{
                font-size: 32px;
                font-weight: bold;
                color: #667eea;
            }}
            .stat-label {{
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }}
            .btn {{
                display: inline-block;
                padding: 15px 30px;
                margin: 10px 10px 10px 0;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 12px;
                font-weight: 600;
                transition: all 0.2s;
                border: none;
                cursor: pointer;
            }}
            .btn:hover {{
                background: #5568d3;
                transform: translateY(-2px);
            }}
            .btn-primary {{
                background: #48bb78;
                font-size: 18px;
            }}
            .btn-primary:hover {{
                background: #38a169;
            }}
            .endpoint {{
                background: #f7fafc;
                padding: 15px;
                border-radius: 8px;
                margin: 10px 0;
                font-family: monospace;
            }}
            .status {{
                display: inline-block;
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
            }}
            .status-running {{
                background: #fef5e7;
                color: #f39c12;
            }}
            .status-idle {{
                background: #e8f5e9;
                color: #4caf50;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🎯 Job Search Agent</h1>
            <p class="subtitle">Remote access to your automated job search</p>
            
            {f'<div class="pending-banner">🎨 {pending_count} jobs waiting for review! Open on your computer to use the GUI.</div>' if pending_count > 0 else ''}
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{stats['total']}</div>
                    <div class="stat-label">Total Jobs</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{stats['liked']}</div>
                    <div class="stat-label">👍 Liked</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{stats['maybe']}</div>
                    <div class="stat-label">🤔 Maybe</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{stats['applied']}</div>
                    <div class="stat-label">📤 Applied</div>
                </div>
            </div>
            
            <p><span class="status {'status-running' if search_status['running'] else 'status-idle'}">
                {'🔄 Search Running...' if search_status['running'] else '✅ Ready'}
            </span></p>
            
            <div style="margin-top: 30px;">
                <a href="/search/trigger" class="btn btn-primary">🚀 Run Search Now</a>
                {f'<a href="/review" class="btn btn-primary">🎨 Review {pending_count} Jobs (GUI)</a>' if pending_count > 0 else ''}
                <a href="/stats" class="btn">📊 View Stats</a>
                <a href="/liked" class="btn">👍 Liked Jobs</a>
                <a href="/docs" class="btn">📚 API Docs</a>
            </div>
            
            <div style="margin-top: 30px;">
                <h3>Instructions</h3>
                <p>💡 <strong>From Phone:</strong> Trigger searches remotely</p>
                <p>💻 <strong>On Computer:</strong> Run <code>python review_pending.py</code> to review with GUI</p>
                <p>📧 You'll get Discord notifications when searches complete</p>
            </div>
            
            {f'<p style="color: #666; margin-top: 20px;">Last search: {search_status["last_run"]}</p>' if search_status["last_run"] else ''}
        </div>
    </body>
    </html>
    """
    return html


@app.get("/stats")
async def get_stats():
    """Get job tracker statistics"""
    
    tracker = JobTracker()
    
    return {
        "total_jobs": len(tracker.jobs),
        "by_status": {
            "new": len(tracker.get_jobs_by_status("new")),
            "liked": len(tracker.get_jobs_by_status("liked")),
            "maybe": len(tracker.get_jobs_by_status("maybe")),
            "disliked": len(tracker.get_jobs_by_status("disliked")),
            "applied": len(tracker.get_jobs_by_status("applied")),
            "interview": len(tracker.get_jobs_by_status("interview")),
            "offer": len(tracker.get_jobs_by_status("offer")),
            "rejected": len(tracker.get_jobs_by_status("rejected")),
        },
        "by_type": {
            "industry": len([j for j in tracker.jobs.values() if j.get("type") == "Industry"]),
            "phd": len([j for j in tracker.jobs.values() if j.get("type") == "PhD"]),
        },
        "last_search": search_status.get("last_run"),
        "search_running": search_status["running"]
    }


@app.get("/liked")
async def get_liked_jobs():
    """Get all liked jobs"""
    
    tracker = JobTracker()
    liked = tracker.get_jobs_by_status("liked")
    
    return {
        "count": len(liked),
        "jobs": [
            {
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "type": job["type"],
                "url": job["url"],
                "date_found": job["date_found"],
                "notes": job.get("notes", "")
            }
            for job in liked
        ]
    }


@app.get("/recent")
async def get_recent_jobs(limit: int = 10):
    """Get most recently found jobs"""
    
    tracker = JobTracker()
    
    # Sort by date
    all_jobs = sorted(
        tracker.jobs.values(),
        key=lambda x: x["date_found"],
        reverse=True
    )
    
    recent = all_jobs[:limit]
    
    return {
        "count": len(recent),
        "jobs": [
            {
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "type": job["type"],
                "status": job["status"],
                "url": job["url"],
                "date_found": job["date_found"]
            }
            for job in recent
        ]
    }


@app.get("/search/status")
async def search_status_endpoint():
    """Check if search is currently running"""
    
    return {
        "running": search_status["running"],
        "last_run": search_status["last_run"],
        "last_result": search_status["last_result"]
    }


@app.get("/search/trigger")
async def trigger_search_simple(background_tasks: BackgroundTasks):
    """Simple endpoint to trigger search (GET for easy browser access)"""
    
    if search_status["running"]:
        return HTMLResponse("""
            <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>⏳ Search Already Running</h1>
                <p>Please wait for the current search to complete.</p>
                <p><a href="/">← Back to Dashboard</a></p>
            </body></html>
        """)
    
    # Trigger search in background
    background_tasks.add_task(run_search_background, "both")
    
    return HTMLResponse("""
        <html><body style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1>🚀 Search Started!</h1>
            <p>The job search is running in the background.</p>
            <p>You'll get a Discord notification when it's done.</p>
            <p><a href="/">← Back to Dashboard</a></p>
        </body></html>
    """)


@app.post("/search")
async def trigger_search(
    request: SearchRequest,
    background_tasks: BackgroundTasks
):
    """Trigger a job search (POST endpoint for programmatic access)"""
    
    if search_status["running"]:
        raise HTTPException(status_code=409, detail="Search already running")
    
    # Validate search type
    if request.search_type not in ["both", "industry", "phd"]:
        raise HTTPException(status_code=400, detail="Invalid search_type")
    
    # Run search in background
    background_tasks.add_task(run_search_background, request.search_type)
    
    return {
        "status": "started",
        "search_type": request.search_type,
        "message": "Search running in background. Check /search/status for updates."
    }


async def run_search_background(search_type: str):
    """Run search in background and save results for GUI review"""
    
    global search_status
    search_status["running"] = True
    search_status["last_run"] = datetime.now().isoformat()
    
    try:
        # Import here to avoid circular imports
        from scrapers import find_all_industry_jobs, find_all_phd_positions
        from agent_claude import filter_industry_job, filter_phd_position
        from memory import is_new_job
        from pending_review import save_for_review
        
        all_relevant = []
        
        # Search based on type
        if search_type in ["both", "industry"]:
            industry_jobs = find_all_industry_jobs()
            for job in industry_jobs:
                if is_new_job(job['url']):
                    is_relevant, info = filter_industry_job(job)
                    if is_relevant:
                        job["ai_summary"] = info["summary"]
                        job["job_type"] = "Industry"
                        all_relevant.append(job)
        
        if search_type in ["both", "phd"]:
            phd_positions = find_all_phd_positions()
            for phd in phd_positions:
                if is_new_job(phd['url']):
                    is_relevant, info = filter_phd_position(phd)
                    if is_relevant:
                        phd["ai_info"] = info
                        phd["ai_summary"] = info.get("summary", "")
                        phd["job_type"] = "PhD"
                        all_relevant.append(phd)
        
        # Save for GUI review
        if all_relevant:
            count = save_for_review(all_relevant)
            
            # Send Discord notification
            try:
                from notifier import send_discord_notification
                send_discord_notification(all_relevant)
            except:
                pass
        
        search_status["last_result"] = {
            "status": "completed",
            "jobs_found": len(all_relevant),
            "saved_for_review": len(all_relevant),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        search_status["last_result"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    
    finally:
        search_status["running"] = False


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "search_running": search_status["running"]
    }


# ============================================================================
# RUN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    
    print(f"\n🌐 Job Search API Starting...")
    print(f"   Local: http://localhost:{port}")
    print(f"   Docs:  http://localhost:{port}/docs")
    print(f"\n📱 Access from phone (same network):")
    print(f"   http://YOUR_COMPUTER_IP:{port}\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)