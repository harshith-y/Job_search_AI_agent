# 🎯 Dual Job Search System - Complete Guide
## Industry ML Jobs + PhD Positions

---

## 📊 Quick Comparison: Industry vs PhD Search

| Aspect | Industry Jobs | PhD Positions |
|--------|--------------|---------------|
| **Volume** | 50-100 new/week | 5-20 new/week |
| **Timing** | Year-round | Sep-Feb peak |
| **Sources** | LinkedIn, company sites | FindAPhD, university sites |
| **Key Factor** | Role/salary match | Funding + research area |
| **Application** | CV + cover letter | Research proposal + references |
| **Decision time** | Days/weeks | Weeks/months |
| **Scraping difficulty** | Medium-Hard | Easy-Medium |

---

## 🚀 Quick Start (Pick Your Approach)

### Option A: Single Agent (Simpler)
Run one search covering both industry + PhD positions.

**Pros:** Simple setup, one notification  
**Cons:** Mixed results, harder to prioritize

### Option B: Dual Agent (Recommended)
Run TWO separate searches with different configs.

**Pros:** Clear separation, different filters, easier to prioritize  
**Cons:** Slightly more setup

---

## 🎓 Option B Setup: Dual Agent System

### Step 1: File Structure

```
Job_search_AI_agent/
├── agent_dual.py          # NEW: Dual filtering logic
├── main_dual.py           # NEW: Runs both searches
├── phd_scraper.py         # NEW: PhD-specific scrapers
├── phd_config.yaml        # NEW: PhD sources
├── config.yaml            # EXISTING: Industry sources
├── memory.py              # EXISTING: Tracks seen jobs
├── seen_jobs.txt          # Industry memory
├── seen_phds.txt          # NEW: PhD memory (separate)
└── .env                   # EXISTING: API keys
```

### Step 2: Install Additional Dependencies

```bash
# No new dependencies needed!
# Same requirements as original
pip install -r requirements.txt
```

### Step 3: Configure Dual Search

Edit `.env`:
```bash
# Existing settings
OPENAI_API_KEY=sk-proj-xxxxx

# Notification settings (same for both)
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxxx
```

### Step 4: Run Dual Search

```bash
# Run both searches
python main_dual.py

# Or run individually
python main_dual.py industry  # Industry only
python main_dual.py phd       # PhD only
```

---

## 📅 Scheduling Strategy

### Recommended Schedule:

```bash
# Industry jobs: Daily at 8 AM (high volume, time-sensitive)
0 8 * * * cd /path/to/agent && python main_dual.py industry

# PhD positions: Monday, Wednesday, Friday at 9 AM (lower volume)
0 9 * * 1,3,5 cd /path/to/agent && python main_dual.py phd

# OR run both together once daily
0 8 * * * cd /path/to/agent && python main_dual.py
```

### Why Different Schedules?

**Industry (Daily):**
- Jobs posted constantly
- First-mover advantage
- Quick application cycles

**PhD (3x/week):**
- Fewer new positions
- Longer application cycles
- More time to prepare
- Less notification fatigue

---

## 🎯 Filtering Differences

### Industry AI Filter Focuses On:
```
✅ Job title match (ML Engineer, Research Scientist, etc.)
✅ Required experience level
✅ Technology stack (PyTorch, TensorFlow)
✅ Location (UK, remote)
✅ Company type (startup, big tech, research lab)
❌ Management roles
❌ Pure software engineering
```

### PhD AI Filter Focuses On:
```
✅ Research area match (CV, NLP, RL, etc.)
✅ FUNDING STATUS (critical!)
✅ Supervisor expertise
✅ University/institute reputation
✅ Application deadline
❌ Unfunded positions
❌ Unrelated research areas
❌ Expired deadlines
```

---

## 💰 Funding Status Detection (PhDs)

The PhD filter specifically looks for:

### ✅ FUNDED (Ideal):
Keywords: "fully funded", "stipend", "scholarship", "EPSRC", "UKRI", "CDT", "DTP"

### ⚠️ FUNDING UNCLEAR (Check manually):
No funding mentioned, vague language

### ❌ UNFUNDED (Skip):
Keywords: "fees only", "self-funded", "no funding available"

**Why this matters:** Unfunded PhDs in UK cost £20k-30k/year. Not worth applying unless exceptional circumstances.

---

## 🌐 PhD Scraping Sources (Priority Order)

### Tier 1: Start Here (Easy + High Coverage)

1. **FindAPhD.com** ⭐⭐⭐⭐⭐
   - UK's largest PhD database
   - Easy to scrape
   - Consistent structure
   - ~80% of UK PhDs listed
   - Scraper: `phd_scraper.py`

2. **jobs.ac.uk (Studentships)** ⭐⭐⭐⭐
   - Already have scraper!
   - Just add `JobType=Studentship` filter
   - Good UK coverage

3. **Alan Turing Institute** ⭐⭐⭐⭐
   - Small but high-quality
   - Easy to scrape
   - Prestigious positions

### Tier 2: Add After Tier 1 Working

4. **CDT Websites** ⭐⭐⭐
   - Centres for Doctoral Training
   - 4-year funded programmes
   - Need individual scrapers per CDT

5. **Top University Departments** ⭐⭐
   - Cambridge, Oxford, Imperial, UCL, Edinburgh
   - Each needs custom scraper
   - Lower ROI vs FindAPhD

### Tier 3: Manual Check (Don't Scrape)

6. **Individual Supervisor Pages**
   - Too varied to scrape
   - Check manually if interested in specific lab

7. **Twitter/Mailing Lists**
   - Informal announcements
   - Manual monitoring

---

## 🛠️ Implementation Roadmap

### Week 1: Industry Search Only
```
✅ Fork friend's repo
✅ Fix OpenAI SDK
✅ Configure UK ML sites
✅ Test and deploy
✅ Run for 1 week
```

### Week 2: Add PhD Basics
```
✅ Add FindAPhD scraper
✅ Implement PhD filtering logic
✅ Test PhD search separately
✅ Compare quality of matches
```

### Week 3: Dual System
```
✅ Integrate dual-agent system
✅ Configure separate notifications
✅ Set up scheduling
✅ Run both searches
```

### Week 4+: Expand
```
✅ Add more PhD sources (jobs.ac.uk PhDs)
✅ Add university-specific scrapers
✅ Fine-tune filtering
✅ Track application success
```

---

## 📊 Expected Results (After 1 Month)

### Industry Jobs:
- **Volume:** 10-20 relevant jobs/week
- **Apply to:** 2-5 jobs/week
- **Time saved:** 5-7 hours/week
- **Cost:** $2-5/month

### PhD Positions:
- **Volume:** 2-5 relevant PhDs/week
- **Apply to:** 1-2 PhDs/week
- **Time saved:** 2-3 hours/week
- **Cost:** $1-2/month

### Total:
- **Notifications:** 12-25 opportunities/week
- **Applications:** 3-7 total/week (mix of both)
- **Time saved:** 7-10 hours/week
- **Total cost:** $3-7/month

---

## 🎨 Your Daily Workflow

### Morning Routine (15 mins):
```
8:00 AM → Industry notification arrives
8:05 AM → Review 3-5 industry jobs
8:10 AM → Flag 1-2 for later

9:00 AM → PhD notification (Mon/Wed/Fri)
9:05 AM → Review 1-2 PhD positions
9:10 AM → Check funding status
9:15 AM → Flag if interesting
```

### Application Time (30-60 mins per opportunity):
```
Industry Job:
1. Research company (10 mins)
2. Tailor CV (15 mins)
3. Write cover letter (20 mins)
4. Apply (5 mins)

PhD Position:
1. Research supervisor (15 mins)
2. Review lab publications (15 mins)
3. Draft research proposal outline (30 mins)
4. Save for full application later
```

---

## 🔍 Scraping Difficulty for PhD Sources

| Source | Difficulty | Why | Time to Build |
|--------|-----------|-----|---------------|
| FindAPhD | ⚡ Easy | Static HTML, consistent structure | 1 hour |
| jobs.ac.uk | ⚡ Easy | Already have scraper! | 10 mins |
| Alan Turing | ⚡ Easy | Simple site | 1 hour |
| University Portals | 🔶 Medium | Each different | 2-3 hours each |
| LinkedIn | 🔴 Hard | Anti-bot, requires login | 8-10 hours |
| Individual Labs | 🔴 Hard | Too varied, not worth it | N/A |

**Recommendation:** Start with FindAPhD + jobs.ac.uk. They cover 80-90% of UK PhDs.

---

## ⚙️ Customization Guide

### For Industry Search:

Edit `agent_dual.py` - `filter_industry_job()`:
```python
Relevant roles:
- Add your specific interests
- Adjust experience level
- Add specific companies to prioritize
```

### For PhD Search:

Edit `agent_dual.py` - `filter_phd_position()`:
```python
Required areas:
- Add your research interests
- Specify funding requirements
- Add preferred universities
- Set deadline preferences
```

### For Sources:

Edit `phd_config.yaml`:
```yaml
phd_easy_sites:
  - name: Your Target University
    url: https://university.edu/phd-opportunities
  - name: Specific CDT
    url: https://cdt.ac.uk/opportunities
```

---

## 🎯 Success Metrics

### After 2 Weeks, Evaluate:

**Industry Search:**
- [ ] Getting 10+ relevant jobs/week?
- [ ] Quality matches (not too junior/senior)?
- [ ] Actually applying to 2-3/week?
- [ ] Saving time vs manual search?

**PhD Search:**
- [ ] Getting 2-5 relevant PhDs/week?
- [ ] Funding status clearly identified?
- [ ] Research areas align well?
- [ ] Catching opportunities early?

### Red Flags:
- ❌ Too many false positives (>50%)
- ❌ Missing obvious good matches
- ❌ Scrapers constantly breaking
- ❌ Not actually using notifications

### If Red Flags: 
1. Adjust AI filtering prompts
2. Add/remove sources
3. Check scraper functionality
4. Consider manual LinkedIn supplement

---

## 💡 Pro Tips

### 1. Separate Decision Modes
```
Industry → "Am I interested?" (quick decision)
PhD → "Is this my future?" (careful consideration)
```

### 2. Application Strategy
```
Industry: Apply broadly (5-10/week)
PhD: Apply selectively (1-2/month)
```

### 3. Networking
```
Industry: Apply first, network second
PhD: Network first (email supervisor), apply second
```

### 4. Tracking
```
Spreadsheet columns:
- Position type (Industry/PhD)
- Title
- Organization
- Found via (agent/manual)
- Application date
- Status
- Notes
```

### 5. Time Management
```
Morning: Review notifications (15 mins)
Afternoon: Applications (1-2 hours)
Evening: Networking/research (30 mins)
```

---

## 🚨 Common Pitfalls

### ❌ Don't:
1. **Auto-apply to PhDs** - They need thought and research proposals
2. **Apply to unfunded PhDs** - Unless you have £100k lying around
3. **Ignore deadlines** - PhDs have hard deadlines
4. **Mix industry/PhD mindsets** - They're different processes
5. **Over-rely on automation** - Still need manual LinkedIn checks

### ✅ Do:
1. **Review all notifications** - Don't let them pile up
2. **Track everything** - Spreadsheet is your friend
3. **Network actively** - Especially for PhDs
4. **Update filters weekly** - Refine based on results
5. **Maintain scrapers** - Fix when they break

---

## 🎓 PhD Application Timeline

Understanding timing helps prioritize:

```
September: New positions posted → HIGH PRIORITY
October: More positions → HIGH PRIORITY  
November: Peak season → HIGH PRIORITY
December: Slowing down → MEDIUM PRIORITY
January: Late postings → MEDIUM PRIORITY
February: Final calls → LOW PRIORITY (often too late)
March-August: Very few → LOW PRIORITY

Start dates: Usually September/October
```

**Action:** Increase PhD search frequency Sep-Dec, reduce Jan-Aug.

---

## 📚 Additional Resources

### For Industry Jobs:
- [Original setup guide](SETUP_GUIDE.md)
- [Scraping difficulty guide](SCRAPING_DIFFICULTY_GUIDE.md)

### For PhD Positions:
- [PhD config](phd_config.yaml)
- [PhD scraper](phd_scraper.py)
- FindAPhD: https://www.findaphd.com
- UKRI Opportunities: https://www.ukri.org/opportunity/

### For Dual System:
- [Dual agent code](agent_dual.py)
- [Dual main script](main_dual.py)

---

## 🎯 Decision Framework: Should You Apply?

### Industry Job Decision (Quick):
```
YES if:
✅ Role matches skills (70%+)
✅ Location acceptable
✅ Salary reasonable (if listed)
✅ Company interesting

Apply even if:
⚠️ Slightly under-qualified
⚠️ Slightly over-qualified
⚠️ Unfamiliar tech (can learn)
```

### PhD Position Decision (Careful):
```
YES if:
✅ Fully funded
✅ Research area perfect match
✅ Supervisor has good publications
✅ University/institute reputable
✅ Within application deadline

Maybe if:
⚠️ Funding unclear (check before applying)
⚠️ Research area adjacent to interests
⚠️ Deadline approaching (if can prepare quickly)

NO if:
❌ Unfunded
❌ Unrelated research area
❌ Deadline passed
❌ No supervisor contact info
```

---

## 🚀 Ready to Start?

1. **Download all files** from outputs
2. **Read this guide** (you're here!)
3. **Set up industry search first** (Week 1)
4. **Add PhD search** (Week 2-3)
5. **Run dual system** (Week 4+)

Good luck with your job search! 🎯

**Remember:** The goal is smart notifications + manual quality applications.  
Not automation for automation's sake.
