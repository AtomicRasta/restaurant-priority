#!/usr/bin/env python3
"""Debug why Bourbon & Bones shows no availability in automated check."""
import os
from playwright.sync_api import sync_playwright

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")

def extract_times(page):
    """Same extraction as check script."""
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
        
        print(f"  Raw times extracted: {times}")
        
        # Filter to 5-9pm
        dinner_times = []
        for t in times:
            hour = int(t.split(':')[0])
            if 'PM' in t.upper():
                if hour >= 5 and hour <= 9:
                    dinner_times.append(t)
        
        print(f"  Filtered to 5-9pm: {dinner_times}")
        return sorted(set(dinner_times))
        
    except Exception as e:
        print(f"  ERROR: {e}")
        return []

# Test both headless and visible
for headless_mode in [True, False]:
    print(f"\n{'='*60}")
    print(f"Testing Bourbon & Bones - Headless={headless_mode}")
    print(f"{'='*60}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=AUTOMATION_PROFILE,
            headless=headless_mode,
            channel="chrome",
            viewport={'width': 1400, 'height': 1000}
        )
        
        page = browser.new_page()
        url = "https://www.opentable.com/r/bourbon-and-bones-scottsdale?dateTime=2026-03-14T18:30&covers=2"
        
        print(f"Loading: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=20000)
        
        times = extract_times(page)
        
        print(f"\n✅ RESULT: {len(times)} times found")
        if times:
            for t in times:
                print(f"    • {t}")
        else:
            print("    ❌ NO TIMES")
        
        browser.close()
        
        if not headless_mode:
            break  # Only need to test visible once

print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)
