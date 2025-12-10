# Job Search AI Agent

An intelligent, self-improving job search assistant that finds, filters, and learns from your preferences.

## Overview

This tool automates job searching with AI-powered filtering that **learns from your feedback**. Unlike static job boards, this agent:

- Scrapes jobs from 100+ sources (career pages, job boards, Google Search)
- Filters with Claude AI using your personalized preferences
- **Learns** what you actually like based on your Like/Maybe/Pass decisions
- Tracks deadlines and alerts you to apply before it's too late
- Exports to a professional Excel spreadsheet

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Run the agent
python main.py

# Optional: Search specific types
python main.py industry  # Only industry jobs
python main.py phd       # Only PhD positions
```

## Architecture

```
Job_search_AI_agent/
├── main.py                 # Entry point - orchestrates everything
├── scrapers.py             # Job discovery (Google Search + direct scraping)
├── agent_claude.py         # AI filtering with Claude
├── tracker.py              # Job database + Excel export
├── review_gui.py           # Web interface for reviewing jobs
├── memory.py               # Tracks seen jobs (prevents duplicates)
├── notifier.py             # Discord notifications
├── user_preferences.py     # Your static preferences
├── config.yaml             # Job sources configuration
│
├── agency/                 # AGENTIC FEATURES (self-improving)
│   ├── feedback_analyzer.py    # Extracts patterns from your feedback
│   ├── preference_learner.py   # Updates Claude's prompts dynamically
│   ├── accuracy_tracker.py     # Monitors filtering accuracy over time
│   ├── deadline_monitor.py     # Alerts for upcoming deadlines
│   ├── strategy_agent.py       # Autonomous strategy decisions
│   └── query_optimizer.py      # Tracks which queries work best
│
├── data/                   # Learned data (auto-generated)
│   ├── learned_preferences.json
│   ├── accuracy_history.json
│   └── strategy_state.json
│
└── output files
    ├── job_tracker_enhanced.json      # Job database
    ├── job_applications_enhanced.xlsx # Excel export
    ├── seen_jobs.txt                  # Memory file
    └── seen_phds.txt                  # PhD memory file
```

## How It Works

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│ 1. DISCOVERY                                                         │
│    scrapers.py → Google Search + Direct Site Scraping               │
│    Output: 100-200 raw job listings                                  │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 2. FILTERING                                                         │
│    agent_claude.py → Each job evaluated by Claude AI                │
│    Uses: user_preferences.py + learned_preferences.json             │
│    Output: 30-50 relevant jobs                                       │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 3. REVIEW                                                            │
│    review_gui.py → Web interface with Like/Maybe/Pass buttons       │
│    Keyboard shortcuts: ← Pass, ↓ Maybe, → Like, Z Undo              │
└─────────────────────┬───────────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ 4. LEARNING                                                          │
│    agency/ modules → Analyze feedback, update preferences           │
│    Next search uses what you actually liked, not just what you said │
└─────────────────────────────────────────────────────────────────────┘
```

### The Learning Loop

The key innovation is the **feedback loop**:

1. **You review jobs** with Like/Maybe/Pass
2. **System analyzes patterns**: "User liked 5 'graduate scheme' jobs, disliked 3 'senior' roles"
3. **Claude's prompts are updated**: "LEARNED: User strongly prefers 'graduate scheme', avoid 'senior'"
4. **Next search is smarter**: Better precision, fewer false positives

This happens automatically after each review session.

## Configuration

### Environment Variables (.env)

```bash
ANTHROPIC_API_KEY=your_claude_api_key
GOOGLE_SEARCH_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
DISCORD_WEBHOOK_URL=your_discord_webhook  # Optional
```

### User Preferences (user_preferences.py)

Edit this file to set your static preferences:

```python
USER_PROFILE = {
    "name": "Your Name",
    "current_level": "Recent Graduate",
    "location_preferences": ["UK", "London", "Remote UK"],
}

INDUSTRY_PREFERENCES = {
    "target_roles": ["Machine Learning Engineer", "Data Scientist", ...],
    "avoid_roles": ["Senior Engineer", "PostDoc", ...],
    "preferred_tech": ["PyTorch", "Python", ...],
    "red_flags": ["requires phd", "5+ years experience", ...],
    "bonus_points": ["graduate scheme", "healthcare", ...],
}

FILTERING_CONFIG = {
    "industry_strictness": "lenient",  # strict | moderate | lenient | very_lenient
}
```

### Job Sources (config.yaml)

Add your own job sources:

```yaml
easy_sites:
  - name: Company Name
    url: https://company.com/careers/
    notes: "Good for ML roles"

google_search_queries:
  industry:
    - "machine learning engineer UK"
    - "site:greenhouse.io ML UK"
```

## Agentic Features

### Level 1: Learning from Feedback

| Component | What it does |
|-----------|--------------|
| `FeedbackAnalyzer` | Extracts patterns from liked vs disliked jobs |
| `PreferenceLearner` | Generates dynamic notes for Claude's prompts |
| `AccuracyTracker` | Measures if filtering accuracy improves over time |

**Example learned output:**

```
LEARNED FROM USER FEEDBACK:
========================================
STRONGLY PREFERRED (user consistently likes):
  + 'graduate' (liked 8x vs disliked 1x)
  + 'healthcare' (liked 5x vs disliked 0x)

STRONGLY AVOIDED (user consistently dislikes):
  - 'senior' (disliked 12x vs liked 0x)
  - 'consultant' (disliked 4x vs liked 1x)

FILTERING GUIDANCE: User only liked 35% of suggestions.
  -> Be MORE selective! Apply stricter criteria.
========================================
```

### Level 2: Autonomous Strategies

| Component | What it does |
|-----------|--------------|
| `DeadlineMonitor` | Alerts when liked jobs have approaching deadlines |
| `StrategyAgent` | Adjusts search strictness based on precision |
| `QueryOptimizer` | Tracks which Google queries produce best results |

**Example deadline alert:**

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
DEADLINE ALERTS - Jobs you liked need action!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  [+] Graduate ML Engineer at NHS Digital
      @ Leeds - 3 days left!
  [?] Research Associate at Cambridge
      @ Cambridge - 5 days left!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
```

## Excel Export

The spreadsheet (`job_applications_enhanced.xlsx`) includes:

| Column | Description |
|--------|-------------|
| Company Name | Company or institution |
| Application Status | Dropdown: Not Applied, Submitted, Interview, etc. |
| Role | Job title |
| Salary | Compensation if listed |
| Date Submitted | When you applied |
| Link to Job Req | Clickable "View Job" link |
| Rejection Reason | Dropdown for tracking rejections |
| Location | City and country |
| Deadline | Application deadline |
| Notes | Your notes |
| AI Summary | Claude's analysis |

Features:
- Dark green header with filters
- Color-coded status cells
- Clickable hyperlinks
- Alternating row colors

## CLI Commands

```bash
# Main search
python main.py              # Search both industry + PhD
python main.py industry     # Industry jobs only
python main.py phd          # PhD positions only

# Tracker utilities
python tracker.py export    # Export to Excel
python tracker.py stats     # View statistics
python tracker.py add       # Add manual entry
```

## Review GUI

Access at `http://localhost:5050` after running a search.

**Keyboard Shortcuts:**
- `←` Arrow Left: Pass
- `↓` Arrow Down: Maybe
- `→` Arrow Right: Like
- `Z`: Undo last action

## Data Files

| File | Purpose | When Created |
|------|---------|--------------|
| `job_tracker_enhanced.json` | Main job database | First search |
| `job_applications_enhanced.xlsx` | Excel export | After review |
| `seen_jobs.txt` | Industry job URLs (prevents re-processing) | First search |
| `seen_phds.txt` | PhD URLs | First PhD search |
| `data/learned_preferences.json` | Learned patterns | After first review |
| `data/accuracy_history.json` | Accuracy over time | After first review |
| `data/strategy_state.json` | Agent decisions | When strategy changes |

## Troubleshooting

### "No module named 'anthropic'"
```bash
pip install anthropic
```

### "ANTHROPIC_API_KEY not found"
Create `.env` file with your API key.

### "Port 5050 already in use"
The GUI will automatically try port 5051.

### Jobs not being filtered correctly
1. Check `user_preferences.py` - are your preferences correct?
2. Run a few review sessions so the agent can learn
3. Check `data/learned_preferences.json` to see what was learned

### Too many/few results
Adjust `FILTERING_CONFIG["industry_strictness"]`:
- `strict`: Only perfect matches
- `moderate`: Good matches (default)
- `lenient`: Reasonable matches
- `very_lenient`: Discovery mode (cast wide net)

## Requirements

- Python 3.8+
- Claude API key (Anthropic)
- Google Custom Search API key (optional, for Google Search)

## Dependencies

```
anthropic          # Claude AI
flask              # Review GUI
openpyxl           # Excel export
requests           # HTTP requests
beautifulsoup4     # HTML parsing
python-dotenv      # Environment variables
pyyaml             # Config files
```

## License

MIT License - See LICENSE file.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Built with Claude AI and a passion for making job searching less painful.
