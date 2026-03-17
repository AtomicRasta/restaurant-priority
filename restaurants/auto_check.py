#!/usr/bin/env python3
"""
Fully automated availability checker using dedicated Chrome profile.
This runs headless and uses your logged-in sessions.
Reads priority order from restaurant-priority.json if available.
"""
import json
import time
import sys
from playwright.sync_api import sync_playwright
import os
from pathlib import Path

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
DATES = ["2026-03-21", "2026-03-22"]
PARTY_SIZE = 2
PRIORITY_FILE = Path(__file__).parent / "restaurant-priority.json"

# Default list (used if priority file doesn't exist)
DEFAULT_RESTAURANTS = [
    # Haven't Been Yet
    ("Kid Sister", "resy", "https://resy.com/cities/phoenix-az/venues/kid-sister"),
    ("Maple & Ash", "resy", "https://resy.com/cities/phoenix-az/venues/maple-and-ash-scottsdale"),
    ("Catch", "resy", "https://resy.com/cities/phoenix-az/venues/catch-scottsdale"),
    ("Nobu", "resy", "https://resy.com/cities/phoenix-az/venues/nobu-scottsdale"),
    ("Jing", "resy", "https://resy.com/cities/phoenix-az/venues/jing-scottsdale"),
    ("Sexy Roman", "resy", "https://resy.com/cities/phoenix-az/venues/the-sexy-roman-scottsdale"),
    ("Shiv Supper Club", "resy", "https://resy.com/cities/phoenix-az/venues/shiv-supper-club"),
    ("40 Love", "opentable", "https://www.opentable.com/r/40-love-scottsdale"),
    ("FLINT by Baltaire", "opentable", "https://www.opentable.com/r/flint-by-baltaire-scottsdale"),
    ("Bourbon & Bones", "opentable", "https://www.opentable.com/r/bourbon-and-bones-scottsdale"),
    ("Society Swan", "opentable", "https://www.opentable.com/r/society-swan-reservations-scottsdale"),
    ("Cleaverman", "opentable", "https://www.opentable.com/r/cleaverman-scottsdale"),
    ("Hainoo", "opentable", "https://www.opentable.com/r/hai-noon-reservations-scottsdale"),
    ("Mowry and Cotton", "opentable", "https://www.opentable.com/r/mowry-and-cotton-scottsdale"),
    
    # Would Return (Already Been)
    ("Buck and Rider", "opentable", "https://www.opentable.com/r/buck-and-rider-scottsdale"),
    ("Uchi", "resy", "https://resy.com/cities/phoenix-az/venues/uchi"),
    ("Pizzeria Bianco", "resy", "https://resy.com/cities/phoenix-az/venues/pizzeria-bianco"),
    ("FnB", "resy", "https://resy.com/cities/phoenix-az/venues/fnb"),
    ("Bacanora", "resy", "https://resy.com/cities/phoenix-az/venues/bacanora"),
    ("Tratto", "resy", "https://resy.com/cities/phoenix-az/venues/tratto"),
    ("Elephante", "resy", "https://resy.com/cities/phoenix-az/venues/elephante"),
    ("Pinyon", "resy", "https://resy.com/cities/phoenix-az/venues/pinyon"),
    ("Valentine", "resy", "https://resy.com/cities/phoenix-az/venues/valentine"),
    ("The Ends", "resy", "https://resy.com/cities/phoenix-az/venues/the-ends"),
    ("Vecina", "resy", "https://resy.com/cities/phoenix-az/venues/vecina"),
    ("Huarachis", "resy", "https://resy.com/cities/phoenix-az/venues/huarachis"),
]

def load_restaurants():
    """
    Load restaurants from priority file if it exists.
    Falls back to default list.
    Returns list of (name, platform, url) tuples.
    """
    if PRIORITY_FILE.exists():
        try:
            with open(PRIORITY_FILE) as f:
                data = json.load(f)
            
            # Use priority_list from the file
            restaurants = []
            for item in data['priority_list']:
                restaurants.append((
                    item['name'],
                    item['platform'],
                    item['url']
                ))
            
            print(f"📋 Loaded {len(restaurants)} restaurants from priority file")
            return restaurants
        except Exception as e:
            print(f"⚠️  Failed to load priority file: {e}")
            print("   Using default order instead")
    
    return DEFAULT_RESTAURANTS

def extract_times(page):
    """Extract time slots from page."""
    try:
        page.wait_for_timeout(4000)
        
        times = page.evaluate("""() => {
            const times = new Set();
            const buttons = document.querySelectorAll('button');
            
            buttons.forEach(btn => {
                const text = btn.textContent.trim();
                // Match time format: "6:30 PM" (with optional text after)
                const match = text.match(/(\\d{1,2}:\\d{2}\\s*[AP]M)/i);
                if (match && text.length < 30) {
                    times.add(match[1]);
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        # Filter to 5pm-9pm window (expanded for better availability)
        dinner_times = [t for t in times if any(h in t for h in ["5:", "6:", "7:", "8:"])]
        return dinner_times
        
    except:
        return []

def check_restaurant(page, platform, url, date):
    """Check one restaurant for one date."""
    if platform == "resy":
        full_url = f"{url}?date={date}&seats={PARTY_SIZE}"
    else:
        full_url = f"{url}?dateTime={date}T18:30&covers={PARTY_SIZE}"
    
    try:
        page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
        return extract_times(page)
    except:
        return []

def main(target_count=5, verbose=True):
    """
    Check restaurants for availability.
    
    Args:
        target_count: Stop after finding this many restaurants
        verbose: Print progress (False for cron jobs)
    """
    if not os.path.exists(AUTOMATION_PROFILE):
        print("❌ Automation profile not found!")
        print(f"Run: bash restaurants/setup_automation.sh")
        return []
    
    if verbose:
        print("🔍 Checking restaurant availability...")
    
    # Load restaurant list (from priority file or default)
    restaurants = load_restaurants()
    if verbose and PRIORITY_FILE.exists():
        print(f"   Using custom priority order")
    
    results = []
    found_count = 0
    
    try:
        with sync_playwright() as p:
            # Launch with automation profile
            browser = p.chromium.launch_persistent_context(
                user_data_dir=AUTOMATION_PROFILE,
                headless=True,  # Run in background
                channel="chrome",
                viewport={'width': 1400, 'height': 1000},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage'
                ]
            )
            
            page = browser.new_page()
            
            for name, platform, url in restaurants:
                if found_count >= target_count:
                    break
                
                if verbose:
                    print(f"  Checking {name}...", end=" ", flush=True)
                
                friday = check_restaurant(page, platform, url, "2026-03-14")
                time.sleep(1)
                saturday = check_restaurant(page, platform, url, "2026-03-15")
                time.sleep(1)
                
                if friday or saturday:
                    found_count += 1
                    results.append({
                        "name": name,
                        "platform": platform,
                        "url": url,
                        "friday": friday,
                        "saturday": saturday
                    })
                    if verbose:
                        print(f"✅ #{found_count}")
                else:
                    if verbose:
                        print("❌")
            
            browser.close()
    
    except Exception as e:
        if verbose:
            print(f"\n❌ Error: {e}")
        return []
    
    # Save results
    output = {
        "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "dates": DATES,
        "party_size": PARTY_SIZE,
        "found_count": len(results),
        "restaurants": results
    }
    
    with open('restaurants/availability_found.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    if verbose:
        print(f"\n✅ Found {len(results)} restaurants with availability")
        for r in results:
            print(f"\n{r['name']} ({r['platform']})")
            print(f"  {r['url']}")
            if r['friday']:
                print(f"  Fri: {', '.join(r['friday'][:5])}")
            if r['saturday']:
                print(f"  Sat: {', '.join(r['saturday'][:5])}")
    
    return results

if __name__ == "__main__":
    # Can pass target count as argument: python3 auto_check.py 3
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(target_count=target, verbose=True)
