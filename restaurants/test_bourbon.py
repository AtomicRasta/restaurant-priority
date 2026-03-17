#!/usr/bin/env python3
"""Test Bourbon & Bones on OpenTable - Friday 3/14/2026."""
import os
from playwright.sync_api import sync_playwright

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")

# Bourbon & Bones on OpenTable for Friday 3/14
URL = "https://www.opentable.com/r/bourbon-and-bones-scottsdale?dateTime=2026-03-14T18:30&covers=2"

print(f"Testing: Bourbon & Bones")
print(f"Date: Friday 3/14/2026")
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
    
    print("Waiting 10 seconds for times to load...\n")
    page.wait_for_timeout(10000)
    
    print("="*60)
    print("ALL BUTTONS ON PAGE:")
    print("="*60 + "\n")
    
    buttons = page.query_selector_all('button')
    print(f"Total buttons: {len(buttons)}\n")
    
    time_buttons = []
    for i, btn in enumerate(buttons):
        text = btn.text_content().strip()
        
        # Look for anything that might be a time
        if ':' in text and ('PM' in text or 'AM' in text):
            classes = btn.get_attribute('class') or ''
            aria_label = btn.get_attribute('aria-label') or ''
            
            print(f"Button #{i+1}:")
            print(f"  Text: '{text}'")
            print(f"  Class: '{classes}'")
            print(f"  Aria-label: '{aria_label}'")
            print()
            
            time_buttons.append(text)
    
    print("="*60)
    print(f"FOUND {len(time_buttons)} TIME SLOTS:")
    print("="*60)
    for t in time_buttons:
        print(f"  • {t}")
    
    print("\n\nBrowser will stay open - check if times are visible on screen.")
    print("Press Enter to close...")
    input()
    browser.close()
