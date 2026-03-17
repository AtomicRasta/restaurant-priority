#!/usr/bin/env python3
"""Book 40 Love for Friday 3/14 at 7:15 PM."""
import os
from playwright.sync_api import sync_playwright

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
URL = "https://www.opentable.com/r/40-love-scottsdale?dateTime=2026-03-14T19:15&covers=2"

print("Booking: 40 Love")
print("Date: Friday 3/14/2026 at 7:15 PM")
print("Party size: 2")
print(f"URL: {URL}\n")

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        user_data_dir=AUTOMATION_PROFILE,
        headless=False,  # Visible so you can see it
        channel="chrome",
        viewport={'width': 1400, 'height': 1000}
    )
    
    page = browser.new_page()
    
    print("Step 1: Loading page...")
    page.goto(URL, wait_until="domcontentloaded", timeout=20000)
    page.wait_for_timeout(5000)
    
    print("Step 2: Looking for 7:15 PM time slot...")
    
    # Look for button/element with 7:15 PM
    time_slot = page.get_by_text("7:15 PM", exact=False).first
    
    if time_slot:
        print("Step 3: Clicking 7:15 PM time slot...")
        time_slot.click()
        page.wait_for_timeout(3000)
        
        print("Step 4: Looking for reservation button...")
        # Look for "Reserve" or "Complete reservation" button
        try:
            reserve_button = page.get_by_role("button", name="Reserve").first
            if reserve_button:
                print("Step 5: Clicking Reserve button...")
                reserve_button.click()
                page.wait_for_timeout(5000)
                
                print("\n✅ Reservation process initiated!")
                print("Check the browser window to complete any final steps.")
            else:
                print("⚠️  Could not find Reserve button - check browser window")
        except:
            print("⚠️  Reservation flow may need manual completion - check browser")
    else:
        print("❌ Could not find 7:15 PM time slot")
    
    print("\nBrowser will stay open - press Enter when done...")
    input()
    browser.close()
