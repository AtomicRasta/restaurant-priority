#!/usr/bin/env python3
"""Smart availability checker with anti-detection."""
import json
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

DATES = ["2026-03-14", "2026-03-15"]
DAY_NAMES = {"2026-03-14": "Fri 3/14", "2026-03-15": "Sat 3/15"}
PARTY_SIZE = 2

# Restaurant URLs
RESTAURANTS = {
    # Resy (usually more permissive)
    "Kid Sister": {"platform": "resy", "url": "https://resy.com/cities/phoenix-az/venues/kid-sister"},
    "Maple & Ash": {"platform": "resy", "url": "https://resy.com/cities/phoenix-az/venues/maple-and-ash-scottsdale"},
    "Catch": {"platform": "resy", "url": "https://resy.com/cities/phoenix-az/venues/catch-scottsdale"},
    "Nobu": {"platform": "resy", "url": "https://resy.com/cities/phoenix-az/venues/nobu-scottsdale"},
    "Jing": {"platform": "resy", "url": "https://resy.com/cities/phoenix-az/venues/jing-scottsdale"},
    "Sexy Roman": {"platform": "resy", "url": "https://resy.com/cities/phoenix-az/venues/the-sexy-roman-scottsdale"},
    "Shiv Supper Club": {"platform": "resy", "url": "https://resy.com/cities/phoenix-az/venues/shiv-supper-club"},
    
    # OpenTable
    "40 Love": {"platform": "opentable", "url": "https://www.opentable.com/r/40-love-scottsdale"},
    "FLINT by Baltaire": {"platform": "opentable", "url": "https://www.opentable.com/r/flint-by-baltaire-scottsdale"},
    "Bourbon & Bones": {"platform": "opentable", "url": "https://www.opentable.com/r/bourbon-and-bones-scottsdale"},
    "Society Swan": {"platform": "opentable", "url": "https://www.opentable.com/r/society-swan-reservations-scottsdale"},
    "Cleaverman": {"platform": "opentable", "url": "https://www.opentable.com/r/cleaverman-scottsdale"},
    "Hainoo": {"platform": "opentable", "url": "https://www.opentable.com/r/hai-noon-reservations-scottsdale"},
}

def extract_resy_times(page):
    """Extract available times from Resy page."""
    try:
        # Wait for time slots to load
        page.wait_for_selector('[data-test-id*="time"], button[class*="ReservationButton"], button[class*="Button"]', timeout=10000)
        
        # Extract all time buttons
        times = page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const times = [];
            buttons.forEach(btn => {
                const text = btn.textContent.trim();
                // Match time patterns like "6:30 PM"
                const match = text.match(/^(\\d{1,2}:\\d{2}\\s*[AP]M)$/i);
                if (match) {
                    times.push(match[1]);
                }
            });
            return times;
        }""")
        
        # Filter to target window
        target = [t for t in times if any(x in t for x in ["6:30", "6:45", "7:00", "7:15", "7:30"])]
        return target if target else times[:5]  # Return first 5 if none in window
    except Exception as e:
        return []

def extract_opentable_times(page):
    """Extract available times from OpenTable page."""
    try:
        # Wait for availability section
        page.wait_for_selector('[data-test*="time"], button[class*="slot"], [class*="TimeSlot"]', timeout=10000)
        
        times = page.evaluate("""() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const times = [];
            buttons.forEach(btn => {
                const text = btn.textContent.trim();
                const match = text.match(/(\\d{1,2}:\\d{2}\\s*PM)/i);
                if (match) {
                    times.push(match[1]);
                }
            });
            return times;
        }""")
        
        target = [t for t in times if any(x in t for x in ["6:30", "6:45", "7:00", "7:15", "7:30"])]
        return target if target else times[:5]
    except Exception as e:
        return []

def check_restaurant(page, name, info, date):
    """Check a single restaurant for a specific date."""
    day_label = DAY_NAMES[date]
    platform = info["platform"]
    base_url = info["url"]
    
    # Build URL with date and party size
    if platform == "resy":
        url = f"{base_url}?date={date}&seats={PARTY_SIZE}"
    else:  # opentable
        url = f"{base_url}?dateTime={date}T18:30&covers={PARTY_SIZE}"
    
    try:
        # Navigate with random delay
        time.sleep(random.uniform(2, 4))
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        # Random human-like delay
        time.sleep(random.uniform(1.5, 3))
        
        # Extract times based on platform
        if platform == "resy":
            times = extract_resy_times(page)
        else:
            times = extract_opentable_times(page)
        
        return {"day": day_label, "slots": times}
    except PlaywrightTimeout:
        return {"day": day_label, "error": "Timeout loading page"}
    except Exception as e:
        return {"day": day_label, "error": str(e)[:100]}

def main():
    results = {}
    confirmed = 0
    
    with sync_playwright() as p:
        # Launch with anti-detection
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/Phoenix',
        )
        
        # Remove webdriver flag
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => false});
        """)
        
        page = context.new_page()
        
        print("=" * 70)
        print("SMART AVAILABILITY CHECKER")
        print("=" * 70)
        
        # Check Resy first (usually more permissive)
        resy_restaurants = {k: v for k, v in RESTAURANTS.items() if v["platform"] == "resy"}
        
        print("\n📋 Checking RESY restaurants...")
        for name, info in resy_restaurants.items():
            if confirmed >= 5:
                break
            
            print(f"\n{name}:")
            results[name] = []
            has_avail = False
            
            for date in DATES:
                if confirmed >= 5:
                    break
                
                result = check_restaurant(page, name, info, date)
                results[name].append(result)
                
                if result.get("slots"):
                    print(f"  ✅ {result['day']}: {', '.join(result['slots'][:5])}")
                    has_avail = True
                elif result.get("error"):
                    print(f"  ❌ {result['day']}: {result['error']}")
                else:
                    print(f"  ❓ {result['day']}: No slots found")
            
            if has_avail:
                confirmed += 1
                print(f"  🎉 CONFIRMED #{confirmed}/5")
        
        # Check OpenTable if needed
        if confirmed < 5:
            ot_restaurants = {k: v for k, v in RESTAURANTS.items() if v["platform"] == "opentable"}
            
            print("\n📋 Checking OPENTABLE restaurants...")
            for name, info in ot_restaurants.items():
                if confirmed >= 5:
                    break
                
                print(f"\n{name}:")
                results[name] = []
                has_avail = False
                
                for date in DATES:
                    if confirmed >= 5:
                        break
                    
                    result = check_restaurant(page, name, info, date)
                    results[name].append(result)
                    
                    if result.get("slots"):
                        print(f"  ✅ {result['day']}: {', '.join(result['slots'][:5])}")
                        has_avail = True
                    elif result.get("error"):
                        print(f"  ❌ {result['day']}: {result['error']}")
                    else:
                        print(f"  ❓ {result['day']}: No slots found")
                
                if has_avail:
                    confirmed += 1
                    print(f"  🎉 CONFIRMED #{confirmed}/5")
        
        browser.close()
    
    print("\n" + "=" * 70)
    print(f"FINAL RESULTS: {confirmed}/5 restaurants with availability")
    print("=" * 70)
    
    # Save results
    with open('availability_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    return results, confirmed

if __name__ == "__main__":
    main()
