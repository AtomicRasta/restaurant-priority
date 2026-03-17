#!/usr/bin/env python3
"""Deep inspection - check ALL elements for times."""
import os
from playwright.sync_api import sync_playwright
import re

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
URL = "https://www.opentable.com/r/bourbon-and-bones-scottsdale?dateTime=2026-03-14T18:30&covers=2"

print(f"Deep inspection: Bourbon & Bones - Friday 3/14/2026\n")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=AUTOMATION_PROFILE,
        headless=False,
        channel="chrome",
        viewport={'width': 1400, 'height': 1000}
    )
    
    page = browser.new_page()
    print("Loading...")
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    
    print("Waiting 12 seconds for full load...")
    page.wait_for_timeout(12000)
    
    # Take screenshot
    page.screenshot(path='restaurants/bourbon-screenshot.png')
    print("Screenshot saved: restaurants/bourbon-screenshot.png\n")
    
    print("="*60)
    print("SEARCHING ALL ELEMENTS FOR TIME PATTERNS")
    print("="*60 + "\n")
    
    # Search for time pattern in ALL elements
    time_pattern = r'\d{1,2}:\d{2}\s*[AP]M'
    
    found = page.evaluate(f"""() => {{
        const pattern = /{time_pattern}/i;
        const results = [];
        
        // Check all elements
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {{
            const text = el.textContent.trim();
            if (pattern.test(text) && text.length < 50) {{
                results.push({{
                    tag: el.tagName.toLowerCase(),
                    text: text,
                    className: el.className,
                    id: el.id,
                    innerHTML: el.innerHTML.substring(0, 200)
                }});
            }}
        }});
        
        return results;
    }}""")
    
    print(f"Found {len(found)} elements with time patterns:\n")
    
    for i, elem in enumerate(found[:20]):  # Show first 20
        print(f"{i+1}. <{elem['tag']}> '{elem['text']}'")
        if elem['className']:
            print(f"   class='{elem['className']}'")
        if elem['id']:
            print(f"   id='{elem['id']}'")
        print()
    
    # Try specific OpenTable selectors
    print("\n" + "="*60)
    print("TRYING SPECIFIC OPENTABLE SELECTORS:")
    print("="*60 + "\n")
    
    selectors_to_try = [
        "button[data-test='availability-slot']",
        "[class*='time']",
        "[class*='slot']",
        "[class*='availability']",
        "a[href*='datetime']",
        "[data-time]",
        ".dtp-picker-time",
        "[role='button']"
    ]
    
    for selector in selectors_to_try:
        try:
            elements = page.query_selector_all(selector)
            if elements:
                print(f"✓ '{selector}' found {len(elements)} elements")
                # Show first match
                if len(elements) > 0:
                    text = elements[0].text_content()[:100]
                    print(f"  First: '{text}'")
        except:
            print(f"✗ '{selector}' - error")
    
    print("\n\nBrowser open - visually confirm times are visible")
    print("Press Enter to close...")
    input()
    browser.close()
