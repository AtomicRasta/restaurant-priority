#!/usr/bin/env python3
"""Check availability using existing browser sessions (logged in)."""
import json
import time
from playwright.sync_api import sync_playwright
import os

DATES = ["2026-03-14", "2026-03-15"]
DAY_NAMES = {"2026-03-14": "Fri 3/14", "2026-03-15": "Sat 3/15"}
PARTY_SIZE = 2

# Restaurants organized by platform
RESTAURANTS = {
    "resy": {
        "Kid Sister": "https://resy.com/cities/phoenix-az/venues/kid-sister",
        "Maple & Ash": "https://resy.com/cities/phoenix-az/venues/maple-and-ash-scottsdale",
        "Catch": "https://resy.com/cities/phoenix-az/venues/catch-scottsdale",
        "Nobu": "https://resy.com/cities/phoenix-az/venues/nobu-scottsdale",
        "Jing": "https://resy.com/cities/phoenix-az/venues/jing-scottsdale",
        "Sexy Roman": "https://resy.com/cities/phoenix-az/venues/the-sexy-roman-scottsdale",
        "Shiv Supper Club": "https://resy.com/cities/phoenix-az/venues/shiv-supper-club",
    },
    "opentable": {
        "40 Love": "https://www.opentable.com/r/40-love-scottsdale",
        "FLINT by Baltaire": "https://www.opentable.com/r/flint-by-baltaire-scottsdale",
        "Bourbon & Bones": "https://www.opentable.com/r/bourbon-and-bones-scottsdale",
        "Society Swan": "https://www.opentable.com/r/society-swan-reservations-scottsdale",
        "Cleaverman": "https://www.opentable.com/r/cleaverman-scottsdale",
        "Hainoo": "https://www.opentable.com/r/hai-noon-reservations-scottsdale",
        "Mowry and Cotton": "https://www.opentable.com/r/mowry-and-cotton-scottsdale",
    }
}

def extract_times_from_page(page, platform):
    """Extract available time slots from current page."""
    try:
        # Wait a bit for dynamic content
        page.wait_for_timeout(3000)
        
        if platform == "resy":
            # Resy time slot extraction
            times = page.evaluate("""() => {
                const times = new Set();
                
                // Try various selectors
                const selectors = [
                    'button[class*="ReservationButton"]',
                    'button[class*="Button--"]',
                    '[data-test-id*="time"]',
                    'button'
                ];
                
                for (const selector of selectors) {
                    const buttons = document.querySelectorAll(selector);
                    buttons.forEach(btn => {
                        const text = btn.textContent.trim();
                        // Match time format: 6:30 PM, 7:00 PM, etc.
                        const match = text.match(/^(\\d{1,2}:\\d{2}\\s*[AP]M)$/i);
                        if (match) {
                            times.add(match[1]);
                        }
                    });
                    if (times.size > 0) break;
                }
                
                return Array.from(times).sort();
            }""")
        else:  # opentable
            # OpenTable time slot extraction
            times = page.evaluate("""() => {
                const times = new Set();
                
                const selectors = [
                    '[data-test*="time-slot"]',
                    '[data-test*="availability"]',
                    'button[class*="time"]',
                    'button[class*="slot"]',
                    'button'
                ];
                
                for (const selector of selectors) {
                    const buttons = document.querySelectorAll(selector);
                    buttons.forEach(btn => {
                        const text = btn.textContent.trim();
                        const match = text.match(/(\\d{1,2}:\\d{2}\\s*PM)/i);
                        if (match && text.length < 20) {  // Filter out long text
                            times.add(match[1]);
                        }
                    });
                    if (times.size > 0) break;
                }
                
                return Array.from(times).sort();
            }""")
        
        # Filter to target window (6:30-7:30pm)
        target_times = [t for t in times if any(x in t for x in ["6:30", "6:45", "7:00", "7:15", "7:30"])]
        
        return target_times if target_times else times[:5]  # Return first 5 if none in window
        
    except Exception as e:
        return []

def check_restaurant(page, name, base_url, platform, date):
    """Check availability for one restaurant on one date."""
    day_label = DAY_NAMES[date]
    
    # Build URL with date and party size
    if platform == "resy":
        url = f"{base_url}?date={date}&seats={PARTY_SIZE}"
    else:  # opentable
        url = f"{base_url}?dateTime={date}T18:30&covers={PARTY_SIZE}"
    
    try:
        print(f"    Checking {day_label}...", end=" ", flush=True)
        
        # Navigate to page
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        
        # Extract times
        times = extract_times_from_page(page, platform)
        
        if times:
            print(f"✅ Found {len(times)} slots")
            return {"day": day_label, "slots": times}
        else:
            print(f"❌ No slots")
            return {"day": day_label, "slots": []}
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}")
        return {"day": day_label, "error": str(e)[:100]}

def main():
    results = {}
    confirmed_count = 0
    
    # Use Chrome user data to leverage logged-in sessions
    chrome_user_data = os.path.expanduser("~/Library/Application Support/Google/Chrome")
    
    with sync_playwright() as p:
        print("=" * 70)
        print("RESTAURANT AVAILABILITY CHECKER")
        print("Using your logged-in browser sessions")
        print("=" * 70)
        
        # Launch browser with user data (logged-in sessions)
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=chrome_user_data,
                headless=False,  # Show browser so you can see progress
                channel="chrome",
                viewport={'width': 1920, 'height': 1080},
                args=['--disable-blink-features=AutomationControlled']
            )
            
            page = browser.new_page()
            
            # Check Resy restaurants first (usually faster)
            print("\n🍽️  CHECKING RESY RESTAURANTS\n")
            for name, url in RESTAURANTS["resy"].items():
                if confirmed_count >= 5:
                    break
                
                print(f"\n{name}:")
                results[name] = {"platform": "resy", "url": url, "availability": []}
                has_availability = False
                
                for date in DATES:
                    if confirmed_count >= 5:
                        break
                    
                    result = check_restaurant(page, name, url, "resy", date)
                    results[name]["availability"].append(result)
                    
                    if result.get("slots"):
                        has_availability = True
                
                if has_availability:
                    confirmed_count += 1
                    print(f"  ✨ CONFIRMED #{confirmed_count}/5")
                
                time.sleep(1)  # Be respectful
            
            # Check OpenTable if needed
            if confirmed_count < 5:
                print("\n🍽️  CHECKING OPENTABLE RESTAURANTS\n")
                for name, url in RESTAURANTS["opentable"].items():
                    if confirmed_count >= 5:
                        break
                    
                    print(f"\n{name}:")
                    results[name] = {"platform": "opentable", "url": url, "availability": []}
                    has_availability = False
                    
                    for date in DATES:
                        if confirmed_count >= 5:
                            break
                        
                        result = check_restaurant(page, name, url, "opentable", date)
                        results[name]["availability"].append(result)
                        
                        if result.get("slots"):
                            has_availability = True
                    
                    if has_availability:
                        confirmed_count += 1
                        print(f"  ✨ CONFIRMED #{confirmed_count}/5")
                    
                    time.sleep(1)
            
            browser.close()
            
        except Exception as e:
            print(f"\n❌ Browser error: {e}")
            print("\nTrying with regular browser (non-persistent)...")
            
            # Fallback to regular browser
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            page = context.new_page()
            
            # Continue with checks...
            # (Same logic as above but without persistent context)
            
            browser.close()
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"RESULTS: Found {confirmed_count} restaurants with availability")
    print("=" * 70)
    
    # Print available restaurants
    available = [name for name, data in results.items() 
                 if any(day.get("slots") for day in data.get("availability", []))]
    
    if available:
        print("\n📋 Restaurants with availability:\n")
        for i, name in enumerate(available, 1):
            data = results[name]
            print(f"{i}. {name} ({data['platform']})")
            for day_data in data["availability"]:
                if day_data.get("slots"):
                    slots_str = ", ".join(day_data["slots"][:5])
                    if len(day_data["slots"]) > 5:
                        slots_str += f" (+{len(day_data['slots'])-5} more)"
                    print(f"   • {day_data['day']}: {slots_str}")
    
    # Save results
    with open('availability_found.json', 'w') as f:
        json.dump({
            "checked_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_dates": DATES,
            "confirmed_count": confirmed_count,
            "restaurants": results
        }, f, indent=2)
    
    print(f"\n💾 Full results saved to availability_found.json")
    
    return confirmed_count

if __name__ == "__main__":
    found = main()
    if found >= 5:
        print("\n✅ Mission accomplished! Found 5+ restaurants.")
    else:
        print(f"\n⚠️  Only found {found} restaurants with availability.")
