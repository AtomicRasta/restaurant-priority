#!/usr/bin/env python3
"""Check restaurant availability on OpenTable and Resy for Fri 3/13 and Sat 3/14."""

import json
import subprocess
import re
import sys
import urllib.parse

RESTAURANTS = [
    "40 Love Scottsdale",
    "Maple & Ash Scottsdale",
    "Nobu Scottsdale",
    "Catch Scottsdale",
    "FLINT by Baltaire Scottsdale",
    "Bourbon & Bones Scottsdale",
    "Mowry and Cotton Scottsdale",
    "Shiv Supper Club Scottsdale",
    "Jing Scottsdale",
    "Society Swan Scottsdale",
    "Sexy Roman Scottsdale",
    "Cleaverman Scottsdale",
    "DiMaggios Scottsdale",
    "Akamura Scottsdale",
    "Hainoo Scottsdale",
    "Chico Malo Phoenix",
    "Kid Sister Wine Phoenix",
    "Cocina Chiwas Phoenix",
    "Confluence Scottsdale",
]

DATES = ["2026-03-13", "2026-03-14"]
PARTY_SIZE = 2

def curl(url, headers=None):
    cmd = ["curl", "-sL", "-A", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"]
    if headers:
        for k, v in headers.items():
            cmd += ["-H", f"{k}: {v}"]
    cmd.append(url)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    return result.stdout

def check_opentable(name):
    """Search OpenTable for restaurant and check availability."""
    encoded = urllib.parse.quote(name)
    # Search for the restaurant
    url = f"https://www.opentable.com/dapi/fe/gql?optype=query&opname=Autocomplete"
    # Try the autocomplete endpoint
    search_url = f"https://www.opentable.com/s?term={encoded}&covers=2&dateTime=2026-03-13T19:00&metroId=50"
    
    # Actually, let's try the direct restaurant search API
    api_url = f"https://www.opentable.com/dapi/fe/gql?optype=query&opname=RestaurantsAvailability"
    
    # Simpler: search and extract restaurant ID from results
    search_html = curl(f"https://www.opentable.com/s?term={encoded}")
    
    # Look for restaurant profile URLs
    matches = re.findall(r'/r/([a-z0-9-]+)', search_html)
    return matches[:3] if matches else []

def check_opentable_availability(slug, date, party_size=2):
    """Check OpenTable availability for a specific restaurant."""
    url = f"https://www.opentable.com/booking/availability?slug={slug}&partySize={party_size}&dateTime={date}T19:00&includeNextAvailable=true"
    headers = {
        "Accept": "application/json",
        "x-csrf-token": "",
    }
    # Try the public availability page
    page_url = f"https://www.opentable.com/r/{slug}?dateTime={date}T19:00&covers={party_size}&language=en-US"
    html = curl(page_url)
    
    # Extract availability data from the page
    # Look for time slot data in the JSON embedded in the page
    json_match = re.search(r'"availabilityToken":\s*"([^"]*)"', html)
    slots_match = re.findall(r'"dateTime":"([^"]*)".*?"slotAvailability"', html)
    
    # Try to find availability times from the page content
    time_matches = re.findall(r'data-test="time-slot"[^>]*>([^<]+)<', html)
    if not time_matches:
        time_matches = re.findall(r'"time":"(\d{1,2}:\d{2}\s*[AP]M)"', html)
    if not time_matches:
        time_matches = re.findall(r'(\d{1,2}:\d{2}\s*PM)', html)
    
    return time_matches

# For each restaurant, try to find it on OpenTable
print("=" * 60)
print("RESTAURANT AVAILABILITY CHECK")
print(f"Dates: Fri 3/13 and Sat 3/14, 6:30-7:30 PM, Party of {PARTY_SIZE}")
print("=" * 60)

for name in RESTAURANTS:
    print(f"\n🔍 Searching: {name}...")
    slugs = check_opentable(name)
    if slugs:
        print(f"   Found OpenTable slugs: {slugs[:2]}")
        for slug in slugs[:1]:
            for date in DATES:
                day_name = "Fri" if date.endswith("13") else "Sat"
                times = check_opentable_availability(slug, date)
                if times:
                    print(f"   ✅ {day_name} {date}: {times}")
                else:
                    print(f"   ❓ {day_name} {date}: no slot data extracted")
    else:
        print(f"   ⚠️  Not found on OpenTable")
