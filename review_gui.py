"""
Enhanced Review GUI
Shows detailed job information to make informed decisions:
- Job requirements
- Role expectations
- City location
- Salary
- Post date
- Application deadline
- CV/Cover letter requirements
"""

from flask import Flask, render_template_string, request, redirect
import webbrowser
import threading
from tracker import EnhancedJobTracker

app = Flask(__name__)

# Store jobs globally
current_jobs = []
current_index = [0]  # Use list to allow modification in nested function
tracker = EnhancedJobTracker()


ENHANCED_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Review - Enhanced</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 42px;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 18px;
            opacity: 0.9;
        }
        
        .progress {
            text-align: center;
            color: white;
            font-size: 24px;
            margin: 20px 0;
            font-weight: 600;
        }
        
        .job-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            margin: 20px 0;
        }
        
        .job-type {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 15px;
        }
        
        .type-industry {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .type-phd {
            background: #f3e5f5;
            color: #7b1fa2;
        }
        
        .job-title {
            font-size: 32px;
            font-weight: 700;
            color: #1a202c;
            margin: 15px 0;
            line-height: 1.3;
        }
        
        .job-company {
            font-size: 22px;
            color: #4a5568;
            margin-bottom: 10px;
        }
        
        .job-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
            padding: 20px;
            background: #f7fafc;
            border-radius: 12px;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .meta-icon {
            font-size: 20px;
        }
        
        .meta-text {
            font-size: 14px;
        }
        
        .meta-label {
            font-weight: 600;
            color: #2d3748;
        }
        
        .meta-value {
            color: #4a5568;
        }
        
        .section {
            margin: 25px 0;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .section-content {
            font-size: 15px;
            line-height: 1.6;
            color: #4a5568;
            background: #f7fafc;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .requirements-list, .expectations-list {
            list-style: none;
            padding: 0;
        }
        
        .requirements-list li, .expectations-list li {
            padding: 8px 0;
            border-bottom: 1px solid #e2e8f0;
        }
        
        .requirements-list li:last-child, .expectations-list li:last-child {
            border-bottom: none;
        }
        
        .requirements-list li:before {
            content: "✓ ";
            color: #48bb78;
            font-weight: bold;
            margin-right: 8px;
        }
        
        .expectations-list li:before {
            content: "▸ ";
            color: #667eea;
            font-weight: bold;
            margin-right: 8px;
        }
        
        .job-link {
            display: inline-block;
            margin: 20px 0;
            padding: 12px 24px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .job-link:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }
        
        .button-group {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-top: 30px;
        }
        
        .btn {
            padding: 20px;
            font-size: 20px;
            font-weight: 700;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.2s;
            text-align: center;
            text-decoration: none;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
        }
        
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }
        
        .btn-like {
            background: #48bb78;
            color: white;
        }
        
        .btn-maybe {
            background: #ed8936;
            color: white;
        }
        
        .btn-pass {
            background: #f56565;
            color: white;
        }
        
        .btn-icon {
            font-size: 32px;
        }
        
        .completion-screen {
            text-align: center;
            color: white;
            padding: 60px 20px;
        }
        
        .completion-screen h2 {
            font-size: 48px;
            margin-bottom: 30px;
        }
        
        .stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin: 40px 0;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 64px;
            font-weight: 700;
            margin-bottom: 10px;
        }
        
        .stat-label {
            font-size: 20px;
            opacity: 0.9;
        }
        
        @media (max-width: 768px) {
            .job-title {
                font-size: 24px;
            }
            
            .button-group {
                grid-template-columns: 1fr;
            }
            
            .job-meta {
                grid-template-columns: 1fr;
            }
            
            .stats {
                flex-direction: column;
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Job Review</h1>
            <p>Review your opportunities with detailed information</p>
        </div>
        
        {% if complete %}
            <div class="completion-screen">
                <h2>🎉 Review Complete!</h2>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">{{ liked_count }}</div>
                        <div class="stat-label">👍 Liked</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{{ maybe_count }}</div>
                        <div class="stat-label">🤔 Maybe</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">{{ passed_count }}</div>
                        <div class="stat-label">👎 Passed</div>
                    </div>
                </div>
                <p style="font-size: 18px; margin: 30px 0;">
                    Your decisions have been saved to the spreadsheet!
                </p>
            </div>
        {% else %}
            <div class="progress">
                Job {{ current + 1 }} of {{ total }}
            </div>
            
            <div class="job-card">
                <span class="job-type {{ 'type-industry' if job.type == 'Industry' else 'type-phd' }}">
                    {{ '💼 Industry Job' if job.type == 'Industry' else '🎓 PhD Position' }}
                </span>
                
                <h2 class="job-title">{{ job.title }}</h2>
                <div class="job-company">🏢 {{ job.company }}</div>
                
                <div class="job-meta">
                    <div class="meta-item">
                        <span class="meta-icon">📍</span>
                        <div class="meta-text">
                            <div class="meta-label">Location</div>
                            <div class="meta-value">{{ job.city }}</div>
                        </div>
                    </div>
                    
                    <div class="meta-item">
                        <span class="meta-icon">💰</span>
                        <div class="meta-text">
                            <div class="meta-label">Salary</div>
                            <div class="meta-value">{{ job.salary }}</div>
                        </div>
                    </div>
                    
                    <div class="meta-item">
                        <span class="meta-icon">📅</span>
                        <div class="meta-text">
                            <div class="meta-label">Posted</div>
                            <div class="meta-value">{{ job.post_date }}</div>
                        </div>
                    </div>
                    
                    <div class="meta-item">
                        <span class="meta-icon">⏰</span>
                        <div class="meta-text">
                            <div class="meta-label">Deadline</div>
                            <div class="meta-value">{{ job.deadline }}</div>
                        </div>
                    </div>
                    
                    <div class="meta-item">
                        <span class="meta-icon">📄</span>
                        <div class="meta-text">
                            <div class="meta-label">CV Required</div>
                            <div class="meta-value">{{ job.cv_required }}</div>
                        </div>
                    </div>
                    
                    <div class="meta-item">
                        <span class="meta-icon">✉️</span>
                        <div class="meta-text">
                            <div class="meta-label">Cover Letter</div>
                            <div class="meta-value">{{ job.cover_letter_required }}</div>
                        </div>
                    </div>
                </div>
                
                {% if job.requirements and job.requirements|length > 0 %}
                <div class="section">
                    <div class="section-title">
                        <span>🎯</span>
                        <span>Key Requirements</span>
                    </div>
                    <div class="section-content">
                        <ul class="requirements-list">
                            {% for req in job.requirements[:8] %}
                            <li>{{ req }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endif %}
                
                {% if job.expectations and job.expectations|length > 0 %}
                <div class="section">
                    <div class="section-title">
                        <span>💡</span>
                        <span>Role Expectations</span>
                    </div>
                    <div class="section-content">
                        <ul class="expectations-list">
                            {% for exp in job.expectations[:5] %}
                            <li>{{ exp }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
                {% endif %}
                
                {% if job.ai_summary %}
                <div class="section">
                    <div class="section-title">
                        <span>🤖</span>
                        <span>AI Analysis</span>
                    </div>
                    <div class="section-content">
                        {{ job.ai_summary }}
                    </div>
                </div>
                {% endif %}
                
                <a href="{{ job.url }}" target="_blank" class="job-link">
                    🔗 View Full Job Posting
                </a>
                
                <div class="button-group">
                    <a href="/review/like" class="btn btn-like">
                        <span class="btn-icon">👍</span>
                        <span>Like</span>
                    </a>
                    <a href="/review/maybe" class="btn btn-maybe">
                        <span class="btn-icon">🤔</span>
                        <span>Maybe</span>
                    </a>
                    <a href="/review/pass" class="btn btn-pass">
                        <span class="btn-icon">👎</span>
                        <span>Pass</span>
                    </a>
                </div>
            </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route('/')
def index():
    """Show current job for review"""
    
    if current_index[0] >= len(current_jobs):
        # Review complete
        liked = len([j for j in current_jobs if tracker.jobs.get(j['url'], {}).get('status') == 'liked'])
        maybe = len([j for j in current_jobs if tracker.jobs.get(j['url'], {}).get('status') == 'maybe'])
        passed = len([j for j in current_jobs if tracker.jobs.get(j['url'], {}).get('status') == 'disliked'])
        
        # Export to spreadsheet
        tracker.export_to_excel_fancy()
        
        return render_template_string(
            ENHANCED_TEMPLATE,
            complete=True,
            liked_count=liked,
            maybe_count=maybe,
            passed_count=passed
        )
    
    job = current_jobs[current_index[0]]
    
    return render_template_string(
        ENHANCED_TEMPLATE,
        job=job,
        current=current_index[0],
        total=len(current_jobs),
        complete=False
    )


@app.route('/review/<action>')
def review_action(action):
    """Handle Like/Maybe/Pass action"""
    
    if current_index[0] < len(current_jobs):
        job = current_jobs[current_index[0]]
        
        # Map action to status
        status_map = {
            'like': 'liked',
            'maybe': 'maybe',
            'pass': 'disliked'
        }
        
        status = status_map.get(action, 'new')
        
        # Save to tracker
        tracker.add_job(job, status=status)
        
        # Move to next
        current_index[0] += 1
    
    return redirect('/')


def start_review_server(jobs, port=5000):
    """Start the review server"""
    
    global current_jobs, current_index, tracker
    current_jobs = jobs
    current_index[0] = 0
    tracker = EnhancedJobTracker()
    
    # Open browser
    threading.Timer(1.5, lambda: webbrowser.open(f'http://localhost:{port}')).start()
    
    print(f"\n{'='*60}")
    print(f"🌐 Review GUI Started")
    print(f"{'='*60}")
    print(f"\n   Opening browser at: http://localhost:{port}")
    print(f"   Jobs to review: {len(jobs)}")
    print(f"\n   Press Ctrl+C to stop\n")
    
    app.run(port=port, debug=False)


if __name__ == "__main__":
    # Test with sample data
    sample_jobs = [
        {
            "title": "Machine Learning Engineer",
            "company": "Google DeepMind",
            "city": "London",
            "location": "UK",
            "type": "Industry",
            "url": "https://deepmind.com/job/123",
            "salary": "£60k-80k",
            "post_date": "2024-12-01",
            "deadline": "2024-12-31",
            "cv_required": "Yes",
            "cover_letter_required": "Optional",
            "requirements": ["PhD or Masters in ML", "PyTorch experience", "3+ publications"],
            "expectations": ["Build state-of-the-art models", "Collaborate with researchers"],
            "ai_summary": "Strong ML role at leading AI research lab...",
        }
    ]
    
    start_review_server(sample_jobs)