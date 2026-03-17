#!/usr/bin/env python3
"""
WORKING availability checker - extracts from DIVs not buttons!
"""
import json
import time
import sys
import os
from playwright.sync_api import sync_playwright
from pathlib import Path

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
DATES = ["2026-03-14", "2026-03-15"]  # This Friday/Saturday
PARTY_SIZE = 2
PRIORITY_FILE = Path(__file__).parent / "restaurant-priority.json"

def load_restaurants():
    """Load from priority file."""
    if PRIORITY_FILE.exists():
        try:
            with open(PRIORITY_FILE) as f:
                data = json.load(f)
            restaurants = []
            for item in data['priority_list']:
                restaurants.append((item['name'], item['platform'], item['url']))
            return restaurants
        except:
            pass
    return []

def extract_times(page):
    """Extract times from ANY element (divs, buttons, etc)."""
    try:
        # Wait for page load
        page.wait_for_timeout(10000)
        
        # Extract times from ALL elements
        times = page.evaluate("""() => {
            const times = new Set();
            const timePattern = /\\b(\\d{1,2}:\\d{2}\\s*[AP]M)\\b/i;
            
            // Check all elements
            const allElements = document.querySelectorAll('*');
            allElements.forEach(el => {
                const text = el.textContent.trim();
                // Only consider elements with short text (likely time slots, not paragraphs)
                if (text.length < 50) {
                    const match = text.match(timePattern);
                    if (match) {
                        // Avoid dropdown options - check if parent is a select
                        if (el.tagName.toLowerCase() !== 'option' && 
                            el.tagName.toLowerCase() !== 'select') {
                            times.add(match[1]);
                        }
                    }
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        # Filter to dinner window (5-9pm)
        dinner_times = []
        for t in times:
            hour = int(t.split(':')[0])
            if 'PM' in t.upper():
                if hour >= 5 and hour <= 9:
                    dinner_times.append(t)
            elif hour == 12:  # noon
                dinner_times.append(t)
        
        return sorted(set(dinner_times))
        
    except Exception as e:
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

def main(target_count=5):
    """Check restaurants."""
    if not os.path.exists(AUTOMATION_PROFILE):
        print("❌ Run: bash restaurants/setup_automation.sh")
        return []
    
    print(f"🔍 Checking availability for {DATES[0]} & {DATES[1]}")
    print(f"   Time window: 5-9pm\n")
    
    restaurants = load_restaurants()
    if not restaurants:
        print("❌ No restaurants in priority file")
        return []
    
    results = []
    found_count = 0
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=AUTOMATION_PROFILE,
                headless=True,
                channel="chrome",
                viewport={'width': 1400, 'height': 1000}
            )
            
            page = browser.new_page()
            
            for name, platform, url in restaurants:
                if found_count >= target_count:
                    break
                
                print(f"  {name}...", end=" ", flush=True)
                
                day1 = check_restaurant(page, platform, url, DATES[0])
                time.sleep(2)
                day2 = check_restaurant(page, platform, url, DATES[1])
                time.sleep(2)
                
                if day1 or day2:
                    found_count += 1
                    results.append({
                        "name": name,
                        "platform": platform,
                        "url": url,
                        "friday": day1,
                        "saturday": day2
                    })
                    print(f"✅ #{found_count}")
                    if day1:
                        print(f"     {DATES[0]}: {', '.join(day1[:5])}")
                    if day2:
                        print(f"     {DATES[1]}: {', '.join(day2[:5])}")
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
    print(f"✅ Found {len(results)} restaurants")
    print(f"{'='*60}\n")
    
    for r in results:
        print(f"\n{r['name']} - {r['platform']}")
        print(f"{r['url']}")
        if r['friday']:
            print(f"  {DATES[0]}: {', '.join(r['friday'])}")
        if r['saturday']:
            print(f"  {DATES[1]}: {', '.join(r['saturday'])}")
    
    return results

if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(target_count=target)
