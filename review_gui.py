"""
Job Review GUI - Professional Edition
Clean, modern interface for reviewing job opportunities
Features:
- Keyboard shortcuts (Arrow keys: Left=Pass, Down=Maybe, Right=Like)
- Undo functionality
- Clean information display with proper fallbacks
- Progress bar
- Professional styling
- LEARNING: Triggers preference learning on session completion
"""

from flask import Flask, render_template_string, request, redirect
import webbrowser
import threading
import subprocess
import sys
from tracker import EnhancedJobTracker


def _trigger_learning():
    """
    Trigger preference learning after review session completes.
    This is the key feedback loop that makes the agent learn.
    """
    try:
        from agency.preference_learner import PreferenceLearner
        from agency.accuracy_tracker import AccuracyTracker

        print("\n" + "=" * 50)
        print("LEARNING FROM YOUR FEEDBACK")
        print("=" * 50)

        # Load tracker data
        learner_tracker = EnhancedJobTracker()

        # Run preference learning
        learner = PreferenceLearner()
        result = learner.learn_from_feedback(learner_tracker.jobs)

        print(f"\n  Feedback analyzed:")
        print(f"    - Liked: {result['accuracy'].get('liked', 0)}")
        print(f"    - Disliked: {result['accuracy'].get('disliked', 0)}")
        print(f"    - Maybe: {result['accuracy'].get('maybe', 0)}")

        print(f"\n  Patterns discovered:")
        print(f"    - Positive patterns: {result['patterns_found']}")
        print(f"    - Negative patterns: {result['negative_patterns_found']}")

        print(f"\n  Current precision: {result['accuracy'].get('precision', 0):.0%}")
        print(f"  Strictness recommendation: {result['strictness_recommendation']}")

        # Track accuracy over time
        accuracy_tracker = AccuracyTracker()
        accuracy_tracker.record_session(learner_tracker.jobs)
        trend = accuracy_tracker.get_accuracy_trend()
        print(f"  Accuracy trend: {trend.get('trend', 'establishing')}")

        print("\n  Preferences updated for next search!")
        print("=" * 50 + "\n")

        return result

    except ImportError:
        print("\n  (Note: Agency module not installed - learning disabled)")
        return None
    except Exception as e:
        print(f"\n  (Learning error: {e})")
        return None

app = Flask(__name__)

# Store jobs globally
current_jobs = []
current_index = [0]
review_history = []  # For undo functionality
tracker = EnhancedJobTracker()

# Use port 5050 to avoid conflicts with MLflow (which uses 5000/5001)
DEFAULT_PORT = 5050


def clean_text(text, max_length=200):
    """Clean and truncate text for display"""
    if not text:
        return ""
    # Remove extra whitespace
    text = ' '.join(text.split())
    # Truncate if too long
    if len(text) > max_length:
        return text[:max_length].rsplit(' ', 1)[0] + "..."
    return text


def get_display_value(value, default="Not available"):
    """Get display value with fallback"""
    if not value or value in ['Not specified', 'Not Specified', '', 'N/A', 'None', 'Unknown', 'See listing']:
        return default
    return value


PROFESSIONAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Job Review</title>
    <style>
        /* === MINIMAL PROFESSIONAL THEME === */
        :root {
            --bg-primary: #fafafa;
            --bg-card: #ffffff;
            --text-primary: #1f2937;
            --text-secondary: #6b7280;
            --text-muted: #9ca3af;
            --accent-like: #10b981;
            --accent-pass: #ef4444;
            --accent-maybe: #f59e0b;
            --accent-primary: #3b82f6;
            --border: #e5e7eb;
            --shadow: rgba(0,0,0,0.08);
            --shadow-lg: rgba(0,0,0,0.12);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
            background: var(--bg-primary);
            min-height: 100vh;
            color: var(--text-primary);
            overflow-x: hidden;
        }

        .app-container {
            max-width: 520px;
            margin: 0 auto;
            padding: 24px 16px;
            min-height: 100vh;
        }

        /* === HEADER === */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .header h1 {
            font-size: 20px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .progress-text {
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .progress-bar {
            height: 4px;
            background: var(--border);
            border-radius: 2px;
            overflow: hidden;
            margin-bottom: 20px;
        }

        .progress-fill {
            height: 100%;
            background: var(--accent-primary);
            transition: width 0.3s ease;
        }

        /* === CARD STACK === */
        .card-stack {
            position: relative;
            height: 520px;
            margin-bottom: 24px;
        }

        /* Snap back button */
        .snap-back-btn {
            position: absolute;
            top: -8px;
            right: -8px;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: var(--bg-card);
            border: 1px solid var(--border);
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            color: var(--text-secondary);
            transition: all 0.2s ease;
            z-index: 20;
            box-shadow: 0 2px 8px var(--shadow);
        }

        .snap-back-btn:hover {
            background: var(--bg-primary);
            color: var(--text-primary);
            transform: scale(1.05);
        }

        /* Next card (behind) */
        .next-card {
            position: absolute;
            top: 8px;
            left: 4px;
            right: 4px;
            height: calc(100% - 8px);
            background: var(--bg-card);
            border-radius: 16px;
            box-shadow: 0 2px 12px var(--shadow);
            opacity: 0.4;
            transform: scale(0.96);
            z-index: 1;
        }

        .next-card-content {
            padding: 24px;
            opacity: 0.6;
        }

        .next-card-title {
            font-size: 18px;
            font-weight: 600;
            color: var(--text-secondary);
        }

        .next-card-meta {
            font-size: 14px;
            color: var(--text-muted);
            margin-top: 4px;
        }

        /* Current swipe card */
        .swipe-card {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 100%;
            background: var(--bg-card);
            border-radius: 16px;
            box-shadow: 0 4px 20px var(--shadow-lg);
            cursor: grab;
            z-index: 10;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            overflow: hidden;
            border: 2px solid transparent;
        }

        .swipe-card.dragging {
            cursor: grabbing;
            transition: box-shadow 0.1s ease;
        }

        /* Swipe direction indicators (subtle border glow) */
        .swipe-card.swiping-right {
            border-color: var(--accent-like);
            box-shadow: 0 4px 20px var(--shadow-lg), 0 0 20px rgba(16, 185, 129, 0.15);
        }

        .swipe-card.swiping-left {
            border-color: var(--accent-pass);
            box-shadow: 0 4px 20px var(--shadow-lg), 0 0 20px rgba(239, 68, 68, 0.15);
        }

        .swipe-card.swiping-down {
            border-color: var(--accent-maybe);
            box-shadow: 0 4px 20px var(--shadow-lg), 0 0 20px rgba(245, 158, 11, 0.15);
        }

        /* Card content */
        .card-content {
            height: 100%;
            overflow-y: auto;
            padding: 24px;
        }

        .job-type-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin-bottom: 12px;
        }

        .badge-industry {
            background: #dbeafe;
            color: #1e40af;
        }

        .badge-phd {
            background: #f3e8ff;
            color: #6b21a8;
        }

        .job-title {
            font-size: 22px;
            font-weight: 700;
            color: var(--text-primary);
            line-height: 1.3;
            margin-bottom: 6px;
        }

        .job-meta {
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 4px;
        }

        .job-salary {
            font-size: 15px;
            font-weight: 600;
            color: var(--accent-like);
            margin-bottom: 16px;
        }

        .divider {
            border: none;
            border-top: 1px solid var(--border);
            margin: 16px 0;
        }

        .section {
            margin-bottom: 16px;
        }

        .section-title {
            font-size: 11px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .section-content {
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-secondary);
        }

        .requirements-list {
            list-style: none;
            padding: 0;
        }

        .requirements-list li {
            padding: 6px 0;
            padding-left: 16px;
            position: relative;
            font-size: 14px;
            color: var(--text-secondary);
            line-height: 1.5;
        }

        .requirements-list li::before {
            content: "";
            position: absolute;
            left: 0;
            top: 12px;
            width: 5px;
            height: 5px;
            background: var(--accent-primary);
            border-radius: 50%;
        }

        .ai-summary {
            background: linear-gradient(135deg, #f0f9ff 0%, #faf5ff 100%);
            border-radius: 8px;
            padding: 14px;
            font-size: 14px;
            line-height: 1.6;
            color: var(--text-secondary);
            border-left: 3px solid var(--accent-primary);
        }

        .job-deadline {
            font-size: 13px;
            color: var(--text-muted);
            margin: 16px 0;
        }

        .job-deadline.urgent {
            color: var(--accent-pass);
            font-weight: 500;
        }

        .view-job-btn {
            display: inline-block;
            padding: 10px 20px;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-primary);
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .view-job-btn:hover {
            background: var(--bg-card);
            border-color: var(--accent-primary);
            color: var(--accent-primary);
        }

        /* === ACTION BUTTONS === */
        .swipe-hints {
            text-align: center;
            margin-bottom: 16px;
            font-size: 13px;
            color: var(--text-muted);
        }

        .action-buttons {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 16px;
        }

        .action-btn {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            border: 2px solid var(--border);
            background: var(--bg-card);
            cursor: pointer;
            font-size: 22px;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            text-decoration: none;
            color: var(--text-secondary);
        }

        .action-btn:hover {
            transform: scale(1.1);
        }

        .action-btn.pass:hover {
            border-color: var(--accent-pass);
            color: var(--accent-pass);
            background: #fef2f2;
        }

        .action-btn.maybe:hover {
            border-color: var(--accent-maybe);
            color: var(--accent-maybe);
            background: #fffbeb;
        }

        .action-btn.like:hover {
            border-color: var(--accent-like);
            color: var(--accent-like);
            background: #ecfdf5;
        }

        /* Bottom bar */
        .bottom-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .undo-btn {
            padding: 8px 14px;
            background: transparent;
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 13px;
            color: var(--text-secondary);
            cursor: pointer;
            text-decoration: none;
            transition: all 0.2s ease;
        }

        .undo-btn:hover {
            background: var(--bg-card);
            color: var(--text-primary);
        }

        .keyboard-hint {
            font-size: 11px;
            color: var(--text-muted);
        }

        .keyboard-hint kbd {
            display: inline-block;
            padding: 2px 5px;
            font-size: 10px;
            font-family: monospace;
            background: var(--bg-card);
            border-radius: 3px;
            border: 1px solid var(--border);
            margin: 0 1px;
        }

        .quality-badge {
            font-size: 12px;
            color: var(--text-muted);
        }

        .quality-badge strong {
            color: var(--accent-primary);
        }

        /* === COMPLETION SCREEN === */
        .completion {
            text-align: center;
            padding: 60px 20px;
        }

        .completion h2 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--text-primary);
        }

        .completion-subtitle {
            font-size: 15px;
            color: var(--text-secondary);
            margin-bottom: 32px;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 12px;
            max-width: 320px;
            margin: 0 auto 32px;
        }

        .stat-card {
            background: var(--bg-card);
            padding: 20px 16px;
            border-radius: 12px;
            box-shadow: 0 2px 8px var(--shadow);
        }

        .stat-number {
            font-size: 32px;
            font-weight: 700;
        }

        .stat-number.liked { color: var(--accent-like); }
        .stat-number.maybe { color: var(--accent-maybe); }
        .stat-number.passed { color: var(--accent-pass); }

        .stat-label {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.3px;
        }

        .completion-note {
            font-size: 14px;
            color: var(--text-muted);
        }

        /* === RESPONSIVE === */
        @media (max-width: 480px) {
            .app-container {
                padding: 16px 12px;
            }

            .card-stack {
                height: 480px;
            }

            .job-title {
                font-size: 20px;
            }

            .action-btn {
                width: 52px;
                height: 52px;
                font-size: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="app-container">
        {% if complete %}
        <!-- Completion Screen -->
        <div class="completion">
            <h2>All Done!</h2>
            <p class="completion-subtitle">Reviewed {{ liked_count + maybe_count + passed_count }} jobs</p>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number liked">{{ liked_count }}</div>
                    <div class="stat-label">Liked</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number maybe">{{ maybe_count }}</div>
                    <div class="stat-label">Maybe</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number passed">{{ passed_count }}</div>
                    <div class="stat-label">Passed</div>
                </div>
            </div>
            <p class="completion-note">
                Saved to spreadsheet. Learning from your preferences...
            </p>
        </div>
        {% else %}
        <!-- Header -->
        <div class="header">
            <h1>Job Review</h1>
            <span class="progress-text">{{ current + 1 }} of {{ total }}</span>
        </div>
        <div class="progress-bar">
            <div class="progress-fill" style="width: {{ ((current + 1) / total * 100) if total > 0 else 0 }}%"></div>
        </div>

        <!-- Card Stack -->
        <div class="card-stack">
            <!-- Snap back button -->
            <button class="snap-back-btn" id="snap-back" title="Reset card position">&#8617;</button>

            <!-- Next card preview (behind) -->
            {% if next_job %}
            <div class="next-card">
                <div class="next-card-content">
                    <div class="next-card-title">{{ next_job.title[:40] }}{% if next_job.title|length > 40 %}...{% endif %}</div>
                    <div class="next-card-meta">{{ next_job.company or 'Company' }}</div>
                </div>
            </div>
            {% endif %}

            <!-- Current swipe card -->
            <div class="swipe-card" id="swipe-card">
                <div class="card-content">
                    <span class="job-type-badge {{ 'badge-industry' if job.type == 'Industry' else 'badge-phd' }}">
                        {{ 'Industry' if job.type == 'Industry' else 'PhD' }}
                    </span>

                    <h2 class="job-title">{{ title_display }}</h2>
                    <p class="job-meta">{{ company_display }} &bull; {{ location_display }}</p>
                    {% if salary_display != 'Not listed' %}
                    <p class="job-salary">{{ salary_display }}</p>
                    {% endif %}

                    <hr class="divider">

                    {% if requirements_display and requirements_display|length > 0 %}
                    <div class="section">
                        <div class="section-title">Key Requirements</div>
                        <ul class="requirements-list">
                            {% for req in requirements_display %}
                            <li>{{ req }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                    {% endif %}

                    {% if ai_summary_display %}
                    <div class="section">
                        <div class="section-title">AI Summary</div>
                        <div class="ai-summary">{{ ai_summary_display }}</div>
                    </div>
                    {% endif %}

                    {% if deadline_display != 'Not specified' %}
                    <p class="job-deadline {{ 'urgent' if 'soon' in deadline_display.lower() or 'day' in deadline_display.lower() else '' }}">
                        Deadline: {{ deadline_display }}
                    </p>
                    {% endif %}

                    <a href="{{ job.url }}" target="_blank" class="view-job-btn">
                        View Job Posting &rarr;
                    </a>
                </div>
            </div>
        </div>

        <!-- Swipe hints -->
        <div class="swipe-hints">
            &larr; Pass &nbsp;&nbsp; &darr; Maybe &nbsp;&nbsp; Like &rarr;
        </div>

        <!-- Action buttons -->
        <div class="action-buttons">
            <a href="/review/pass" class="action-btn pass" id="btn-pass">&times;</a>
            <a href="/review/maybe" class="action-btn maybe" id="btn-maybe">?</a>
            <a href="/review/like" class="action-btn like" id="btn-like">&hearts;</a>
        </div>

        <!-- Bottom bar -->
        <div class="bottom-bar">
            {% if can_undo %}
            <a href="/undo" class="undo-btn" id="btn-undo">Undo</a>
            {% else %}
            <span></span>
            {% endif %}

            <span class="keyboard-hint">
                <kbd>&larr;</kbd><kbd>&darr;</kbd><kbd>&rarr;</kbd><kbd>Z</kbd>
            </span>

            {% if job.quality_score %}
            <span class="quality-badge">Match: <strong>{{ job.quality_score }}%</strong></span>
            {% else %}
            <span></span>
            {% endif %}
        </div>
        {% endif %}
    </div>

    <script>
        (function() {
            const card = document.getElementById('swipe-card');
            const snapBackBtn = document.getElementById('snap-back');
            if (!card) return;

            let startX = 0, startY = 0;
            let currentX = 0, currentY = 0;
            let isDragging = false;

            // Thresholds
            const SWIPE_THRESHOLD = 100;
            const INDICATOR_THRESHOLD = 30;

            function handleDragStart(e) {
                isDragging = true;
                startX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
                startY = e.clientY || (e.touches && e.touches[0].clientY) || 0;
                card.classList.add('dragging');
                card.style.transition = 'none';
            }

            function handleDragMove(e) {
                if (!isDragging) return;
                e.preventDefault();

                const clientX = e.clientX || (e.touches && e.touches[0].clientX) || 0;
                const clientY = e.clientY || (e.touches && e.touches[0].clientY) || 0;

                currentX = clientX - startX;
                currentY = clientY - startY;

                // Apply transform with subtle rotation
                const rotation = currentX * 0.03;
                card.style.transform = `translateX(${currentX}px) translateY(${currentY}px) rotate(${rotation}deg)`;

                // Update swipe indicators
                card.classList.remove('swiping-right', 'swiping-left', 'swiping-down');

                if (currentX > INDICATOR_THRESHOLD) {
                    card.classList.add('swiping-right');
                } else if (currentX < -INDICATOR_THRESHOLD) {
                    card.classList.add('swiping-left');
                } else if (currentY > INDICATOR_THRESHOLD) {
                    card.classList.add('swiping-down');
                }
            }

            function handleDragEnd() {
                if (!isDragging) return;
                isDragging = false;
                card.classList.remove('dragging');

                // Check if threshold reached
                if (currentX > SWIPE_THRESHOLD) {
                    animateOut('right');
                } else if (currentX < -SWIPE_THRESHOLD) {
                    animateOut('left');
                } else if (currentY > SWIPE_THRESHOLD) {
                    animateOut('down');
                } else {
                    snapBack();
                }
            }

            function animateOut(direction) {
                const translateX = direction === 'right' ? 800 : direction === 'left' ? -800 : 0;
                const translateY = direction === 'down' ? 600 : 0;
                const rotation = direction === 'right' ? 15 : direction === 'left' ? -15 : 0;

                card.style.transition = 'transform 0.3s ease-out, opacity 0.3s';
                card.style.transform = `translateX(${translateX}px) translateY(${translateY}px) rotate(${rotation}deg)`;
                card.style.opacity = '0';

                setTimeout(() => {
                    const actionMap = { right: 'like', left: 'pass', down: 'maybe' };
                    window.location.href = '/review/' + actionMap[direction];
                }, 280);
            }

            function snapBack() {
                card.style.transition = 'transform 0.3s ease-out';
                card.style.transform = 'translateX(0) translateY(0) rotate(0deg)';
                card.classList.remove('swiping-right', 'swiping-left', 'swiping-down');
                currentX = 0;
                currentY = 0;
            }

            // Mouse events
            card.addEventListener('mousedown', handleDragStart);
            document.addEventListener('mousemove', handleDragMove);
            document.addEventListener('mouseup', handleDragEnd);

            // Touch events
            card.addEventListener('touchstart', handleDragStart, { passive: false });
            document.addEventListener('touchmove', handleDragMove, { passive: false });
            document.addEventListener('touchend', handleDragEnd);

            // Snap back button
            if (snapBackBtn) {
                snapBackBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    snapBack();
                });
            }

            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

                switch(e.key) {
                    case 'ArrowLeft':
                        e.preventDefault();
                        animateOut('left');
                        break;
                    case 'ArrowDown':
                        e.preventDefault();
                        animateOut('down');
                        break;
                    case 'ArrowRight':
                        e.preventDefault();
                        animateOut('right');
                        break;
                    case 'z':
                    case 'Z':
                        e.preventDefault();
                        window.location.href = '/undo';
                        break;
                }
            });
        })();
    </script>
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

        # TRIGGER LEARNING - This is the key feedback loop!
        _trigger_learning()

        return render_template_string(
            PROFESSIONAL_TEMPLATE,
            complete=True,
            liked_count=liked,
            maybe_count=maybe,
            passed_count=passed
        )

    job = current_jobs[current_index[0]]

    # Get next job for card stack preview
    next_job = None
    if current_index[0] + 1 < len(current_jobs):
        next_job = current_jobs[current_index[0] + 1]

    # Prepare clean display values
    title_display = clean_text(job.get('title', 'Untitled Position'), 150)
    company_display = get_display_value(job.get('company'), 'Company not listed')

    # Location: prefer city, fall back to location
    location = job.get('city') or job.get('location') or ''
    location_display = get_display_value(location, 'Not specified')

    # Salary
    salary_display = get_display_value(job.get('salary'), 'Not listed')

    # Deadline
    deadline_display = get_display_value(job.get('deadline'), 'Not specified')

    # Description - clean and truncate
    description = job.get('description', '')
    description_display = clean_text(description, 300) if description else None

    # Requirements - clean each item
    requirements = job.get('requirements', [])
    if requirements:
        requirements_display = [clean_text(r, 150) for r in requirements[:5] if r and len(r.strip()) > 3]
    else:
        requirements_display = []

    # AI Summary
    ai_summary = job.get('ai_summary', '')
    ai_summary_display = clean_text(ai_summary, 400) if ai_summary else None

    return render_template_string(
        PROFESSIONAL_TEMPLATE,
        job=job,
        next_job=next_job,
        current=current_index[0],
        total=len(current_jobs),
        complete=False,
        can_undo=len(review_history) > 0,
        # Clean display values
        title_display=title_display,
        company_display=company_display,
        location_display=location_display,
        salary_display=salary_display,
        deadline_display=deadline_display,
        description_display=description_display,
        requirements_display=requirements_display,
        ai_summary_display=ai_summary_display,
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

        # Save to history for undo
        review_history.append({
            'index': current_index[0],
            'job': job,
            'action': action
        })

        # Save to tracker
        tracker.add_job(job, status=status)

        # Move to next
        current_index[0] += 1

    return redirect('/')


@app.route('/undo')
def undo_action():
    """Undo the last review action"""

    if review_history:
        last_action = review_history.pop()
        current_index[0] = last_action['index']

        # Remove from tracker (reset to new)
        job = last_action['job']
        if job['url'] in tracker.jobs:
            tracker.jobs[job['url']]['status'] = 'new'

    return redirect('/')


def open_browser_explicitly(url):
    """Try multiple methods to open the browser to a specific URL"""

    # Method 1: Try opening with specific browser on Mac
    if sys.platform == 'darwin':
        try:
            subprocess.run(['open', '-a', 'Safari', url], check=False)
            return True
        except:
            pass
        try:
            subprocess.run(['open', '-a', 'Google Chrome', url], check=False)
            return True
        except:
            pass
        try:
            subprocess.run(['open', url], check=False)
            return True
        except:
            pass

    # Method 2: Standard webbrowser with new window
    try:
        webbrowser.open(url, new=2)  # new=2 opens in new tab
        return True
    except:
        pass

    return False


def start_review_server(jobs, port=None):
    """Start the review server"""

    global current_jobs, current_index, tracker, review_history

    if port is None:
        port = DEFAULT_PORT

    current_jobs = jobs
    current_index[0] = 0
    review_history = []
    tracker = EnhancedJobTracker()

    url = f'http://localhost:{port}'

    print()
    print("=" * 60)
    print("  JOB REVIEW GUI")
    print("=" * 60)
    print()
    print(f"  Jobs to review: {len(jobs)}")
    print()
    print("  Open this URL in your browser:")
    print()
    print(f"  >>> {url} <<<")
    print()
    print("  Keyboard shortcuts:")
    print("    Arrow Left  = Pass")
    print("    Arrow Down  = Maybe")
    print("    Arrow Right = Like")
    print("    Z           = Undo")
    print()
    print("  Press Ctrl+C to stop the server")
    print("=" * 60)
    print()

    # Try to open browser after a short delay
    def delayed_open():
        import time
        time.sleep(1.5)
        success = open_browser_explicitly(url)
        if not success:
            print(f"\n  Could not auto-open browser.")
            print(f"  Please manually open: {url}\n")

    threading.Thread(target=delayed_open, daemon=True).start()

    # Run Flask with minimal output
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    try:
        app.run(host='127.0.0.1', port=port, debug=False, threaded=True)
    except OSError as e:
        if 'Address already in use' in str(e):
            print(f"\n  Port {port} is in use. Trying port {port + 1}...")
            app.run(host='127.0.0.1', port=port + 1, debug=False, threaded=True)
        else:
            raise


if __name__ == "__main__":
    # Test with sample data
    sample_jobs = [
        {
            "title": "Machine Learning Engineer - Healthcare AI Team",
            "company": "Google DeepMind",
            "city": "London",
            "location": "UK",
            "type": "Industry",
            "url": "https://deepmind.com/job/123",
            "salary": "GBP 80,000 - 120,000",
            "post_date": "2025-12-01",
            "deadline": "2026-01-31",
            "cv_required": "Yes",
            "cover_letter_required": "Optional",
            "requirements": [
                "PhD or Master's in Machine Learning, Computer Science, or related field",
                "Strong experience with PyTorch or TensorFlow",
                "Published research in top ML conferences (NeurIPS, ICML, ICLR)",
                "Experience with healthcare/medical data is a plus"
            ],
            "expectations": [
                "Build state-of-the-art ML models for medical applications",
                "Collaborate with clinical researchers"
            ],
            "ai_summary": "Excellent match for your ML + healthcare interests. This role combines cutting-edge AI research with real-world medical applications at one of the world's leading AI labs.",
            "quality_score": 92,
            "source": "Google Search",
        },
        {
            "title": "Graduate Data Scientist",
            "company": "NHS Digital",
            "city": "Leeds",
            "location": "UK",
            "type": "Industry",
            "url": "https://nhsdigital.nhs.uk/job/456",
            "salary": "GBP 35,000 - 45,000",
            "post_date": "2025-12-05",
            "deadline": "2026-02-15",
            "requirements": [
                "Recent graduate with degree in Data Science, Statistics, or related field",
                "Python programming skills",
                "Interest in healthcare data"
            ],
            "ai_summary": "Graduate-level role in healthcare data - great entry point for NHS career path.",
            "quality_score": 78,
            "source": "jobs.ac.uk",
        }
    ]

    start_review_server(sample_jobs)
