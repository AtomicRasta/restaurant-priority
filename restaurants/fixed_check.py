#!/usr/bin/env python3
"""
Fixed availability checker - waits for actual time slot buttons to load.
"""
import json
import time
from playwright.sync_api import sync_playwright
import os
from pathlib import Path

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
DATES = ["2026-03-21", "2026-03-22"]
PARTY_SIZE = 2
PRIORITY_FILE = Path(__file__).parent / "restaurant-priority.json"

DEFAULT_RESTAURANTS = [
    ("Kid Sister", "resy", "https://resy.com/cities/phoenix-az/venues/kid-sister"),
    ("Maple & Ash", "resy", "https://resy.com/cities/phoenix-az/venues/maple-and-ash-scottsdale"),
]

def load_restaurants():
    """Load from priority file or use default."""
    if PRIORITY_FILE.exists():
        try:
            with open(PRIORITY_FILE) as f:
                data = json.load(f)
            restaurants = []
            for item in data['priority_list']:
                restaurants.append((item['name'], item['platform'], item['url']))
            print(f"📋 Loaded {len(restaurants)} restaurants from priority file")
            return restaurants
        except:
            pass
    return DEFAULT_RESTAURANTS

def extract_times_resy(page):
    """Extract time slots from Resy page."""
    try:
        # Wait for page to fully load
        page.wait_for_timeout(8000)  # Resy loads times dynamically
        
        times = page.evaluate("""() => {
            const times = new Set();
            
            // Look for Resy booking buttons
            const bookButtons = document.querySelectorAll('button[data-test-id*="book"], .Button--venue-booking');
            bookButtons.forEach(btn => {
                const text = btn.textContent.trim();
                // Match times like "5:00 PM", "6:30 PM"
                const match = text.match(/(\\d{1,2}:\\d{2}\\s*[AP]M)/);
                if (match) {
                    times.add(match[1]);
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        # Filter to 5-9pm
        dinner_times = [t for t in times if any(h in t for h in ["5:", "6:", "7:", "8:"])]
        return dinner_times
        
    except Exception as e:
        print(f"   Error: {e}")
        return []

def extract_times_opentable(page):
    """Extract time slots from OpenTable page."""
    try:
        # Wait for page to fully load
        page.wait_for_timeout(8000)  # OpenTable also loads dynamically
        
        times = page.evaluate("""() => {
            const times = new Set();
            
            // OpenTable uses different selectors
            const timeButtons = document.querySelectorAll('button[data-test-id*="time"], .time-slot-button, button[type="button"]');
            timeButtons.forEach(btn => {
                const text = btn.textContent.trim();
                const match = text.match(/(\\d{1,2}:\\d{2}\\s*[AP]M)/);
                if (match && text.length < 20) {
                    times.add(match[1]);
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        dinner_times = [t for t in times if any(h in t for h in ["5:", "6:", "7:", "8:"])]
        return dinner_times
        
    except Exception as e:
        print(f"   Error: {e}")
        return []

def check_restaurant(page, platform, url, date):
    """Check one restaurant for one date."""
    if platform == "resy":
        full_url = f"{url}?date={date}&seats={PARTY_SIZE}"
        page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
        return extract_times_resy(page)
    else:  # opentable
        full_url = f"{url}?dateTime={date}T18:30&covers={PARTY_SIZE}"
        page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
        return extract_times_opentable(page)

def main(target_count=5):
    """Check restaurants for availability."""
    if not os.path.exists(AUTOMATION_PROFILE):
        print("❌ Automation profile not found!")
        print(f"Run: bash restaurants/setup_automation.sh")
        return []
    
    print("🔍 Checking restaurant availability...")
    print(f"   Dates: {', '.join(DATES)}")
    print(f"   Time window: 5-9pm")
    print(f"   Stopping after {target_count} with availability\\n")
    
    restaurants = load_restaurants()
    
    results = []
    found_count = 0
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=AUTOMATION_PROFILE,
                headless=False,  # Show browser for debugging
                channel="chrome",
                viewport={'width': 1400, 'height': 1000}
            )
            
            page = browser.new_page()
            
            for name, platform, url in restaurants:
                if found_count >= target_count:
                    break
                
                print(f"  Checking {name}...", end=" ", flush=True)
                
                friday = check_restaurant(page, platform, url, DATES[0])
                time.sleep(2)
                saturday = check_restaurant(page, platform, url, DATES[1])
                time.sleep(2)
                
                if friday or saturday:
                    found_count += 1
                    results.append({
                        "name": name,
                        "platform": platform,
                        "url": url,
                        "friday": friday,
                        "saturday": saturday
                    })
                    print(f"✅ #{found_count}")
                    print(f"     Fri: {', '.join(friday[:5]) if friday else 'None'}")
                    print(f"     Sat: {', '.join(saturday[:5]) if saturday else 'None'}")
                else:
                    print("❌")
            
            browser.close()
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
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
    
    print(f"\n{'='*60}")
    print(f"✅ Found {len(results)} restaurants with availability")
    print(f"{'='*60}\n")
    
    return results

if __name__ == "__main__":
    main(target_count=5)
