#!/usr/bin/env python3
import urllib.request, ssl, re, json

ctx = ssl.create_default_context()
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"

slugs = {
    "40 Love": "40-love-scottsdale",
    "Bourbon and Bones": "bourbon-and-bones-scottsdale", 
    "Society Swan": "society-swan-reservations-scottsdale",
    "Cleaverman": "cleaverman-scottsdale",
    "Hainoo": "hai-noon-reservations-scottsdale",
    "FLINT by Baltaire": "flint-by-baltaire-scottsdale",
    "Chico Malo": "chico-malo-phoenix",
    "Maple and Ash": "maple-and-ash-scottsdale",
    "Nobu": "nobu-scottsdale",
    "Catch": "catch-scottsdale",
    "Mowry and Cotton": "mowry-and-cotton-scottsdale",
}

dates = ["2026-03-13", "2026-03-14"]
results = {}

for name, slug in slugs.items():
    results[name] = {}
    for date in dates:
        day = "Fri" if "13" in date else "Sat"
        url = "https://www.opentable.com/r/" + slug + "?dateTime=" + date + "T19:00&covers=2"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            html = urllib.request.urlopen(req, timeout=20, context=ctx).read().decode(errors="replace")
            
            # Check if page is valid (not 404)
            if "Page not found" in html or len(html) < 3000:
                results[name][day] = "NOT_ON_OT"
                continue
            
            # Extract all PM times from the page
            times = re.findall(r"(\d{1,2}:\d{2}\s*PM)", html)
            unique = list(dict.fromkeys(times))
            
            # Filter to 6:30-7:30 window
            target = [t for t in unique if any(x in t for x in ["6:30","6:45","7:00","7:15","7:30"])]
            
            if target:
                results[name][day] = "AVAILABLE: " + ", ".join(target)
            elif unique:
                results[name][day] = "TIMES_OUTSIDE_WINDOW: " + ", ".join(unique[:8])
            else:
                results[name][day] = "NO_TIMES_EXTRACTED"
        except Exception as e:
            results[name][day] = "ERROR: " + str(e)

# Output results
print(json.dumps(results, indent=2))
