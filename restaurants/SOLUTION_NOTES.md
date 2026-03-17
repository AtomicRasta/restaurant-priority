# Restaurant Availability Checking - Solution Notes

## Problem
Need reliable, automated way to check availability across multiple reservation platforms (OpenTable, Resy, Tock, etc.) for regular workflow.

## Challenges Discovered

### OpenTable
- Direct API endpoints return 404/503
- HTTP2 protocol errors with Playwright
- Actively blocks automated requests
- Widget/iframe embeds might be more accessible

### Resy
- Playwright worked for Kid Sister
- Direct API calls need investigation
- May have public API with proper auth

### Solutions to Try

1. **Browser Automation (Playwright/Selenium)**
   - Use residential proxy rotation
   - Add random delays/human-like behavior
   - Maintain session cookies
   - Rotate user agents

2. **Official APIs/SDKs**
   - Research if platforms offer partner APIs
   - Check for unofficial but stable APIs
   - Look for restaurant-side booking widgets

3. **Hybrid Approach**
   - Parse restaurant websites for booking platform
   - Use platform-specific checkers
   - Fall back to manual check list

4. **Third-Party Services**
   - Consider services like Resy Bot, etc.
   - May have better infrastructure for this

## Next Steps
1. Get Playwright working with better anti-detection
2. Research Resy API documentation
3. Build fallback manual check interface
4. Consider proxy service for production use
