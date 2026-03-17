# Restaurant Availability Workflow

## Current Solution (Until Automation Improves)

### Step 1: Quick Manual Check
Run the quick checker to open all booking pages:
```bash
python3 restaurants/quick_check.py
```

This opens all restaurant booking pages in your browser. Manually note which have availability for:
- Friday 3/14 between 6:30-7:30pm
- Saturday 3/15 between 6:30-7:30pm

### Step 2: Record Results
Create or update `availability_found.json`:
```json
{
  "date_checked": "2026-03-08",
  "target_dates": ["2026-03-14", "2026-03-15"],
  "restaurants_with_availability": [
    {
      "name": "Kid Sister",
      "platform": "resy",
      "friday": ["6:30 PM", "6:45 PM", "7:00 PM", "7:15 PM", "7:30 PM"],
      "saturday": ["6:30 PM", "6:45 PM", "7:00 PM"],
      "url": "https://resy.com/cities/phoenix-az/venues/kid-sister"
    }
  ]
}
```

### Step 3: Book Selected Restaurant
Once you choose which restaurant to book, use the booking script:
```bash
python3 restaurants/book.py --restaurant "Restaurant Name" --date "2026-03-14" --time "7:00 PM"
```

## Why Automation Is Challenging

**OpenTable:**
- HTTP/2 protocol errors indicate aggressive bot detection
- Requires residential proxies or solving CAPTCHA
- API endpoints have changed/are protected

**Resy:**
- Pages load but time slots require JavaScript execution
- Needs more sophisticated wait conditions
- May require logged-in session for some restaurants

## Long-Term Solutions to Implement

1. **Proxy Service Integration**
   - Use services like BrightData, Oxylabs for residential IPs
   - Rotate IPs per request
   - Cost: ~$50-100/month

2. **CAPTCHA Solving**
   - Integrate 2captcha or similar service
   - Add human verification step
   - Cost: ~$1-3 per 1000 solves

3. **Browser Extension**
   - Build Chrome extension for semi-automated checking
   - Leverages your actual browser session
   - More reliable but requires manual trigger

4. **Monitoring Service**
   - Set up continuous monitoring
   - Alert when availability appears
   - Requires dedicated server/service

## Recommended Approach for Now

**Hybrid Manual + Automation:**
1. Use `quick_check.py` to open all pages (30 seconds)
2. Manually scan tabs for availability (2-3 minutes)
3. Log results in structured format
4. Use booking automation once target is selected

**Time investment:** ~5 minutes vs hours of building complex anti-detection
**Reliability:** 100% vs 60-70% with current automation
**Cost:** $0 vs $100+/month for proxy services

## Future Automation Ideas

- [ ] Parse restaurant websites to find direct booking links
- [ ] Use restaurant-provided widgets (less protected)
- [ ] Build relationships with platforms for API access
- [ ] Create booking service with proper infrastructure
- [ ] Integrate with services that already solve this (Resy bots, etc.)
