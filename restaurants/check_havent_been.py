#!/usr/bin/env python3
"""
Check ONLY "Haven't Been Yet" restaurants in priority order.
"""
import json
import time
import os
from playwright.sync_api import sync_playwright
from pathlib import Path

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
DATES = ["2026-03-14", "2026-03-15"]  # This Friday/Saturday
PARTY_SIZE = 2
PRIORITY_FILE = Path(__file__).parent / "restaurant-priority.json"

def load_havent_been_restaurants():
    """Load ONLY 'Haven't Been Yet' restaurants from priority file."""
    with open(PRIORITY_FILE) as f:
        data = json.load(f)
    
    restaurants = []
    for item in data['priority_list']:
        if item.get('section') == 'haventBeenYet':
            restaurants.append((item['name'], item['platform'], item['url']))
    
    return restaurants

def extract_times(page):
    """Extract times from ANY element."""
    try:
        page.wait_for_timeout(10000)
        
        times = page.evaluate("""() => {
            const times = new Set();
            const timePattern = /\\b(\\d{1,2}:\\d{2}\\s*[AP]M)\\b/i;
            
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                const text = el.textContent.trim();
                if (text.length < 50) {
                    const match = text.match(timePattern);
                    if (match) {
                        if (el.tagName.toLowerCase() !== 'option' && 
                            el.tagName.toLowerCase() !== 'select') {
                            times.add(match[1]);
                        }
                    }
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        # Filter to 5-9pm
        dinner_times = []
        for t in times:
            hour = int(t.split(':')[0])
            if 'PM' in t.upper():
                if hour >= 5 and hour <= 9:
                    dinner_times.append(t)
        
        return sorted(set(dinner_times))
        
    except:
        return []

def check_restaurant(page, platform, url, date):
    """Check one restaurant for one date."""
    if platform == "resy":
        full_url = f"{url}?date={date}&seats={PARTY_SIZE}"
    else:  # opentable
        full_url = f"{url}?dateTime={date}T18:30&covers={PARTY_SIZE}"
    
    try:
        page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
        return extract_times(page)
    except:
        return []

def main():
    """Check Haven't Been Yet restaurants."""
    if not os.path.exists(AUTOMATION_PROFILE):
        print("❌ Run: bash restaurants/setup_automation.sh")
        return []
    
    print("🔍 Checking 'Haven't Been Yet' restaurants")
    print(f"   Dates: Friday {DATES[0]} & Saturday {DATES[1]}")
    print(f"   Time: 5-9pm | Stopping after 5\n")
    
    restaurants = load_havent_been_restaurants()
    print(f"📋 Loaded {len(restaurants)} 'Haven't Been Yet' restaurants\n")
    
    results = []
    found_count = 0
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=AUTOMATION_PROFILE,
                headless=False,  # OpenTable blocks headless browsers!
                channel="chrome",
                viewport={'width': 1400, 'height': 1000}
            )
            
            page = browser.new_page()
            
            for name, platform, url in restaurants:
                if found_count >= 5:
                    break
                
                print(f"  {name}...", end=" ", flush=True)
                
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
                else:
                    print("❌")
            
            browser.close()
    
    except Exception as e:
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
    
    print(f"\n{'='*60}")
    print(f"✅ Found {len(results)} restaurants with availability")
    print(f"{'='*60}\n")
    
    return results

if __name__ == "__main__":
    main()
