#!/usr/bin/env python3
"""Quick manual availability checker - opens booking pages in browser."""
import webbrowser
import time
import json

# Load restaurant data
with open('data.json', 'r') as f:
    data = json.load(f)

# Booking URLs for haven't been yet restaurants
BOOKING_URLS = {
    # OpenTable
    "40 Love": "https://www.opentable.com/r/40-love-scottsdale?dateTime=2026-03-14T18:30&covers=2",
    "FLINT by Baltaire": "https://www.opentable.com/r/flint-by-baltaire-scottsdale?dateTime=2026-03-14T18:30&covers=2",
    "Bourbon & Bones": "https://www.opentable.com/r/bourbon-and-bones-scottsdale?dateTime=2026-03-14T18:30&covers=2",
    "Society Swan": "https://www.opentable.com/r/society-swan-reservations-scottsdale?dateTime=2026-03-14T18:30&covers=2",
    "Cleaverman": "https://www.opentable.com/r/cleaverman-scottsdale?dateTime=2026-03-14T18:30&covers=2",
    "Hainoo": "https://www.opentable.com/r/hai-noon-reservations-scottsdale?dateTime=2026-03-14T18:30&covers=2",
    "Chico Malo": "https://www.opentable.com/r/chico-malo-phoenix?dateTime=2026-03-14T18:30&covers=2",
    "Mowry and Cotton": "https://www.opentable.com/r/mowry-and-cotton-scottsdale?dateTime=2026-03-14T18:30&covers=2",
    
    # Resy
    "Maple & Ash": "https://resy.com/cities/phoenix-az/venues/maple-and-ash-scottsdale?date=2026-03-14&seats=2",
    "Catch": "https://resy.com/cities/phoenix-az/venues/catch-scottsdale?date=2026-03-14&seats=2",
    "Nobu": "https://resy.com/cities/phoenix-az/venues/nobu-scottsdale?date=2026-03-14&seats=2",
    "Jing": "https://resy.com/cities/phoenix-az/venues/jing-scottsdale?date=2026-03-14&seats=2",
    "Sexy Roman": "https://resy.com/cities/phoenix-az/venues/the-sexy-roman-scottsdale?date=2026-03-14&seats=2",
    "Shiv Supper Club": "https://resy.com/cities/phoenix-az/venues/shiv-supper-club?date=2026-03-14&seats=2",
    "Kid Sister": "https://resy.com/cities/phoenix-az/venues/kid-sister?date=2026-03-14&seats=2",
}

print("=" * 70)
print("QUICK AVAILABILITY CHECK")
print("=" * 70)
print("\nWill open booking pages in your browser.")
print("Check availability for Friday 3/14 and Saturday 3/15 between 6:30-7:30pm")
print("\nPress Enter to continue, or Ctrl+C to cancel...")
input()

# Group by platform for efficiency
opentable = [name for name in BOOKING_URLS if "opentable" in BOOKING_URLS[name]]
resy = [name for name in BOOKING_URLS if "resy" in BOOKING_URLS[name]]

print("\n📋 Opening OpenTable restaurants...")
for i, name in enumerate(opentable, 1):
    print(f"  {i}. {name}")
    webbrowser.open(BOOKING_URLS[name])
    if i < len(opentable):
        time.sleep(2)  # Stagger opens

print("\n📋 Opening Resy restaurants...")
for i, name in enumerate(resy, 1):
    print(f"  {i}. {name}")
    webbrowser.open(BOOKING_URLS[name])
    if i < len(resy):
        time.sleep(2)

print("\n" + "=" * 70)
print("✅ All booking pages opened!")
print("\nManually check each tab and note which have availability.")
print("=" * 70)
