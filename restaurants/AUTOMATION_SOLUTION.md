## Fully Automated Restaurant Availability Checking

### The Problem
- OpenTable & Resy detect headless browsers and automation
- Bot detection ≠ IP address type (residential vs datacenter)
- Your Mac Mini already has a residential IP (home WiFi) ✅
- Detection happens via: browser fingerprints, automation flags, behavior patterns

### The Solution
Use a **dedicated Chrome profile** that stays logged into your reservation accounts.

### One-Time Setup (5 minutes)

1. **Create automation profile and log in:**
```bash
bash restaurants/setup_automation.sh
```

This will:
- Create `~/.openclaw/chrome-automation/` profile
- Open Chrome where you log into Resy, OpenTable, Tock
- Save your login sessions for automation

2. **That's it!** Now you can run automated checks anytime.

### Running Automated Checks

**Check for 5 restaurants with availability:**
```bash
python3 restaurants/auto_check.py
```

**Check for different number:**
```bash
python3 restaurants/auto_check.py 3  # Stop after finding 3
```

**Results saved to:**
`restaurants/availability_found.json`

### How It Works

1. Uses your dedicated automation Chrome profile (logged-in sessions persist)
2. Runs headless (background, no windows)
3. Checks each restaurant on your list
4. Stops after finding target number with availability
5. Saves results to JSON

### Integration with OpenClaw

Once setup is complete, you can:

**Manual run:**
```bash
python3 restaurants/auto_check.py
```

**Scheduled checking (via cron):**
Set up a weekly check every Monday morning to find Friday/Saturday availability:
```bash
# Add to OpenClaw cron or system crontab
0 9 * * MON cd ~/.openclaw/workspace && python3 restaurants/auto_check.py 5
```

**On-demand from agent:**
Just ask me to check restaurant availability and I'll run the script.

### Why This Works

**Residential IP:** ✅ Already have it (home WiFi)  
**Logged-in sessions:** ✅ Using dedicated profile with saved logins  
**Browser fingerprint:** ✅ Real Chrome browser, not headless automation flags  
**Cookies/history:** ✅ Persistent profile looks like normal usage  
**Rate limiting:** ✅ 1-2 second delays between checks  

### Maintenance

**If sessions expire (rare):**
```bash
# Re-run setup to log in again
bash restaurants/setup_automation.sh
```

**Add new restaurants:**
Edit `RESTAURANTS` list in `auto_check.py`

**Change dates:**
Edit `DATES` variable in `auto_check.py`

### Example Output

```
🔍 Checking restaurant availability...
  Checking Kid Sister... ✅ #1
  Checking Maple & Ash... ❌
  Checking Catch... ❌
  ...

✅ Found 5 restaurants with availability

Kid Sister (resy)
  Fri: 6:00 PM, 6:30 PM, 7:00 PM, 7:30 PM
  Sat: 6:00 PM, 6:30 PM, 7:00 PM

...
```

### Cost: $0
No proxy services, no CAPTCHA solvers, no API fees.  
Just your existing home internet and Chrome browser.
