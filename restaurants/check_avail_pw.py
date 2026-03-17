#!/usr/bin/env python3
"""Check restaurant availability using Playwright headless browser."""
import json
import sys
from playwright.sync_api import sync_playwright

PARTY_SIZE = 2
DATES = ["2026-03-14", "2026-03-15"]
DAY_NAMES = {"2026-03-14": "Fri", "2026-03-15": "Sat"}

# OpenTable restaurants with slugs and IDs
OT_RESTAURANTS = {
    "40 Love": {"slug": "40-love-scottsdale", "rid": 1354504},
    "FLINT by Baltaire": {"slug": "flint-by-baltaire-scottsdale", "rid": 1045138},
    "Bourbon & Bones": {"slug": "bourbon-and-bones-scottsdale", "rid": 1075225},
    "Society Swan": {"slug": "society-swan-reservations-scottsdale", "rid": 1460734},
    "Cleaverman": {"slug": "cleaverman-scottsdale", "rid": 1392139},
    "Hainoo": {"slug": "hai-noon-reservations-scottsdale", "rid": 1293022},
    "Chico Malo": {"slug": "chico-malo-phoenix", "rid": None},
    "Maple & Ash": {"slug": "maple-and-ash-scottsdale", "rid": None},
    "Nobu": {"slug": "nobu-scottsdale", "rid": None},
    "Catch": {"slug": "catch-scottsdale", "rid": None},
    "Mowry and Cotton": {"slug": "mowry-and-cotton-scottsdale", "rid": None},
}

# Resy restaurants
RESY_RESTAURANTS = {
    "Kid Sister": "kid-sister",
    "Maple & Ash": "maple-and-ash-scottsdale",
    "Nobu": "nobu-scottsdale",  
    "Catch": "catch-scottsdale",
    "Jing": "jing-scottsdale",
    "Sexy Roman": "the-sexy-roman-scottsdale",
    "Shiv Supper Club": "shiv-supper-club",
}

def extract_ot_slots(page, url, restaurant_name, date):
    """Navigate to OpenTable and extract available time slots."""
    day = DAY_NAMES[date]
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)  # Extra wait for dynamic content
        
        # Try to find time slot buttons
        slots = page.evaluate("""() => {
            // Try multiple selectors for time slots
            var selectors = [
                '[data-test="time-slot"]',
                'button[data-test*="timeslot"]', 
                '[class*="TimeSlot"] button',
                '[class*="timeslot"] button',
                'button[class*="slot"]',
                '[data-test="availabilityButton"]',
            ];
            var times = [];
            for (var sel of selectors) {
                var els = document.querySelectorAll(sel);
                els.forEach(function(el) {
                    var t = el.textContent.trim();
                    if (t.match(/\\d{1,2}:\\d{2}\\s*PM/i)) {
                        times.push(t.match(/\\d{1,2}:\\d{2}\\s*PM/i)[0]);
                    }
                });
                if (times.length > 0) break;
            }
            
            // Fallback: find all buttons with PM times
            if (times.length === 0) {
                document.querySelectorAll('button').forEach(function(b) {
                    var t = b.textContent.trim();
                    var m = t.match(/^(\\d{1,2}:\\d{2}\\s*PM)$/i);
                    if (m) times.push(m[1]);
                });
            }
            
            return times;
        }""")
        
        # Filter to 6:30-7:30 window
        target = []
        for t in slots:
            if any(x in t for x in ["6:30", "6:45", "7:00", "7:15", "7:30"]):
                target.append(t)
        
        return {"day": day, "all_slots": slots, "target_slots": target}
    except Exception as e:
        return {"day": day, "error": str(e)}

def extract_resy_slots(page, slug, date):
    """Check Resy for availability."""
    day = DAY_NAMES[date]
    url = f"https://resy.com/cities/phoenix-az/venues/{slug}?date={date}&seats={PARTY_SIZE}"
    try:
        page.goto(url, wait_until="networkidle", timeout=20000)
        page.wait_for_timeout(3000)
        
        slots = page.evaluate("""() => {
            var times = [];
            // Resy time slot buttons
            var buttons = document.querySelectorAll('[class*="ReservationButton"], [class*="TimeSlot"], button[class*="time"]');
            buttons.forEach(function(b) {
                var t = b.textContent.trim();
                if (t.match(/\\d{1,2}:\\d{2}\\s*(PM|AM)/i)) {
                    times.push(t.match(/\\d{1,2}:\\d{2}\\s*(PM|AM)/i)[0]);
                }
            });
            
            // Fallback
            if (times.length === 0) {
                document.querySelectorAll('button').forEach(function(b) {
                    var t = b.textContent.trim();
                    if (t.match(/^\\d{1,2}:\\d{2}\\s*PM$/i)) times.push(t);
                });
            }
            
            return times;
        }""")
        
        target = [t for t in slots if any(x in t for x in ["6:30", "6:45", "7:00", "7:15", "7:30"])]
        return {"day": day, "all_slots": slots, "target_slots": target}
    except Exception as e:
        return {"day": day, "error": str(e)}

results = {}
confirmed = 0

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()
    
    # Check OpenTable restaurants first
    print("=== CHECKING OPENTABLE ===", flush=True)
    for name, info in OT_RESTAURANTS.items():
        if confirmed >= 5:
            break
        print(f"\nChecking {name}...", flush=True)
        results[name] = []
        has_avail = False
        
        for date in DATES:
            if confirmed >= 5:
                break
            url = f"https://www.opentable.com/r/{info['slug']}?dateTime={date}T19:00&covers={PARTY_SIZE}"
            result = extract_ot_slots(page, url, name, date)
            results[name].append(result)
            
            if result.get("target_slots"):
                print(f"  ✅ {result['day']}: {', '.join(result['target_slots'])}", flush=True)
                has_avail = True
            elif result.get("all_slots"):
                print(f"  ⏰ {result['day']}: Slots found but none in 6:30-7:30: {result['all_slots'][:5]}", flush=True)
            elif result.get("error"):
                print(f"  ❌ {result['day']}: {result['error'][:100]}", flush=True)
            else:
                print(f"  ❓ {result['day']}: No slots found on page", flush=True)
        
        if has_avail:
            confirmed += 1
            print(f"  🎉 CONFIRMED #{confirmed}", flush=True)
    
    # Check Resy restaurants
    if confirmed < 5:
        print("\n=== CHECKING RESY ===", flush=True)
        for name, slug in RESY_RESTAURANTS.items():
            if confirmed >= 5:
                break
            if name in results:  # Skip if already found on OT
                continue
            print(f"\nChecking {name}...", flush=True)
            results[name] = []
            has_avail = False
            
            for date in DATES:
                if confirmed >= 5:
                    break
                result = extract_resy_slots(page, slug, date)
                results[name].append(result)
                
                if result.get("target_slots"):
                    print(f"  ✅ {result['day']}: {', '.join(result['target_slots'])}", flush=True)
                    has_avail = True
                elif result.get("all_slots"):
                    print(f"  ⏰ {result['day']}: Slots found but none in 6:30-7:30: {result['all_slots'][:5]}", flush=True)
                elif result.get("error"):
                    print(f"  ❌ {result['day']}: {result['error'][:100]}", flush=True)
                else:
                    print(f"  ❓ {result['day']}: No slots found on page", flush=True)
            
            if has_avail:
                confirmed += 1
                print(f"  🎉 CONFIRMED #{confirmed}", flush=True)
    
    browser.close()

print(f"\n=== SUMMARY: {confirmed} restaurants with confirmed availability ===", flush=True)
print(json.dumps(results, indent=2))
