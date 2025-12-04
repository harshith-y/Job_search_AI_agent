# 📌 Quick Reference - Job Search Agent

## What You're Getting

✅ **Smart notifications** of relevant UK ML/AI jobs  
✅ **You review and manually apply** - no auto-spam  
✅ **Saves 5-7 hours/week** vs manual searching  
✅ **Costs ~$5-10/month** (OpenAI API)  

---

## Files Provided

1. **agent.py** - Fixed OpenAI SDK, 60x cheaper model (gpt-4o-mini)
2. **main.py** - Improved workflow with better error handling
3. **notifier.py** - Discord + Email support
4. **config.yaml** - UK ML/AI focused job sites
5. **requirements.txt** - Updated dependencies
6. **.env.example** - Configuration template
7. **SETUP_GUIDE.md** - Full setup instructions

---

## 30-Second Setup

```bash
# 1. Replace files in friend's repo
cp agent.py main.py notifier.py config.yaml /path/to/Job_search_AI_agent/

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env: Add OPENAI_API_KEY and notification settings

# 4. Test
python main.py

# 5. Schedule daily (optional)
crontab -e
# Add: 0 8 * * * cd /path/to/agent && python main.py
```

---

## Key Improvements Over Original

### ✨ What I Fixed:

1. **OpenAI SDK** - Updated from deprecated to modern API
2. **Cost** - Switched to gpt-4o-mini ($1/mo vs $60/mo)
3. **Email support** - Added as notification option
4. **Better error handling** - Won't crash on single job failure
5. **UK ML focus** - Configured for your target market
6. **Documentation** - Clear setup guide

### 🎯 What You Should Customize:

1. **AI filtering** (agent.py) - Add your specific interests
2. **Job sites** (config.yaml) - Add universities/companies you like
3. **Notification format** (notifier.py) - Match your preference
4. **Schedule** - Pick best time for you (default: 8 AM)

---

## Your Daily Workflow

```
8:00 AM ┃ Bot runs automatically
8:05 AM ┃ Notification: "3 relevant jobs found"
8:10 AM ┃ Review jobs (5 mins)
8:30 AM ┃ Apply to 1-2 best matches (30 mins)
9:00 AM ┃ Continue your day

Time saved: 1-2 hours vs manual searching
```

---

## Cost Breakdown (Monthly)

| Item | Cost |
|------|------|
| OpenAI API (gpt-4o-mini) | $1-5 |
| Server/hosting | $0 (runs locally) |
| Notifications | $0 (Discord/Email free) |
| **Total** | **$1-5/month** 🎉 |

Compare to:
- LoopCV: $29-99/month
- LazyApply: $99-250/month
- Your time: ~$200-400/month (5-7 hrs/wk × £10-15/hr)

---

## Critical Success Factors

### ✅ Do This:
- Tailor each application
- Research companies
- Network while searching
- Track applications
- Update search weekly

### ❌ Don't Do This:
- Auto-apply to everything
- Copy-paste same CV
- Skip company research
- Ignore notifications
- Set and forget

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No jobs found | Check scrapers in config.yaml |
| API error | Verify OpenAI key and credits |
| No notification | Check Discord/Email settings |
| Too many jobs | Tighten AI filter in agent.py |
| Too few jobs | Loosen filter, add more sites |

---

## When to Evaluate (After 2 weeks)

### ✅ Keep using if:
- Getting 5-10 relevant jobs/week
- Quality of matches is good
- Saving time vs manual search
- Getting interviews

### 🔄 Adjust if:
- Too many false positives → Tighten AI filter
- Missing good jobs → Add more sites or manual LinkedIn
- Scrapers breaking → Comment out broken sites

### ❌ Stop if:
- No relevant matches consistently
- All scrapers broken
- Not applying to jobs anyway

---

## Pro Tips

1. **Week 1**: Let it run, observe quality
2. **Week 2**: Refine AI prompts and sites
3. **Week 3**: Add LinkedIn manual check (10 mins/day)
4. **Month 2**: Consider adding medium_sites scrapers

**Ultimate goal:** Spend less time searching, more time applying well.

---

## Support

- Original repo: https://github.com/J0MT/Job_search_AI_agent
- OpenAI API: https://platform.openai.com
- Discord webhooks: Server Settings → Integrations → Webhooks

---

## Quick Links

- [Full Setup Guide](SETUP_GUIDE.md)
- [OpenAI API Keys](https://platform.openai.com/api-keys)
- [Discord Webhooks Guide](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)
- [Gmail App Passwords](https://support.google.com/accounts/answer/185833)

---

**Remember:** This is a notification system, not an auto-applier. 
The value is in smart filtering + manual application with quality.

Good luck! 🚀
