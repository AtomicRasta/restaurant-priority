#!/usr/bin/env python3
"""Debug version with screenshots and detailed logging."""
import json
import time
from playwright.sync_api import sync_playwright
import os
from pathlib import Path

AUTOMATION_PROFILE = os.path.expanduser("~/.openclaw/chrome-automation")
DATE = "2026-03-21"
PARTY_SIZE = 2

def check_one_restaurant():
    """Check a single known-good restaurant with detailed logging."""
    
    # Kid Sister - should definitely have SOME availability
    name = "Kid Sister"
    platform = "resy"
    url = "https://resy.com/cities/phoenix-az/venues/kid-sister"
    
    print(f"\n🔍 Debugging: {name}")
    print(f"URL: {url}?date={DATE}&seats={PARTY_SIZE}")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=AUTOMATION_PROFILE,
                headless=False,  # Show browser so we can see what's happening
                channel="chrome",
                viewport={'width': 1400, 'height': 1000}
            )
            
            page = browser.new_page()
            
            # Navigate
            full_url = f"{url}?date={DATE}&seats={PARTY_SIZE}"
            print(f"\n📍 Navigating...")
            page.goto(full_url, wait_until="domcontentloaded", timeout=20000)
            
            # Wait for content
            print("⏳ Waiting 5 seconds for content to load...")
            page.wait_for_timeout(5000)
            
            # Take screenshot
            screenshot_path = Path(__file__).parent / "debug-screenshot.png"
            page.screenshot(path=str(screenshot_path))
            print(f"📸 Screenshot saved: {screenshot_path}")
            
            # Log page HTML
            html = page.content()
            html_path = Path(__file__).parent / "debug-page.html"
            with open(html_path, 'w') as f:
                f.write(html)
            print(f"📄 HTML saved: {html_path}")
            
            # Check for buttons
            print("\n🔍 Looking for button elements...")
            buttons = page.query_selector_all('button')
            print(f"Found {len(buttons)} button elements")
            
            # Sample button text
            print("\n📝 Sample button text (first 10):")
            for i, btn in enumerate(buttons[:10]):
                text = btn.text_content()
                print(f"  {i+1}. {repr(text)}")
            
            # Try our extraction logic
            print("\n🧪 Testing extraction logic...")
            times = page.evaluate("""() => {
                const times = new Set();
                const buttons = document.querySelectorAll('button');
                
                buttons.forEach(btn => {
                    const text = btn.textContent.trim();
                    const match = text.match(/(\\d{1,2}:\\d{2}\\s*[AP]M)/i);
                    if (match && text.length < 30) {
                        times.add(match[1]);
                    }
                });
                
                return Array.from(times).sort();
            }""")
            
            print(f"✅ Extracted times: {times}")
            
            # Filter to dinner
            dinner_times = [t for t in times if any(h in t for h in ["5:", "6:", "7:", "8:"])]
            print(f"🍽️  Dinner times (5-9pm): {dinner_times}")
            
            print("\nPress Enter to close browser...")
            input()
            
            browser.close()
            
            return dinner_times
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    result = check_one_restaurant()
    print(f"\n{'='*60}")
    print(f"RESULT: {len(result)} times found")
    if result:
        print(f"Times: {', '.join(result)}")
    print(f"{'='*60}")
