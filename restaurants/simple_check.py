#!/usr/bin/env python3
import urllib.request
import json
import time

def check_ot(rid, date):
    url = f"https://www.opentable.com/dapi/availability/timeslots?restaurantId={rid}&dateTime={date}T18:30:00&partySize=2"
    headers = {'User-Agent': 'Mozilla/5.0', 'Accept': 'application/json'}
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        data = json.loads(response.read())
        slots = []
        if 'availabilities' in data:
            for a in data['availabilities']:
                if 'dateTime' in a:
                    t = a['dateTime']
                    if '18:' in t or '19:' in t:
                        slots.append(t)
        return slots
    except Exception as e:
        return str(e)[:100]

# Test 40 Love
print("40 Love - Friday 3/14:")
result = check_ot(1354504, "2026-03-14")
print(result)
time.sleep(2)

print("\n40 Love - Saturday 3/15:")
result = check_ot(1354504, "2026-03-15")
print(result)
