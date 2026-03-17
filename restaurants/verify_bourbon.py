#!/usr/bin/env python3
"""Verify Bourbon & Bones with the exact automated check code."""
import os
from playwright.sync_api import sync_playwright

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")

def extract_times(page):
    """Same extraction as automated check."""
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
        
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def check_restaurant(page, url, date):
    """Check one restaurant - OpenTable."""
    full_url = f"{url}?dateTime={date}T18:30&covers=2"
    try:
        page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
        return extract_times(page)
    except Exception as e:
        print(f"ERROR loading page: {e}")
        return []

print("Testing: Bourbon & Bones")
print("Using: NON-headless mode (visible browser)")
print("="*60 + "\n")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=AUTOMATION_PROFILE,
        headless=False,  # NOT headless
        channel="chrome",
        viewport={'width': 1400, 'height': 1000}
    )
    
    page = browser.new_page()
    
    print("Checking Friday 3/14...")
    friday = check_restaurant(page, "https://www.opentable.com/r/bourbon-and-bones-scottsdale", "2026-03-14")
    
    print(f"\n{'='*60}")
    print("FRIDAY 3/14 RESULTS:")
    print(f"{'='*60}")
    if friday:
        print(f"✅ Found {len(friday)} times:")
        for t in friday:
            print(f"   • {t}")
    else:
        print("❌ NO TIMES FOUND")
    
    import time
    time.sleep(2)
    
    print(f"\n{'='*60}")
    print("Checking Saturday 3/15...")
    saturday = check_restaurant(page, "https://www.opentable.com/r/bourbon-and-bones-scottsdale", "2026-03-15")
    
    print(f"\n{'='*60}")
    print("SATURDAY 3/15 RESULTS:")
    print(f"{'='*60}")
    if saturday:
        print(f"✅ Found {len(saturday)} times:")
        for t in saturday:
            print(f"   • {t}")
    else:
        print("❌ NO TIMES FOUND")
    
    print(f"\n{'='*60}")
    if friday or saturday:
        print("✅ SUCCESS - Automated check is working!")
    else:
        print("❌ FAILED - Still not finding availability")
    print(f"{'='*60}")
    
    browser.close()
