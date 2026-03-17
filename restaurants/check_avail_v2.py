#!/usr/bin/env python3
"""Check availability by scraping reservation platform pages."""
import urllib.request
import urllib.parse
import json
import ssl
import re

ctx = ssl.create_default_context()
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

DATES = ["2026-03-13", "2026-03-14"]
PARTY_SIZE = 2

def fetch(url, headers=None):
    hdrs = {"User-Agent": UA, "Accept": "*/*"}
    if headers:
        hdrs.update(headers)
    req = urllib.request.Request(url, headers=hdrs)
    try:
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return resp.read().decode(errors='replace')
    except Exception as e:
        return f"ERROR: {e}"

def check_opentable_page(slug, date):
    """Load OpenTable restaurant page for a date and extract time slots from embedded JSON."""
    url = f"https://www.opentable.com/r/{slug}?dateTime={date}T19:00&covers={PARTY_SIZE}"
    html = fetch(url)
    if html.startswith("ERROR"):
        return None, html
    
    # Extract timeslot availability from __NEXT_DATA__ or inline JSON
    # Look for availability/timeslot data
    slots = []
    
    # Pattern 1: Look for time slots in the availability section
    time_pattern = re.findall(r'"dateTime":"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?)"', html)
    
    # Pattern 2: Look for slot times like "6:30 PM", "7:00 PM"
    display_times = re.findall(r'(\d{1,2}:\d{2}\s*PM)', html)
    
    # Pattern 3: Look in window.__INITIAL_STATE__ for availability data
    state_match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?})\s*</script>', html, re.DOTALL)
    if state_match:
        try:
            state = json.loads(state_match.group(1))
            # Navigate to availability data
            avail = state.get('availability', {})
            if avail:
                slots.append(f"STATE_AVAIL: {json.dumps(avail)[:500]}")
        except:
            pass
    
    # Filter display times to our 6:30-7:30 window
    target_times = []
    for t in display_times:
        hour_min = t.strip()
        if any(x in hour_min for x in ["6:30", "6:45", "7:00", "7:15", "7:30"]):
            target_times.append(hour_min)
    
    return target_times, time_pattern[:10]

def check_resy_venue(venue_slug, date):
    """Check Resy availability using the find endpoint."""
    # Resy API - need to POST to search first to get venue_id
    url = f"https://api.resy.com/4/find?lat=33.4942&long=-111.9261&day={date}&party_size={PARTY_SIZE}"
    headers = {
        "Authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
        "Accept": "application/json",
        "X-Resy-Auth-Token": "",
        "X-Resy-Universal-Auth": "",
    }
    
    # Try venue-specific availability
    venue_url = f"https://api.resy.com/4/find?venue_id={venue_slug}&day={date}&party_size={PARTY_SIZE}&lat=33.4942&long=-111.9261"
    return fetch(venue_url, headers)

def check_resy_page(slug, date):
    """Check Resy availability by loading the venue page."""
    url = f"https://resy.com/cities/phoenix-az/venues/{slug}?date={date}&seats={PARTY_SIZE}"
    html = fetch(url)
    if html.startswith("ERROR"):
        return html
    
    # Look for availability data in the page
    slots = re.findall(r'"time_slot":"([^"]+)"', html)
    display = re.findall(r'"display_config".*?"time":"([^"]+)"', html)
    return slots[:10] or display[:10] or "No slot data found in page"

# Known OpenTable slugs (from earlier searches)
OT_SLUGS = {
    "40 Love": "40-love-scottsdale",
    "FLINT by Baltaire": "flint-by-baltaire-scottsdale",
    "Bourbon & Bones": "bourbon-and-bones-scottsdale",
    "Society Swan": "society-swan-reservations-scottsdale", 
    "Cleaverman": "cleaverman-scottsdale",
    "Hainoo": "hai-noon-reservations-scottsdale",
    "Chico Malo": "chico-malo-phoenix",
}

# Known Resy slugs
RESY_SLUGS = {
    "Kid Sister": "kid-sister",
    "Catch": "catch-scottsdale",
}

# Check for platforms we don't know yet
UNKNOWN = ["Maple & Ash", "Nobu", "Mowry and Cotton", "Shiv Supper Club", "Jing", 
           "Sexy Roman", "DiMaggios", "Akamura", "Cocina Chiwas", "Confluence"]

print("=" * 60)
print("AVAILABILITY CHECK - Fri 3/13 & Sat 3/14, 6:30-7:30 PM")
print("=" * 60)

# Check OpenTable restaurants
print("\n--- OPENTABLE RESTAURANTS ---")
for name, slug in OT_SLUGS.items():
    print(f"\n🍽️  {name}")
    for date in DATES:
        day = "Fri" if "13" in date else "Sat"
        target_times, all_times = check_opentable_page(slug, date)
        if target_times:
            print(f"  ✅ {day}: Available at {', '.join(set(target_times))}")
        elif all_times:
            print(f"  ⏰ {day}: Times found but outside 6:30-7:30: {all_times[:5]}")
        else:
            print(f"  ❓ {day}: Could not extract availability from page")

# Check Resy restaurants
print("\n--- RESY RESTAURANTS ---")
for name, slug in RESY_SLUGS.items():
    print(f"\n🍽️  {name}")
    for date in DATES:
        day = "Fri" if "13" in date else "Sat"
        result = check_resy_page(slug, date)
        print(f"  {day}: {result}")

# Try to find unknown restaurants on OpenTable
print("\n--- CHECKING UNKNOWN PLATFORMS ---")
for name in UNKNOWN:
    search_name = name.replace("&", "and").replace(" ", "-").lower()
    # Try common OpenTable slug patterns
    slugs_to_try = [
        f"{search_name}-scottsdale",
        f"{search_name}-phoenix",
        f"{search_name}",
    ]
    print(f"\n🔍 {name}")
    for slug in slugs_to_try:
        url = f"https://www.opentable.com/r/{slug}"
        result = fetch(url)
        if "ERROR" not in result and "404" not in result[:200] and len(result) > 5000:
            print(f"  Found on OpenTable: {slug}")
            # Check availability
            for date in DATES:
                day = "Fri" if "13" in date else "Sat"
                target_times, all_times = check_opentable_page(slug, date)
                if target_times:
                    print(f"  ✅ {day}: Available at {', '.join(set(target_times))}")
                else:
                    print(f"  ❓ {day}: No 6:30-7:30 slots extracted")
            break
    else:
        print(f"  Not found on OpenTable with common slugs")
