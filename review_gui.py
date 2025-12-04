"""
Job Review Web Interface
Simple web GUI for reviewing jobs with Like/Maybe/Pass buttons
"""

from flask import Flask, render_template_string, request, jsonify, redirect
import webbrowser
import threading
from tracker import JobTracker
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Global storage for jobs to review
jobs_to_review = []
tracker = JobTracker()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Job Review</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
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
            max-width: 800px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 32px;
        }
        
        .header p {
            color: #666;
            font-size: 16px;
        }
        
        .progress {
            background: white;
            padding: 15px 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
            font-size: 18px;
            color: #667eea;
            font-weight: 600;
        }
        
        .job-card {
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
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
            font-size: 28px;
            font-weight: 700;
            color: #2d3748;
            margin-bottom: 15px;
            line-height: 1.3;
        }
        
        .job-meta {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
            color: #666;
            font-size: 16px;
        }
        
        .meta-item svg {
            width: 20px;
            height: 20px;
        }
        
        .job-summary {
            background: #f7fafc;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            line-height: 1.6;
            color: #4a5568;
        }
        
        .job-link {
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .job-link:hover {
            text-decoration: underline;
        }
        
        .button-group {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        
        .btn {
            flex: 1;
            padding: 18px 30px;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        
        .btn-like {
            background: #48bb78;
            color: white;
        }
        
        .btn-like:hover {
            background: #38a169;
        }
        
        .btn-maybe {
            background: #ed8936;
            color: white;
        }
        
        .btn-maybe:hover {
            background: #dd6b20;
        }
        
        .btn-pass {
            background: #e53e3e;
            color: white;
        }
        
        .btn-pass:hover {
            background: #c53030;
        }
        
        .complete-screen {
            background: white;
            border-radius: 20px;
            padding: 60px 40px;
            text-align: center;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        
        .complete-screen h2 {
            font-size: 48px;
            margin-bottom: 20px;
        }
        
        .complete-screen p {
            font-size: 20px;
            color: #666;
            margin-bottom: 30px;
        }
        
        .stats {
            display: flex;
            gap: 30px;
            justify-content: center;
            margin: 40px 0;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-number {
            font-size: 48px;
            font-weight: 700;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 16px;
            color: #666;
            margin-top: 5px;
        }
        
        .btn-secondary {
            background: #667eea;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 12px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px;
        }
        
        .btn-secondary:hover {
            background: #5568d3;
        }
        
        @media (max-width: 768px) {
            .job-card {
                padding: 25px;
            }
            
            .job-title {
                font-size: 22px;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            .btn {
                padding: 15px 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Job Review</h1>
            <p>Review your new opportunities and track what interests you</p>
        </div>
        
        {% if current_job %}
        <div class="progress">
            Job {{ current_index + 1 }} of {{ total_jobs }}
        </div>
        
        <div class="job-card">
            <span class="job-type type-{{ current_job.job_type.lower() }}">
                {% if current_job.job_type == 'PhD' %}🎓 PhD Position{% else %}💼 Industry Job{% endif %}
            </span>
            
            <h2 class="job-title">{{ current_job.title }}</h2>
            
            <div class="job-meta">
                <div class="meta-item">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path></svg>
                    {{ current_job.company }}
                </div>
                <div class="meta-item">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    {{ current_job.location }}
                </div>
            </div>
            
            {% if current_job.ai_summary %}
            <div class="job-summary">
                💡 {{ current_job.ai_summary }}
            </div>
            {% endif %}
            
            {% if current_job.get('ai_info') and current_job.ai_info.get('funding_status') %}
            <div class="job-summary">
                💰 Funding: {{ current_job.ai_info.funding_status }}
                {% if current_job.ai_info.get('research_match') %}
                <br>📊 Research Match: {{ current_job.ai_info.research_match }}
                {% endif %}
            </div>
            {% endif %}
            
            <a href="{{ current_job.url }}" target="_blank" class="job-link">🔗 View Full Posting →</a>
            
            <div class="button-group">
                <button class="btn btn-like" onclick="reviewJob('liked')">
                    👍 Like
                </button>
                <button class="btn btn-maybe" onclick="reviewJob('maybe')">
                    🤔 Maybe
                </button>
                <button class="btn btn-pass" onclick="reviewJob('disliked')">
                    👎 Pass
                </button>
            </div>
        </div>
        {% else %}
        <div class="complete-screen">
            <h2>🎉</h2>
            <p style="font-size: 32px; font-weight: 700; color: #2d3748;">Review Complete!</p>
            <p>You've reviewed all {{ total_jobs }} jobs</p>
            
            <div class="stats">
                <div class="stat">
                    <div class="stat-number">{{ stats.liked }}</div>
                    <div class="stat-label">👍 Liked</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ stats.maybe }}</div>
                    <div class="stat-label">🤔 Maybe</div>
                </div>
                <div class="stat">
                    <div class="stat-number">{{ stats.passed }}</div>
                    <div class="stat-label">👎 Passed</div>
                </div>
            </div>
            
            <p style="margin-top: 30px;">Your spreadsheet has been updated!</p>
            <a href="/export" class="btn-secondary">📊 Open Spreadsheet</a>
            <a href="/close" class="btn-secondary">✅ Done</a>
        </div>
        {% endif %}
    </div>
    
    <script>
        function reviewJob(status) {
            fetch('/review', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ status: status })
            })
            .then(response => response.json())
            .then(data => {
                if (data.complete) {
                    window.location.href = '/complete';
                } else {
                    window.location.reload();
                }
            });
        }
    </script>
</body>
</html>
"""


@app.route('/')
def index():
    """Main review page"""
    if not jobs_to_review:
        return render_template_string(HTML_TEMPLATE, 
                                     current_job=None,
                                     total_jobs=0,
                                     stats={'liked': 0, 'maybe': 0, 'passed': 0})
    
    return render_template_string(HTML_TEMPLATE,
                                 current_job=jobs_to_review[0],
                                 current_index=0,
                                 total_jobs=len(jobs_to_review))


@app.route('/review', methods=['POST'])
def review():
    """Handle review action"""
    global jobs_to_review
    
    if not jobs_to_review:
        return jsonify({'complete': True})
    
    status = request.json.get('status')
    current_job = jobs_to_review[0]
    
    # Add to tracker
    tracker.add_job(current_job, status=status)
    
    # Remove from review list
    jobs_to_review.pop(0)
    
    # Check if complete
    if not jobs_to_review:
        # Export to spreadsheet
        tracker.export_to_excel()
        return jsonify({'complete': True})
    
    return jsonify({'complete': False})


@app.route('/complete')
def complete():
    """Completion page"""
    stats = {
        'liked': len(tracker.get_jobs_by_status('liked')),
        'maybe': len(tracker.get_jobs_by_status('maybe')),
        'passed': len(tracker.get_jobs_by_status('disliked'))
    }
    
    return render_template_string(HTML_TEMPLATE,
                                 current_job=None,
                                 total_jobs=len(tracker.jobs),
                                 stats=stats)


@app.route('/export')
def export():
    """Export and open spreadsheet"""
    filepath = tracker.export_to_excel()
    
    # Open spreadsheet
    import platform
    import subprocess
    
    try:
        if platform.system() == 'Darwin':  # macOS
            subprocess.call(['open', filepath])
        elif platform.system() == 'Windows':
            os.startfile(filepath)
        else:  # linux
            subprocess.call(['xdg-open', filepath])
    except:
        pass
    
    return redirect('/close')


@app.route('/close')
def close_server():
    """Close the server"""
    func = request.environ.get('werkzeug.server.shutdown')
    if func:
        func()
    return '<h1>✅ Done! You can close this window.</h1><script>setTimeout(() => window.close(), 2000)</script>'


def start_review_server(jobs, port=5000):
    """Start the review web interface"""
    global jobs_to_review
    jobs_to_review = jobs.copy()
    
    # Open browser automatically
    def open_browser():
        webbrowser.open(f'http://localhost:{port}')
    
    timer = threading.Timer(1.5, open_browser)
    timer.start()
    
    print(f"\n🌐 Opening review interface in your browser...")
    print(f"   URL: http://localhost:{port}")
    print(f"   Press Ctrl+C to stop\n")
    
    app.run(port=port, debug=False)


# Command line usage
if __name__ == "__main__":
    # Test with sample jobs
    sample_jobs = [
        {
            "title": "Machine Learning Engineer",
            "company": "Google DeepMind",
            "location": "London, UK",
            "url": "https://careers.google.com/example",
            "job_type": "Industry",
            "ai_summary": "Exciting ML role focusing on reinforcement learning for robotics applications."
        },
        {
            "title": "PhD in Computer Vision",
            "company": "University of Cambridge",
            "location": "Cambridge, UK",
            "url": "https://cam.ac.uk/example",
            "job_type": "PhD",
            "ai_summary": "Fully funded PhD position researching novel approaches to 3D scene understanding.",
            "ai_info": {
                "funding_status": "FUNDED (EPSRC)",
                "research_match": "90%"
            }
        }
    ]
    
    start_review_server(sample_jobs)