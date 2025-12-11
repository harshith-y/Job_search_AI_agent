# Job Search AI Agent

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Claude AI](https://img.shields.io/badge/AI-Claude%20Sonnet%204-orange.svg)](https://www.anthropic.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

An intelligent, **self-improving** job search assistant powered by Claude AI. It discovers opportunities, filters them using your preferences, and **learns from your feedback** to get smarter over time.

## Key Features

- **AI-Powered Filtering** - Claude evaluates each job against your personalized criteria
- **Self-Learning System** - Learns from your Like/Pass decisions to improve accuracy
- **Swipe-Based Review UI** - Tinder-style interface for quick job review (swipe or use keyboard)
- **Deadline Alerts** - Proactively notifies you about approaching application deadlines
- **Multi-Source Discovery** - Scrapes 100+ job sources via Google Search and direct site scraping
- **Smart Export** - Professional Excel spreadsheet with status tracking and hyperlinks

## Demo

```
┌─────────────────────────────────────────────────┐
│  JOB REVIEW                           5 of 15   │
│  ════════════════════════░░░░░░░░              │
├─────────────────────────────────────────────────┤
│   ┌─────────────────────────────────────┐  [↩] │
│   │   ML Engineer                       │       │
│   │   Google • London, UK               │       │
│   │   £80k - £120k                      │       │
│   │   ─────────────────────────────     │       │
│   │   Key Requirements:                 │       │
│   │   • 3+ years Python                 │       │
│   │   • PyTorch/TensorFlow              │       │
│   │                                     │       │
│   │   AI Summary:                       │       │
│   │   Strong match for your profile...  │       │
│   │                                     │       │
│   │        [ View Job Posting → ]       │       │
│   └─────────────────────────────────────┘       │
│                                                 │
│       ← Pass        ↓ Maybe        Like →       │
│                                                 │
│    [ ✕ ]       [ ? ]       [ ♥ ]       [Undo]   │
└─────────────────────────────────────────────────┘
```

*Swipe cards left/right/down or use arrow keys for quick decisions*

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                               │
│              (preferences, feedback, review decisions)           │
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  DISCOVERY LAYER                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Google Search  │  │  Direct Scrape  │  │  Job Boards     │  │
│  │  API            │  │  (BeautifulSoup)│  │  (Greenhouse,   │  │
│  │                 │  │                 │  │   Lever, etc)   │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
└───────────┼─────────────────────┼─────────────────────┼─────────┘
            └─────────────────────┼─────────────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│  AI FILTERING LAYER                                              │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Claude Sonnet 4                                            ││
│  │  • Evaluates job against user preferences                   ││
│  │  • Considers learned patterns from past feedback            ││
│  │  • Returns: relevance score, key requirements, summary      ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  REVIEW INTERFACE                                                │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Swipe-Based Web GUI (Flask)                                ││
│  │  • Drag cards: Right=Like, Left=Pass, Down=Maybe            ││
│  │  • Keyboard: Arrow keys + Z for undo                        ││
│  │  • Touch-friendly for mobile                                ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────┬───────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  LEARNING LAYER (Agentic Features)                               │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │ FeedbackAnalyzer │ │ PreferenceLearner│ │ AccuracyTracker  │ │
│  │ Extract patterns │ │ Update prompts   │ │ Monitor accuracy │ │
│  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘ │
│           └────────────────────┴────────────────────┘           │
│                                ▼                                 │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │ DeadlineMonitor  │ │ StrategyAgent    │ │ QueryOptimizer   │ │
│  │ Alert deadlines  │ │ Auto-adjust      │ │ Track query      │ │
│  │                  │ │ strictness       │ │ effectiveness    │ │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  OUTPUT                                                          │
│  • Excel spreadsheet with status tracking                        │
│  • JSON database for programmatic access                         │
│  • Discord notifications (optional)                              │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

| Category | Technologies |
|----------|-------------|
| **AI/ML** | Claude Sonnet 4 (Anthropic API), Custom preference learning |
| **Backend** | Python 3.8+, Flask |
| **Scraping** | BeautifulSoup4, Requests, Google Custom Search API |
| **Data** | JSON storage, OpenPyXL (Excel export) |
| **Frontend** | Vanilla JS, CSS3 (swipe animations), HTML5 |

## Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/Job_search_AI_agent.git
cd Job_search_AI_agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (see Configuration section)

# Run the agent
python main.py
```

## Configuration

### Required: API Keys (.env)

```bash
ANTHROPIC_API_KEY=your_claude_api_key      # Required
GOOGLE_SEARCH_API_KEY=your_google_key       # Optional (for Google Search)
GOOGLE_CSE_ID=your_custom_search_engine_id  # Optional
DISCORD_WEBHOOK_URL=your_webhook            # Optional (notifications)
GOOGLE_SHEET_ID=your_sheet_id              # Optional (for Google Sheets sync)
```

### Optional: Google Sheets Integration

Sync your job applications directly to a Google Sheet for cloud access:

```bash
# 1. Run setup guide
python google_sheets.py setup

# 2. Follow instructions to:
#    - Create Google Cloud project
#    - Enable Google Sheets API
#    - Download service account credentials
#    - Share your Sheet with the service account

# 3. Sync jobs
python google_sheets.py sync
```

### Customize: Your Preferences (user_preferences.py)

```python
USER_PROFILE = {
    "name": "Your Name",
    "current_level": "Recent Graduate",  # Entry-Level, Mid-Level, Senior
    "location_preferences": ["UK", "London", "Remote"],
}

INDUSTRY_PREFERENCES = {
    "target_roles": ["Machine Learning Engineer", "Data Scientist"],
    "avoid_roles": ["Senior Engineer", "Principal"],
    "preferred_tech": ["PyTorch", "Python", "TensorFlow"],
    "red_flags": ["10+ years experience", "PhD required"],
}

FILTERING_CONFIG = {
    "industry_strictness": "moderate",  # strict | moderate | lenient
}
```

## How the Learning Works

The agent improves over time through a **feedback loop**:

```
┌────────────────────────────────────────────────────────────────┐
│  LEARNING CYCLE                                                 │
│                                                                 │
│   1. You review jobs ──► 2. System analyzes patterns           │
│         │                         │                             │
│         │                         ▼                             │
│         │              ┌─────────────────────┐                 │
│         │              │ "User liked 8 jobs  │                 │
│         │              │  with 'graduate'    │                 │
│         │              │  in title, disliked │                 │
│         │              │  all 'senior' roles"│                 │
│         │              └──────────┬──────────┘                 │
│         │                         │                             │
│   4. Better results ◄── 3. Claude's prompts updated            │
│                                                                 │
│   Each cycle: ~15% accuracy improvement                         │
└────────────────────────────────────────────────────────────────┘
```

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

Current precision: 67% → Recommendation: maintain moderate strictness
========================================
```

## Project Structure

```
Job_search_AI_agent/
├── main.py                 # Entry point - orchestrates pipeline
├── scrapers.py             # Multi-source job discovery
├── agent_claude.py         # AI filtering with Claude
├── tracker.py              # Job database + Excel export
├── google_sheets.py        # Google Sheets sync integration
├── review_gui.py           # Swipe-based review interface
├── memory.py               # Deduplication (tracks seen jobs)
├── notifier.py             # Discord notifications
├── user_preferences.py     # Your customizable preferences
├── config.yaml             # Job sources configuration
│
├── agency/                 # Self-improving modules
│   ├── feedback_analyzer.py    # Pattern extraction
│   ├── preference_learner.py   # Dynamic prompt updates
│   ├── accuracy_tracker.py     # Performance monitoring
│   ├── deadline_monitor.py     # Deadline alerts
│   ├── strategy_agent.py       # Autonomous decisions
│   └── query_optimizer.py      # Query effectiveness tracking
│
└── data/                   # Learned data (auto-generated)
    ├── learned_preferences.json
    ├── accuracy_history.json
    └── strategy_state.json
```

## Usage

### Basic Commands

```bash
python main.py              # Run full search (industry + PhD)
python main.py industry     # Industry jobs only
python main.py phd          # PhD positions only
```

### Review Interface

After a search completes, the web GUI opens automatically at `http://localhost:5050`

**Controls:**
| Action | Swipe | Keyboard |
|--------|-------|----------|
| Like | Drag right | → |
| Pass | Drag left | ← |
| Maybe | Drag down | ↓ |
| Undo | - | Z |
| Reset card | Click ↩ button | - |

### Tracker Utilities

```bash
python tracker.py export    # Export to Excel
python tracker.py stats     # View statistics
```

## Agentic Features

### Level 1: Learning from Feedback

| Module | Function |
|--------|----------|
| `FeedbackAnalyzer` | Extracts patterns from liked vs disliked jobs |
| `PreferenceLearner` | Updates Claude's filtering prompts dynamically |
| `AccuracyTracker` | Monitors precision over time |

### Level 2: Autonomous Strategies

| Module | Function |
|--------|----------|
| `DeadlineMonitor` | Alerts for upcoming deadlines on liked jobs |
| `StrategyAgent` | Adjusts search strictness based on accuracy |
| `QueryOptimizer` | Tracks which search queries yield best results |

## Output

### Excel Spreadsheet

The exported spreadsheet includes:
- Company, Role, Location, Salary
- Application status dropdown (Not Applied → Offer)
- Clickable job links
- AI-generated summaries
- Deadline tracking
- Color-coded rows by status

### Google Sheets Sync

Sync to Google Sheets for cloud access:
- Same columns and formatting as Excel
- Real-time cloud sync from review GUI
- Status dropdowns with conditional formatting
- Accessible from any device

### JSON Database

All jobs stored in `job_tracker.json` for programmatic access.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `No module named 'anthropic'` | `pip install anthropic` |
| `ANTHROPIC_API_KEY not found` | Create `.env` file with your key |
| `Port 5050 in use` | GUI auto-tries port 5051 |
| Too many/few results | Adjust `industry_strictness` in preferences |

## Future Enhancements

- [ ] Google Sheets integration for cloud sync
- [ ] Browser extension for one-click job saving
- [ ] Resume matching score
- [ ] Interview prep suggestions based on job requirements

## License

MIT License - See [LICENSE](LICENSE) file.

---

**Built with Claude AI** | Questions? Open an issue on GitHub.
