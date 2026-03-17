#!/usr/bin/env python3
"""Get specific times for 40 Love and Bourbon & Bones."""
import os
from playwright.sync_api import sync_playwright
import time

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")

RESTAURANTS = [
    ("40 Love", "opentable", "https://www.opentable.com/r/40-love-scottsdale"),
    ("Bourbon & Bones", "opentable", "https://www.opentable.com/r/bourbon-and-bones-scottsdale")
]

def extract_times(page):
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
        
        dinner_times = []
        for t in times:
            hour = int(t.split(':')[0])
            if 'PM' in t.upper() and hour >= 5 and hour <= 9:
                dinner_times.append(t)
        return sorted(set(dinner_times))
    except:
        return []

def check(page, url, date):
    full_url = f"{url}?dateTime={date}T18:30&covers=2"
    try:
        page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
        return extract_times(page)
    except:
        return []

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=AUTOMATION_PROFILE,
        headless=False,
        channel="chrome",
        viewport={'width': 1400, 'height': 1000}
    )
    
    page = browser.new_page()
    
    for name, platform, url in RESTAURANTS:
        print(f"\n{'='*60}")
        print(f"{name}")
        print(f"{'='*60}")
        print(f"{url}")
        
        fri = check(page, url, "2026-03-14")
        time.sleep(2)
        sat = check(page, url, "2026-03-15")
        time.sleep(2)
        
        if fri:
            print(f"\n✅ Friday 3/14: {', '.join(fri)}")
        else:
            print(f"\n❌ Friday 3/14: No availability")
            
        if sat:
            print(f"✅ Saturday 3/15: {', '.join(sat)}")
        else:
            print(f"❌ Saturday 3/15: No availability")
    
    browser.close()
    
print(f"\n{'='*60}")
print("COMPLETE")
print(f"{'='*60}")
