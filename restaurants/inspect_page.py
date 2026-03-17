#!/usr/bin/env python3
"""Inspect what's actually on the Resy page."""
import os
from playwright.sync_api import sync_playwright

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
URL = "https://resy.com/cities/phoenix-az/venues/kid-sister?date=2026-03-21&seats=2"

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=AUTOMATION_PROFILE,
        headless=False,
        channel="chrome",
        viewport={'width': 1400, 'height': 1000}
    )
    
    page = browser.new_page()
    print(f"Loading: {URL}")
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    
    print("\nWaiting 10 seconds for page to fully load...")
    page.wait_for_timeout(10000)
    
    print("\n" + "="*60)
    print("BUTTONS ON PAGE:")
    print("="*60)
    
    buttons = page.query_selector_all('button')
    print(f"\nTotal buttons found: {len(buttons)}")
    
    print("\nButton text (showing all buttons):")
    for i, btn in enumerate(buttons):
        text = btn.text_content().strip()
        classes = btn.get_attribute('class') or ''
        test_id = btn.get_attribute('data-test-id') or ''
        
        # Only show buttons that might be time slots
        if any(char.isdigit() for char in text) or 'book' in classes.lower() or 'book' in test_id.lower():
            print(f"{i+1}. TEXT: '{text}'")
            print(f"   CLASS: '{classes}'")
            print(f"   TEST-ID: '{test_id}'")
            print()
    
    print("\n" + "="*60)
    print("Press Enter in terminal to close...")
    input()
    browser.close()
