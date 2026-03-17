#!/usr/bin/env python3
"""Test different OpenTable API endpoints."""
import urllib.request
import json

RID = 1354504  # 40 Love
DATE = "2026-03-14"
PARTY = 2

endpoints = [
    f"https://www.opentable.com/dapi/availability/timeslots?restaurantId={RID}&dateTime={DATE}T18:30:00&partySize={PARTY}",
    f"https://www.opentable.com/dapi/fe/gql?optype=query",
    f"https://www.opentable.com/dapi/availability?restaurantId={RID}&dateTime={DATE}T18:30:00&partySize={PARTY}",
    f"https://www.opentable.com/api/availability?rid={RID}&datetime={DATE}T18:30&covers={PARTY}",
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'application/json',
}

for i, url in enumerate(endpoints, 1):
    print(f"\n{i}. Testing: {url[:80]}...")
    try:
        req = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(req, timeout=10)
        print(f"   ✅ Status {response.status}")
        data = response.read()[:500]
        print(f"   Response preview: {data.decode('utf-8', errors='ignore')[:200]}")
    except urllib.error.HTTPError as e:
        print(f"   ❌ HTTP {e.code}: {e.reason}")
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:100]}")
