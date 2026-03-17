#!/usr/bin/env python3
"""Automated booking once restaurant and time are selected."""
import json
import sys
from playwright.sync_api import sync_playwright
import argparse

def book_resy(page, url, date, time, party_size=2):
    """Book a reservation on Resy."""
    # Navigate to restaurant page with date and party size
    booking_url = f"{url}?date={date}&seats={party_size}"
    print(f"Opening: {booking_url}")
    page.goto(booking_url, wait_until="networkidle")
    
    # Wait for time slots to load
    page.wait_for_selector('button', timeout=10000)
    
    # Find and click the desired time slot
    print(f"Looking for {time} time slot...")
    time_clicked = page.evaluate(f"""(time) => {{
        const buttons = Array.from(document.querySelectorAll('button'));
        for (const btn of buttons) {{
            if (btn.textContent.includes(time)) {{
                btn.click();
                return true;
            }}
        }}
        return false;
    }}""", time)
    
    if not time_clicked:
        print(f"❌ Could not find {time} slot")
        return False
    
    print(f"✅ Clicked {time} slot")
    
    # Wait for reservation details page
    page.wait_for_timeout(2000)
    
    # Check if login is required
    if "sign-in" in page.url.lower() or "login" in page.url.lower():
        print("\n⚠️  Login required!")
        print("Please log in to your Resy account in the browser...")
        input("Press Enter once logged in...")
    
    print("\n📋 Reservation details page loaded")
    print("Complete the booking in the browser window")
    print("Script will wait here...")
    
    input("\nPress Enter once booking is confirmed...")
    return True

def book_opentable(page, url, date, time, party_size=2):
    """Book a reservation on OpenTable."""
    # Navigate to restaurant page with date, time and party size
    booking_url = f"{url}?dateTime={date}T{time.replace(' ', '')}&covers={party_size}"
    print(f"Opening: {booking_url}")
    page.goto(booking_url, wait_until="networkidle")
    
    # Wait for time slots
    page.wait_for_selector('button', timeout=10000)
    
    # Find and click the time slot
    print(f"Looking for {time} time slot...")
    time_clicked = page.evaluate(f"""(time) => {{
        const buttons = Array.from(document.querySelectorAll('button'));
        for (const btn of buttons) {{
            if (btn.textContent.includes(time)) {{
                btn.click();
                return true;
            }}
        }}
        return false;
    }}""", time)
    
    if not time_clicked:
        print(f"❌ Could not find {time} slot")
        return False
    
    print(f"✅ Clicked {time} slot")
    
    # Wait for booking form
    page.wait_for_timeout(2000)
    
    # Check if login required
    if "sign" in page.url.lower() or "login" in page.url.lower():
        print("\n⚠️  Login required!")
        print("Please log in to your OpenTable account in the browser...")
        input("Press Enter once logged in...")
    
    print("\n📋 Reservation form loaded")
    print("Complete the booking in the browser window")
    
    input("\nPress Enter once booking is confirmed...")
    return True

def main():
    parser = argparse.ArgumentParser(description='Book a restaurant reservation')
    parser.add_argument('--restaurant', required=True, help='Restaurant name')
    parser.add_argument('--date', required=True, help='Date (YYYY-MM-DD)')
    parser.add_argument('--time', required=True, help='Time (e.g., "7:00 PM")')
    parser.add_argument('--party-size', type=int, default=2, help='Party size')
    
    args = parser.parse_args()
    
    # Load restaurant data
    try:
        with open('availability_found.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ No availability data found. Run the checker first.")
        return
    
    # Find restaurant
    restaurant = None
    for r in data.get('restaurants_with_availability', []):
        if r['name'].lower() == args.restaurant.lower():
            restaurant = r
            break
    
    if not restaurant:
        print(f"❌ Restaurant '{args.restaurant}' not found in availability data")
        print("Available restaurants:")
        for r in data.get('restaurants_with_availability', []):
            print(f"  - {r['name']}")
        return
    
    print("=" * 70)
    print("AUTOMATED RESTAURANT BOOKING")
    print("=" * 70)
    print(f"\n📍 Restaurant: {restaurant['name']}")
    print(f"📅 Date: {args.date}")
    print(f"🕐 Time: {args.time}")
    print(f"👥 Party size: {args.party_size}")
    print(f"🌐 Platform: {restaurant['platform']}")
    
    input("\nPress Enter to proceed with booking...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser for user interaction
        context = browser.new_context()
        page = context.new_page()
        
        if restaurant['platform'] == 'resy':
            success = book_resy(page, restaurant['url'], args.date, args.time, args.party_size)
        else:  # opentable
            success = book_opentable(page, restaurant['url'], args.date, args.time, args.party_size)
        
        if success:
            print("\n✅ Booking process completed!")
        else:
            print("\n❌ Booking failed")
        
        browser.close()

if __name__ == "__main__":
    main()
