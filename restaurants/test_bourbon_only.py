#!/usr/bin/env python3
"""Test ONLY Bourbon & Bones for Friday 3/14."""
import os
from playwright.sync_api import sync_playwright

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
URL = "https://www.opentable.com/r/bourbon-and-bones-scottsdale?dateTime=2026-03-14T18:30&covers=2"

print("Testing: Bourbon & Bones")
print("Date: Friday 3/14/2026")
print(f"URL: {URL}\n")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=AUTOMATION_PROFILE,
        headless=False,
        channel="chrome",
        viewport={'width': 1400, 'height': 1000}
    )
    
    page = browser.new_page()
    print("Loading page...")
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    
    print("Waiting 10 seconds for times to load...")
    page.wait_for_timeout(10000)
    
    print("\nExtracting times from ALL elements...\n")
    
    times = page.evaluate("""() => {
        const times = new Set();
        const timePattern = /\\b(\\d{1,2}:\\d{2}\\s*[AP]M)\\b/i;
        
        // Check all elements
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
            const text = el.textContent.trim();
            // Only short text (not paragraphs)
            if (text.length < 50) {
                const match = text.match(timePattern);
                if (match) {
                    // Skip dropdown options
                    if (el.tagName.toLowerCase() !== 'option' && 
                        el.tagName.toLowerCase() !== 'select') {
                        times.add(match[1]);
                    }
                }
            }
        });
        
        return Array.from(times).sort();
    }""")
    
    print("="*60)
    print(f"FOUND {len(times)} TIME SLOTS:")
    print("="*60)
    for t in times:
        print(f"  • {t}")
    
    # Filter to 5-9pm
    dinner = []
    for t in times:
        hour = int(t.split(':')[0])
        if 'PM' in t.upper():
            if hour >= 5 and hour <= 9:
                dinner.append(t)
    
    print(f"\n" + "="*60)
    print(f"DINNER TIMES (5-9 PM): {len(dinner)}")
    print("="*60)
    for t in dinner:
        print(f"  ✅ {t}")
    
    print("\n" + "="*60)
    if len(dinner) >= 3:
        print("✅ SUCCESS! Found availability (6:30, 7:00, 7:30 PM)")
    else:
        print("❌ FAILED! Should have found 6:30, 7:00, 7:30 PM")
    print("="*60)
    
    print("\nPress Enter to close...")
    input()
    browser.close()
