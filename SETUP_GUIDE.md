# 🚀 Quick Setup Guide - Job Search Notification Agent

**Goal:** Get daily notifications about relevant UK ML/AI jobs, then manually apply with tailored applications.

---

## 📋 What You're Building

```
Daily at 8 AM:
1. Bot scrapes UK ML job sites
2. GPT-4o-mini filters relevant jobs
3. You get Discord/Email notification
4. You review jobs (5 mins)
5. You manually apply to best matches (30 mins)

Time saved: ~5-7 hours/week
Cost: ~$5-10/month (OpenAI API)
```

---

## ⚡ Quick Start (30 minutes)

### Step 1: Clone the Repo

```bash
git clone https://github.com/J0MT/Job_search_AI_agent.git
cd Job_search_AI_agent
```

### Step 2: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Install updated OpenAI SDK
pip install --upgrade openai
```

### Step 3: Replace Files with Fixed Versions

Replace these files with the improved versions I provided:
- `agent.py` (fixed OpenAI SDK, cheaper model)
- `main.py` (improved workflow)
- `notifier.py` (added email support)
- `config.yaml` (UK ML-focused sites)

### Step 4: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your keys
nano .env  # or use any text editor
```

**Required:**
- `OPENAI_API_KEY` - Get from https://platform.openai.com/api-keys

**Choose notification method:**

**Option A: Discord Webhook (Easiest)**
1. Open Discord server
2. Server Settings → Integrations → Webhooks
3. Create New Webhook
4. Copy webhook URL to `.env`

**Option B: Email**
1. For Gmail: Create App Password (https://support.google.com/accounts/answer/185833)
2. Add SMTP settings to `.env`

### Step 5: Test It

```bash
# Test scraper
python easy_scraper.py

# Test AI filtering
python main.py

# Test notifications
python notifier.py
```

---

## 📅 Schedule Daily Runs

### Option A: Cron (Mac/Linux)

```bash
# Edit crontab
crontab -e

# Add this line (runs at 8 AM daily)
0 8 * * * cd /path/to/Job_search_AI_agent && /path/to/venv/bin/python main.py >> job_search.log 2>&1
```

### Option B: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 8:00 AM
4. Action: Start a program
5. Program: `C:\path\to\venv\Scripts\python.exe`
6. Arguments: `C:\path\to\Job_search_AI_agent\main.py`

### Option C: Run Manually

```bash
# Activate environment
source venv/bin/activate

# Run agent
python main.py
```

---

## 🎯 Customizing for Your Needs

### 1. Adjust AI Filtering (agent.py)

Change the criteria in `agent.py`:

```python
prompt = f"""
You are an AI assistant helping a user find jobs related to:
- Machine Learning Research
- Computer Vision
- NLP / Large Language Models
- Add your specific interests here

Focus on:
- Senior-level positions
- UK-based roles only
- Companies doing cutting-edge research
"""
```

### 2. Add More Job Sites (config.yaml)

Add sites you want to monitor:

```yaml
easy_sites:
  - name: Your University
    url: https://university.edu/jobs
```

### 3. Change Notification Format (notifier.py)

Customize the Discord/Email message format to your preference.

---

## 💰 Cost Breakdown

**OpenAI API (gpt-4o-mini):**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens

**Typical daily usage:**
- 20 jobs scraped
- ~500 words per job description
- Total: ~10,000 tokens/day
- Cost: **$0.03/day = ~$1/month**

**Maximum scenario (100 jobs/day):**
- Cost: **$0.15/day = ~$5/month**

**Compare to gpt-4:** Would be ~$60/month 🤯

---

## 🎨 Your Daily Workflow

### Morning (5-10 mins)

```
8:00 AM → Notification arrives
8:05 AM → Open Discord/Email
8:10 AM → Review 3-5 relevant jobs
8:15 AM → Decide which to apply to
```

### Application Time (30-45 mins per job)

```
1. Read full job description
2. Research the company
3. Tailor CV for role
4. Write custom cover letter
5. Submit application
6. Track in spreadsheet
```

**Result:** 2-3 high-quality applications/day = 10-15/week

---

## 🔧 Troubleshooting

### "OpenAI API Error"
- Check your API key is correct
- Verify you have credits: https://platform.openai.com/usage
- Check rate limits

### "No jobs found"
- Scrapers may have broken (sites changed structure)
- Check which sites are working: run `python easy_scraper.py`
- Comment out broken sites in `config.yaml`

### "Discord notification failed"
- Verify webhook URL is correct
- Test webhook: `curl -X POST -H "Content-Type: application/json" -d '{"content":"test"}' YOUR_WEBHOOK_URL`

### "Too many/few jobs"
- Adjust AI filtering prompt in `agent.py`
- Add more specific keywords
- Exclude certain types of roles

---

## 🚀 Next Steps After Setup

**Week 1:**
- Run daily and review quality of matches
- Track which job sites give best results
- Note any false positives/negatives

**Week 2:**
- Refine AI filtering prompts
- Add/remove job sites
- Adjust notification timing if needed

**Week 3:**
- Consider adding LinkedIn manual checks (10 mins/day)
- Build a simple spreadsheet to track applications
- Optimize your workflow

**Month 2+:**
- Add more complex scrapers (medium_sites)
- Consider building a simple dashboard
- Share improvements back with community

---

## ⚠️ Important Notes

1. **Don't auto-apply** - This system is for notifications only
2. **Scrapers break** - Job sites change, you'll need to update scrapers
3. **Quality > Quantity** - Better to apply to 2 great jobs than 20 mediocre ones
4. **Networking matters** - Use saved time to reach out to people at companies
5. **Track everything** - Keep a spreadsheet of applications/responses

---

## 📊 Success Metrics

After 1 month, evaluate:

- ✅ Time saved searching for jobs
- ✅ Quality of job matches
- ✅ Number of interviews secured
- ✅ Cost (should be ~$5-10/month)

If working well: Keep going!
If not: Adjust filtering or add manual LinkedIn checks

---

## 🤝 Getting Help

- **Scraper broken?** Check GitHub issues
- **Need features?** Fork and customize
- **Want to contribute?** Submit PRs to original repo

---

## 📝 Pro Tips

1. **Set up SMS alerts** - Use Zapier to forward Discord → SMS
2. **Create job spreadsheet** - Track applications, responses, interviews
3. **Network while searching** - Use time saved to connect with people
4. **Update weekly** - Review and refine your search criteria
5. **Stay organized** - Keep CVs/cover letters in a structured folder

---

Good luck with your job search! 🎯
