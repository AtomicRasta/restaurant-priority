# Restaurant Booking System

Complete workflow for checking availability and booking reservations across multiple platforms.

## Quick Start

### 1. Check Availability (5 minutes)
```bash
python3 restaurants/quick_check.py
```
This opens all restaurant booking pages in your browser. Check each tab for Friday 3/14 and Saturday 3/15 between 6:30-7:30pm.

### 2. Record What You Find
Create `restaurants/availability_found.json`:
```bash
cat > restaurants/availability_found.json << 'EOF'
{
  "date_checked": "2026-03-08",
  "target_dates": ["2026-03-14", "2026-03-15"],
  "restaurants_with_availability": [
    {
      "name": "Kid Sister",
      "platform": "resy",
      "friday": ["6:30 PM", "6:45 PM", "7:00 PM"],
      "saturday": ["6:30 PM", "7:00 PM"],
      "url": "https://resy.com/cities/phoenix-az/venues/kid-sister"
    }
  ]
}
EOF
```

### 3. Book Your Choice
```bash
python3 restaurants/book_reservation.py \
  --restaurant "Kid Sister" \
  --date "2026-03-14" \
  --time "7:00 PM" \
  --party-size 2
```

## Files

- **quick_check.py** - Opens all booking pages in browser for manual checking
- **smart_check.py** - Attempts automated checking (currently blocked by platforms)
- **book_reservation.py** - Semi-automated booking once you've chosen
- **data.json** - Your restaurant lists
- **WORKFLOW.md** - Detailed workflow and future automation plans
- **SOLUTION_NOTES.md** - Technical notes on what we tried

## Current Status

✅ **Working:**
- Quick manual checking workflow (5 mins total)
- Semi-automated booking assistance
- Restaurant data management

⚠️ **Blocked:**
- Full automation of availability checking
- OpenTable: HTTP/2 errors, aggressive bot detection
- Resy: Pages load but selectors don't consistently match

## Why Manual Checking for Now?

The platforms have sophisticated bot detection:
- OpenTable blocks headless browsers completely
- Resy requires complex session management
- Both use CAPTCHAs and rate limiting

**Solutions that would work but require investment:**
1. Residential proxy service ($50-100/month)
2. CAPTCHA solving service ($1-3/1000 checks)
3. Browser extension (development time)
4. Professional booking API access (contact platforms)

**Our pragmatic approach:**
- 5 minutes of manual checking = reliable results
- Automation kicks in for booking step
- Can revisit full automation when worth the investment

## Restaurant Platforms

**Resy (7 restaurants):**
- Kid Sister ✅ (confirmed availability)
- Maple & Ash
- Catch
- Nobu
- Jing
- Sexy Roman
- Shiv Supper Club

**OpenTable (7 restaurants):**
- 40 Love
- FLINT by Baltaire
- Bourbon & Bones
- Society Swan
- Cleaverman
- Hainoo
- Mowry and Cotton

**Unknown (5 restaurants):**
- DiMaggios
- Akamura
- Chico Malo
- Cocina Chiwas
- Confluence

## Next Steps

1. Run `quick_check.py` to find 5 restaurants with availability
2. Record results in `availability_found.json`
3. Choose your favorite
4. Use `book_reservation.py` to complete booking
5. Update `data.json` once you visit (move to "wouldReturn" list)

## Future Improvements

- [ ] Add more restaurants to tracking
- [ ] Build Chrome extension for easier checking
- [ ] Investigate official booking APIs
- [ ] Set up monitoring for specific hard-to-get reservations
- [ ] Integrate with calendar for automatic reminders
