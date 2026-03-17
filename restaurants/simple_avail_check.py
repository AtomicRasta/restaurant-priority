#!/usr/bin/env python3
"""Simple availability checker - opens pages one by one for visual checking."""
import time
from playwright.sync_api import sync_playwright

DATES = ["2026-03-14", "2026-03-15"]
PARTY_SIZE = 2

# All restaurants to check
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

def check_availability(page, name, platform, base_url, date):
    """Navigate to restaurant page and extract times."""
    # Build URL
    if platform == "resy":
        url = f"{base_url}?date={date}&seats={PARTY_SIZE}"
    else:
        url = f"{base_url}?dateTime={date}T18:30&covers={PARTY_SIZE}"
    
    try:
        print(f"  Loading {date}... ", end="", flush=True)
        page.goto(url, wait_until="domcontentloaded", timeout=15000)
        page.wait_for_timeout(3000)  # Wait for JS to render
        
        # Extract time slots
        times = page.evaluate("""() => {
            const times = new Set();
            const buttons = document.querySelectorAll('button');
            
            buttons.forEach(btn => {
                const text = btn.textContent.trim();
                // Match time patterns
                const match = text.match(/^(\\d{1,2}:\\d{2}\\s*[AP]M)$/i);
                if (match) {
                    times.add(match[1]);
                }
            });
            
            return Array.from(times).sort();
        }""")
        
        # Filter to dinner window
        dinner_times = [t for t in times if any(x in t for x in ["6:", "7:"])]
        
        if dinner_times:
            print(f"✅ {len(dinner_times)} slots")
            return dinner_times
        elif times:
            print(f"⏰ {len(times)} slots (not dinner time)")
            return []
        else:
            print(f"❌ No slots")
            return []
            
    except Exception as e:
        print(f"❌ Error")
        return []

def main():
    print("=" * 70)
    print("RESTAURANT AVAILABILITY CHECKER")
    print("=" * 70)
    print(f"\nChecking for {PARTY_SIZE} people on:")
    print(f"  • Friday 3/14")
    print(f"  • Saturday 3/15")
    print(f"\nTarget time: 6:30-7:30 PM")
    print("\nOpening browser window to check each restaurant...")
    print("="*70)
    
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, channel="chrome")
        context = browser.new_context(
            viewport={'width': 1400, 'height': 1000}
        )
        page = context.new_page()
        
        found_count = 0
        
        for name, platform, url in RESTAURANTS:
            if found_count >= 5:
                print(f"\n✅ Found 5 restaurants! Stopping here.")
                break
            
            print(f"\n{len(results)+1}. {name} ({platform}):")
            
            friday_slots = check_availability(page, name, platform, url, "2026-03-14")
            time.sleep(1)
            saturday_slots = check_availability(page, name, platform, url, "2026-03-15")
            time.sleep(1)
            
            if friday_slots or saturday_slots:
                found_count += 1
                results.append({
                    "name": name,
                    "platform": platform,
                    "url": url,
                    "friday": friday_slots,
                    "saturday": saturday_slots
                })
                print(f"   ✨ CONFIRMED #{found_count}/5")
        
        browser.close()
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"FINAL RESULTS: {len(results)} restaurants with availability")
    print("=" * 70)
    
    if results:
        print("\n📋 Available Restaurants:\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. **{r['name']}** ({r['platform']})")
            if r['friday']:
                print(f"   • Friday: {', '.join(r['friday'][:5])}")
            if r['saturday']:
                print(f"   • Saturday: {', '.join(r['saturday'][:5])}")
            print(f"   • URL: {r['url']}")
            print()
    
    # Save JSON
    import json
    with open('availability_found.json', 'w') as f:
        json.dump({
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "restaurants": results
        }, f, indent=2)
    
    print("💾 Results saved to availability_found.json")
    
    return results

if __name__ == "__main__":
    main()
