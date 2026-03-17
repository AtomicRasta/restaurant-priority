#!/usr/bin/env python3
"""
Check availability using Chrome DevTools Protocol.
This connects to your existing Chrome browser instead of launching a new one.
"""
import json
import time
from playwright.sync_api import sync_playwright

DATES = ["2026-03-14", "2026-03-15"]
PARTY_SIZE = 2

RESTAURANTS = [
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
]

def extract_times(page, platform):
    """Extract time slots from page."""
    try:
        page.wait_for_timeout(4000)
        
        times = page.evaluate("""() => {
            const times = new Set();
            const buttons = document.querySelectorAll('button');
            
            buttons.forEach(btn => {
                const text = btn.textContent.trim();
                const match = text.match(/(\\d{1,2}:\\d{2}\\s*[AP]M)/i);
                if (match && text.length < 30) {
                    times.add(match[1]);
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        # Filter to dinner window
        dinner_times = [t for t in times if any(h in t for h in ["6:", "7:"])]
        return dinner_times
        
    except Exception as e:
        return []

def check_restaurant(page, name, platform, base_url, date):
    """Check availability for one restaurant/date."""
    if platform == "resy":
        url = f"{base_url}?date={date}&seats={PARTY_SIZE}"
    else:
        url = f"{base_url}?dateTime={date}T18:30&covers={PARTY_SIZE}"
    
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        return extract_times(page, platform)
    except:
        return []

def main():
    print("=" * 70)
    print("AUTOMATED RESTAURANT AVAILABILITY CHECKER")
    print("=" * 70)
    print(f"\nTarget: Friday 3/14 & Saturday 3/15, {PARTY_SIZE} people, 6-8pm")
    print("Connecting to Chrome...\n")
    
    results = []
    found_count = 0
    
    try:
        with sync_playwright() as p:
            # Connect to existing Chrome via CDP
            # First, launch Chrome with remote debugging:
            # /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
            
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]  # Use existing context
            page = context.new_page()
            
            for name, platform, url in RESTAURANTS:
                if found_count >= 5:
                    print(f"\n✅ Found 5! Stopping.")
                    break
                
                print(f"\n{len(results)+1}. {name} ({platform})")
                
                friday = check_restaurant(page, name, platform, url, "2026-03-14")
                print(f"   Fri: {'✅ ' + ', '.join(friday[:4]) if friday else '❌ None'}")
                time.sleep(1)
                
                saturday = check_restaurant(page, name, platform, url, "2026-03-15")
                print(f"   Sat: {'✅ ' + ', '.join(saturday[:4]) if saturday else '❌ None'}")
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
                    print(f"   🎉 #{found_count}/5")
            
            browser.close()
    
    except Exception as e:
        print(f"\n❌ Connection failed: {e}")
        print("\nTo use this method, start Chrome with remote debugging:")
        print('  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/Library/Application Support/Google/Chrome"')
        return []
    
    # Save results
    with open('restaurants/availability_found.json', 'w') as f:
        json.dump({
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "found_count": len(results),
            "restaurants": results
        }, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"Found {len(results)} restaurants")
    print(f"{'='*70}\n")
    
    for r in results:
        print(f"• {r['name']}")
        if r['friday']:
            print(f"  Fri: {', '.join(r['friday'])}")
        if r['saturday']:
            print(f"  Sat: {', '.join(r['saturday'])}")
        print()
    
    return results

if __name__ == "__main__":
    main()
