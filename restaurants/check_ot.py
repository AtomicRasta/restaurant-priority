#!/usr/bin/env python3
"""Check OpenTable availability for known restaurant IDs."""
import urllib.request
import json
import ssl

ctx = ssl.create_default_context()

OT_RESTAURANTS = {
    "40 Love": 1354504,
    "FLINT by Baltaire": 1045138,
    "Bourbon & Bones": 1075225,
    "Society Swan": 1460734,
    "Cleaverman": 1392139,
    "Hainoo": 1293022,
}

DATES = ["2026-03-13", "2026-03-14"]
PARTY_SIZE = 2

def check_ot_availability(rid, date, party_size=2):
    """Try multiple OpenTable API endpoints."""
    # Try the restref widget API
    url = f"https://www.opentable.com/widget/reservation/loader?rid={rid}&type=standard&theme=standard&color=4&dark=false&iframe=true&domain=com&lang=en-US&newtab=true&ot_source=Restaurant%20website"
    
    # Try the availability endpoint  
    avail_url = f"https://www.opentable.com/booking/availability?restaurantId={rid}&dateTime={date}T19:00&partySize={party_size}&includeNextAvailable=true"
    
    try:
        req = urllib.request.Request(avail_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "application/json",
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        data = resp.read().decode()
        return data[:1000]
    except Exception as e:
        return f"Error: {e}"

def check_ot_restref(rid, date, party_size=2):
    """Try the restref availability API."""
    url = f"https://www.opentable.com/restref/api/availability?rid={rid}&datetime={date}T19:00&covers={party_size}&language=en-US&channel=4"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
            "Accept": "application/json",
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        data = resp.read().decode()
        return data[:1000]
    except Exception as e:
        return f"Error: {e}"

# Also check Resy for Catch and Kid Sister
def check_resy_search(query):
    """Search Resy for a restaurant."""
    url = f"https://api.resy.com/3/venuesearch/search?query={urllib.parse.quote(query)}&geo=%7B%22latitude%22%3A33.49%2C%22longitude%22%3A-111.93%7D&per_page=5"
    try:
        req = urllib.request.Request(url, headers={
            "Authorization": 'ResyAPI api_key="VbWk7s3L4KiK5fzlO7JD3Q5EYolJI7n5"',
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        return resp.read().decode()[:2000]
    except Exception as e:
        return f"Error: {e}"

import urllib.parse

print("=" * 60)
print("OPENTABLE AVAILABILITY CHECK")
print(f"Fri 3/13 & Sat 3/14, 6:30-7:30 PM, Party of {PARTY_SIZE}")
print("=" * 60)

for name, rid in OT_RESTAURANTS.items():
    print(f"\n🍽️  {name} (rid={rid})")
    for date in DATES:
        day = "Fri" if date.endswith("13") else "Sat"
        result = check_ot_availability(rid, date)
        print(f"  {day} booking/availability: {result[:300]}")
        result2 = check_ot_restref(rid, date)
        print(f"  {day} restref/api: {result2[:300]}")

print("\n" + "=" * 60)
print("RESY SEARCH")
print("=" * 60)
for q in ["Catch Scottsdale", "Kid Sister Phoenix", "Maple Ash Scottsdale", "Nobu Scottsdale", "Sexy Roman Scottsdale", "Jing Scottsdale"]:
    print(f"\n🔍 {q}")
    r = check_resy_search(q)
    print(f"  {r[:500]}")
