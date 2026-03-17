#!/usr/bin/env python3
"""
Weekly restaurant availability check for FOLLOWING weekend (12-13 days out).
Time window: 6:30-7:30 PM
Checks: Haven't Been Yet → Already Been (priority order)
"""
import json
import time
import os
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
from pathlib import Path

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
PARTY_SIZE = 2
PRIORITY_FILE = Path(__file__).parent / "restaurant-priority.json"

def get_following_weekend():
    """Get Friday/Saturday 12-13 days from today."""
    today = datetime.now()
    days_until_friday = (4 - today.weekday()) % 7  # 0=Mon, 4=Fri
    if days_until_friday < 12:
        days_until_friday += 7  # Skip to following week
    
    friday = today + timedelta(days=days_until_friday + 7)  # Following Friday
    saturday = friday + timedelta(days=1)
    
    return [
        friday.strftime("%Y-%m-%d"),
        saturday.strftime("%Y-%m-%d")
    ]

def load_priority_restaurants():
    """Load restaurants in priority order: Haven't Been Yet → Already Been."""
    with open(PRIORITY_FILE) as f:
        data = json.load(f)
    
    restaurants = []
    
    # First: Haven't Been Yet
    for item in data['priority_list']:
        if item.get('section') == 'haventBeenYet':
            restaurants.append((item['name'], item['platform'], item['url'], 'New'))
    
    # Then: Already Been (Would Return)
    for item in data['priority_list']:
        if item.get('section') == 'wouldReturn':
            restaurants.append((item['name'], item['platform'], item['url'], 'Return'))
    
    return restaurants

def extract_times(page):
    """Extract times from page elements."""
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
                    if (match && el.tagName.toLowerCase() !== 'option' && 
                        el.tagName.toLowerCase() !== 'select') {
                        times.add(match[1]);
                    }
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        # Filter to 6:30-7:30 PM ONLY
        target_times = []
        for t in times:
            t_upper = t.upper()
            if 'PM' in t_upper:
                # Parse time
                parts = t.split(':')
                hour = int(parts[0])
                minute = int(parts[1].split()[0])
                
                # 6:30, 6:45, 7:00, 7:15, 7:30
                if (hour == 6 and minute >= 30) or (hour == 7 and minute <= 30):
                    target_times.append(t)
        
        return sorted(set(target_times))
        
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

def generate_booking_link(platform, url, date, time_slot):
    """Generate direct booking link with all details filled."""
    if platform == "resy":
        # Resy format: ?date=2026-03-21&seats=2
        return f"{url}?date={date}&seats={PARTY_SIZE}"
    else:
        # OpenTable format: ?dateTime=2026-03-21T19:15&covers=2
        # Convert time like "7:15 PM" to "19:15"
        time_parts = time_slot.replace(" PM", "").replace(" AM", "").split(":")
        hour = int(time_parts[0])
        minute = time_parts[1]
        if "PM" in time_slot.upper() and hour != 12:
            hour += 12
        time_24 = f"{hour:02d}:{minute}"
        return f"{url}?dateTime={date}T{time_24}&covers={PARTY_SIZE}"

def main():
    """Weekly availability check."""
    if not os.path.exists(AUTOMATION_PROFILE):
        return {"error": "Automation profile not set up"}
    
    dates = get_following_weekend()
    friday_formatted = datetime.strptime(dates[0], "%Y-%m-%d").strftime("%A %b %d")
    saturday_formatted = datetime.strptime(dates[1], "%Y-%m-%d").strftime("%A %b %d")
    
    print(f"🔍 Weekly Restaurant Check")
    print(f"   {friday_formatted} & {saturday_formatted}")
    print(f"   Time: 6:30-7:30 PM\n")
    
    restaurants = load_priority_restaurants()
    print(f"📋 Checking {len(restaurants)} restaurants in priority order\n")
    
    results = []
    found_count = 0
    target_count = 5
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=AUTOMATION_PROFILE,
                headless=False,
                channel="chrome",
                viewport={'width': 1400, 'height': 1000}
            )
            
            page = browser.new_page()
            
            for name, platform, url, category in restaurants:
                if found_count >= target_count:
                    break
                
                print(f"  {name} ({category})...", end=" ", flush=True)
                
                friday = check_restaurant(page, platform, url, dates[0])
                time.sleep(2)
                saturday = check_restaurant(page, platform, url, dates[1])
                time.sleep(2)
                
                if friday or saturday:
                    found_count += 1
                    
                    # Generate booking links
                    friday_links = []
                    if friday:
                        for t in friday[:3]:  # Top 3 times
                            friday_links.append({
                                "time": t,
                                "link": generate_booking_link(platform, url, dates[0], t)
                            })
                    
                    saturday_links = []
                    if saturday:
                        for t in saturday[:3]:
                            saturday_links.append({
                                "time": t,
                                "link": generate_booking_link(platform, url, dates[1], t)
                            })
                    
                    results.append({
                        "name": name,
                        "platform": platform,
                        "url": url,
                        "category": category,
                        "friday_date": dates[0],
                        "saturday_date": dates[1],
                        "friday_times": friday,
                        "saturday_times": saturday,
                        "friday_links": friday_links,
                        "saturday_links": saturday_links
                    })
                    print(f"✅ #{found_count}")
                else:
                    print("❌")
            
            browser.close()
    
    except Exception as e:
        return {"error": str(e)}
    
    # Save results
    output = {
        "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "friday": dates[0],
        "saturday": dates[1],
        "party_size": PARTY_SIZE,
        "found_count": len(results),
        "restaurants": results
    }
    
    with open('restaurants/weekly_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    return output

if __name__ == "__main__":
    results = main()
    
    if "error" in results:
        print(f"\n❌ Error: {results['error']}")
    else:
        print(f"\n{'='*60}")
        print(f"✅ Found {results['found_count']} restaurants")
        print(f"{'='*60}\n")
        
        for r in results['restaurants']:
            print(f"\n{r['name']} ({r['category']})")
            print(f"{r['url']}")
            
            if r['friday_links']:
                print(f"\n  {results['friday']}:")
                for link in r['friday_links']:
                    print(f"    {link['time']}: {link['link']}")
            
            if r['saturday_links']:
                print(f"\n  {results['saturday']}:")
                for link in r['saturday_links']:
                    print(f"    {link['time']}: {link['link']}")
